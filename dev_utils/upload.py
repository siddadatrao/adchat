import pandas as pd

def get_embedding(text, openai_connection, model="text-embedding-3-small"):
	return openai_connection.embeddings.create(input = [text], model=model).data[0].embedding

def send_data_to_pinecone(data_string, openai_connection, pinecone, client_uuid):
	df = pd.DataFrame({'text': data_string})
	df['ada_embedding'] = df.text.apply(lambda x: get_embedding(x, openai_connection, model='text-embedding-3-small'))
	
	df['id'] = df.index.astype(str) # Add an ID column (for simplicity, using index as ID)

	# Convert DataFrame rows to the format required by upsert
	vectors = [
		{
			"id": row['id'],
			"values": row['ada_embedding'],
			"metadata": {"text": row['text']}
		} for index, row in df.iterrows()
	]
	
	# Assuming `index` is your Pinecone index object
	pinecone.Index("adchat").upsert(
		vectors=vectors,
		namespace=client_uuid
	)

def run_upload(doc_path, client_uuid, openai_connection, pinecone_connection):
	data = pd.read_csv(doc_path)
	data_strings = []
	for i, j in data.iterrows():
		data_strings.append(f"{j['Offer']}. {j['Description']} {j['Location']}. The promotion code is {j['Promotion Codes']}")
	data_string = ['\n\n'.join(data_strings)]
	send_data_to_pinecone(data_string, openai_connection, pinecone_connection, client_uuid)
	return "SUCCESS"