from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_KEY')
PINECONE_KEY = os.getenv('PINECONE_KEY')
