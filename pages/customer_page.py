import streamlit as st
import openai
from dev_utils.connections import api_connections, database

def get_embedding(text, open_ai_client, model="text-embedding-3-small"):
	return open_ai_client.embeddings.create(input = [text], model=model).data[0].embedding

def templatize(query, context):
	return "Answer the question based only on the following offers by picking one that is most applicable:" + context + "Question: " + query

def get_similar(namespace, query, open_ai_client, pinecone):
	query_embedding = get_embedding(query, open_ai_client, model='text-embedding-3-small')
	query_results1 = pinecone.Index("adchat").query(
		namespace=namespace,
		vector=query_embedding,
		top_k=1,
		include_values=False,
		include_metadata=True,
	)
	query_result = query_results1['matches'][0]['metadata']['text']
	return templatize(query, query_result)

def get_namespace():
	test_params = st.query_params
	if "namespace" not in test_params:
		return "ns1"
	else:
		return test_params["namespace"]

def get_completion(prompt, key):
	openai.api_key = key

	response = openai.chat.completions.create(
		model="gpt-4o-mini",
		messages=[
		{"role": "system", "content": "You are a sales agent trying to present information regarding a offers for a company after someone who clicked an ad."},
		{"role": "user", "content": prompt}
		],
		stream=True
	)
	return response

def main():
	openai_connection, pinecone_connection, openai_key, pinecone_key = api_connections()

	# openai_api_key = st.text_input("OpenAI API Key", type="password")
	# pinecone_key = st.text_input("pinecone API Key", type="password")

	if not openai_connection or not pinecone_connection:
		st.info("Please add valid OpenAI & Pinecode API keys to continue.", icon="🗝️")
	else:
		# Create a session state variable to store the chat messages. 
		# This ensures that the messages persist across reruns.
		if "messages" not in st.session_state:
			st.session_state.messages = []

		# Display the existing chat messages via 'st.chat_message'.
		for message in st.session_state.messages:
			with st.chat_message(message["role"]):
				st.markdown(message["content"])

		# Create a chat input field to allow the user to enter a message. 
		# This will display automatically at the bottom of the page.
		if query := st.chat_input("What is up?"):

			# Store and display the current prompt.
			st.session_state.messages.append({"role": "user", "content": query})
			with st.chat_message("user"):
				st.markdown(query)
				
			namespace = get_namespace()
			prompt = get_similar(namespace, query, openai_connection, pinecone_connection)
			stream = get_completion(prompt, openai_key)

			# # Generate a response using the OpenAI API.
			# stream = client.chat.completions.create(
			#     model="gpt-3.5-turbo",
			#     messages=[
			#         {"role": m["role"], "content": m["content"]}
			#         for m in st.session_state.messages
			#     ],
			#     stream=True,
			# )

			# Stream the response to the chat using `st.write_stream`, then store it in session state.
			with st.chat_message("assistant"):
				response = st.write_stream(stream)
			st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":

	st.title("AdChat Explore")
	st.write(
		"Ask this ad any questions you have!"
	)
	
	main()


# Notes:
# 1. Ask user for their OpenAI API key via `st.text_input`.
# 2. Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# 3. via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management 
