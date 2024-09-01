from pinecone import Pinecone as PineconeClient
from openai import OpenAI


def connections(open_ai_key, pinecone_key):
    pinecone = PineconeClient(api_key=pinecone_key)
    open_ai_client = OpenAI(api_key=open_ai_key)
    return open_ai_client, pinecone