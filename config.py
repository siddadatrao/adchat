from dotenv import load_dotenv
import streamlit as st
import os

# load_dotenv()
# OPENAI_KEY = os.getenv('OPEN_AI_API_KEY')
# PINECONE_KEY = os.getenv('PINECONE_API_KEY')

OPENAI_KEY = st.secrets["OPEN_AI_API_KEY"]
PINECONE_KEY = st.secrets["PINECONE_API_KEY"]
