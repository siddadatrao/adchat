from pinecone import Pinecone as PineconeClient
from openai import OpenAI
from contextlib import contextmanager
import psycopg2, psycopg2.extras
import config


def api_connections():
	openai_key = config.OPENAI_KEY
	pinecone_key = config.PINECONE_KEY
	openai_connection = OpenAI(api_key=openai_key)
	pinecone_connection = PineconeClient(api_key=pinecone_key)
	return openai_connection, pinecone_connection, openai_key, pinecone_key

@contextmanager
def database():
	connection = psycopg2.connect(
									host = config.DB_HOST, 
									port = config.DB_PORT, 
									user = config.DB_USER, 
									password = config.DB_PASSWORD
								)
	cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
	try:
		yield connection, cursor
	finally:
		cursor.close()
		connection.close()

