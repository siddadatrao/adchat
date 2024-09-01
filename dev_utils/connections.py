from pinecone import Pinecone as PineconeClient
from openai import OpenAI
import config


def connections():
	openai_key = config.OPENAI_KEY
	pinecone_key = config.PINECONE_KEY
	openai_connection = OpenAI(api_key=openai_key)
	pinecone_connection = PineconeClient(api_key=pinecone_key)
	return openai_connection, pinecone_connection, openai_key, pinecone_key