from dotenv import load_dotenv
import streamlit as st
import os

# load_dotenv()
# OPENAI_KEY = os.getenv('OPEN_AI_API_KEY')
# PINECONE_KEY = os.getenv('PINECONE_API_KEY')

OPENAI_KEY = st.secrets["OPEN_AI_API_KEY"]
PINECONE_KEY = st.secrets["PINECONE_API_KEY"]
DB_HOST = st.secrets["POSTGRES_DB_HOST"]
DB_PORT = st.secrets["POSTGRES_DB_PORT"]
DB_USER = st.secrets["POSTGRES_DB_USER"]
DB_PASSWORD = st.secrets["POSTGRES_DB_PASSWORD"]


# The secrets comes to this file from "secrets.toml".
