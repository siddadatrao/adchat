import streamlit as st
from datetime import datetime
from dev_utils.upload import run_upload
from dev_utils.connections import api_connections, database
import psycopg2, psycopg2.extras
import os, uuid


UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
	os.makedirs(UPLOAD_DIR)

def create_session_folder(base_upload_dir):
	"""Utility function to create a unique session folder"""
	session_id = datetime.now().strftime("%Y%m%d%H%M%S")
	session_folder = os.path.join(base_upload_dir, session_id)
	os.makedirs(session_folder, exist_ok=True)
	return session_folder

def save_uploaded_file(uploaded_file, folder):
	"""Utility function to save uploaded files"""
	try:
		file_path = os.path.join(folder, uploaded_file.name)
		with open(file_path, "wb") as f:
			f.write(uploaded_file.getbuffer())
		return file_path
	except Exception as e:
		st.error(f"Error saving file: {e}")
		return None

def handle_image_upload():
	"""Definition to handle image upload"""
	st.header("Ad Image")
	image_file = st.file_uploader("Upload an image...", type=["png", "jpg", "jpeg"])
	image_params = {}
	if image_file is not None:
		image_params['Offer'] = st.text_input("What is the offer for the provided creative?", value="")
		image_params['Promotion Code Type'] = st.selectbox(
			"Promotion Code Type",
			options=["Category Code", "Static Code"]
		)
		image_params['Tags'] = st.text_input("Tags (comma-separated)", value="")
	return image_file, image_params

def handle_document_upload():
	"""Definition to handle document upload"""
	st.header("Available Offers")
	doc_file = st.file_uploader("Upload a document...", type=["pdf", "docx", "txt", "csv"])
	return doc_file

def handle_client_parameters():
	"""Definition to handle Client Information"""
	st.header("Client Information")
	client_details = {}
	client_details['Client Name'] = st.text_input("Client Name", value="")
	client_details['Client Email'] = st.text_input("Client Email", value="")
	client_details['Client Phone'] = st.text_input("Client Phone", value="")
	client_details['Upload Date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	return client_details

def save_parameters(params, folder, filename="params.txt"):
	"""Utility function to save parameters to a file"""
	params_file = os.path.join(folder, filename)
	with open(params_file, "w") as f:
		for section, section_params in params.items():
			f.write(f"{section}:\n")
			for key, value in section_params.items():
				f.write(f"  {key}: {value}\n")
			f.write("\n")
	return params_file

def create_url(client_name):
	"""Utility function to create url along with the uid"""
	c_uuid = uuid.uuid4()
	client_uuid = str(client_name) + str(c_uuid)
	url_base = "http://localhost:8501/customer_page?namespace=" + client_uuid
	return client_uuid, url_base

def ad_chat_client_upload():

	st.title("AdChat Client Portal")

	image_file, image_params = handle_image_upload()
	doc_file = handle_document_upload()
	client_details = handle_client_parameters()

	if st.button("Submit"):
		openai_connection, pinecone_connection, openai_key, pinecone_key = api_connections()

		if image_file and doc_file and client_details['Client Name'] and client_details['Client Email']:

			session_folder = create_session_folder(UPLOAD_DIR)

			image_path = save_uploaded_file(image_file, session_folder)
			if image_path:
				st.success(f"Image '{image_file.name}' uploaded successfully!")

			doc_path = save_uploaded_file(doc_file, session_folder)

			# Get current URL and Client UUID to post data to pinecone
			client_uuid, url = create_url(client_details["Client Name"])
			run_upload(doc_path, client_uuid, openai_connection, pinecone_connection)
			st.success(f"Share This URL: '{url}")
			print(url)

			if doc_path:
				st.success(f"Document '{doc_file.name}' uploaded successfully!")

			params = {
				"Image Parameters": image_params,
				"Client Details": client_details,
				"Client_Customer_Link": {'Client_UUID': client_uuid, 'Client_URL': url}
			}
			save_parameters(params, session_folder)
			st.success("All files and parameters saved successfully!")

			if len(params) > 0:
				records = [(params['Client_Customer_Link']['Client_UUID'], 
							params['Client Details']['Client Name'], 
							params['Client Details']['Client Phone'], 
							params['Client Details']['Client Email'])]
				
				with database() as (connection, cursor):
					psycopg2.extras.execute_values(cursor, """
						INSERT INTO client_info
							(uuid, client_name, client_phone, client_email)
						VALUES %s
						ON CONFLICT ON CONSTRAINT unq_constraint_uuid_client_name
						DO UPDATE
						SET 
							client_phone = EXCLUDED.client_phone,
							client_email = EXCLUDED.client_email
						""", records
					)
					connection.commit()
		else:
			st.error("Please upload both an image and a document, and fill in all client details.")

def analytics_page():
	st.title("Analytics")
	st.write("This is where you can display analytics about the ad campaigns.")

def client_feedback_page():
	st.title("Client Feedback")
	st.write("This is where you can gather and display client feedback.")

def main():
	st.sidebar.title("Navigation")
	page = st.sidebar.radio("Go to", ["AdChat Client Upload", "Analytics", "Client Feedback"])

	if page == "AdChat Client Upload":
		ad_chat_client_upload()
	elif page == "Analytics":
		analytics_page()
	elif page == "Client Feedback":
		client_feedback_page()

if __name__ == "__main__":
	main()
