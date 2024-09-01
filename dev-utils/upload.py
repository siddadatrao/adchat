import os
from pinecone import Pinecone as PineconeClient
import requests
# new
from openai import OpenAI
import pandas as pd
import numpy as np
import random


def get_embedding(text, open_ai_client, model="text-embedding-3-small"):
    return open_ai_client.embeddings.create(input = [text], model=model).data[0].embedding


def send_data_to_pinecone(data, open_ai_client, pinecone, namespace):
    # Create a DataFrame
    df = pd.DataFrame({'text': data})
    df['ada_embedding'] = df.text.apply(lambda x: get_embedding(x, open_ai_client, model='text-embedding-3-small'))
    # Add an ID column (for simplicity, using index as ID)
    df['id'] = df.index.astype(str)

    
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
        namespace=namespace
    )

    def run_upload(offers, namespace, open_ai_client, pinecone):
        data = pd.read_csv(offers)
        data_strings = []
        for i, j in data.iterrows():
            data_strings.append(f"{j['Offer']}. {j['Description']} {j['Location']}. The promotion code is {j['Promotion Codes']}")
        data_string = ['\n\n'.join(data_strings)]
        send_data_to_pinecone(data_string, open_ai_client, pinecone, namespace)