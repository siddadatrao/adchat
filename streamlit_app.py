import streamlit as st
import openai
from openai import OpenAI
from pinecone import Pinecone as PineconeClient
import requests

# Show title and description.
st.title("AdChat Explore")
st.write(
    "Ask this ad any questions you have!"
)

def connections(open_ai_key, pinecone_key):
    pinecone = PineconeClient(api_key=pinecone_key)
    open_ai_client = OpenAI(api_key=open_ai_key)
    return open_ai_client, pinecone

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


# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
pinecone_key = st.text_input("pinecone API Key", type="password")
if not openai_api_key or not pinecone_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    open_ai_client, pinecone = connections(openai_api_key, pinecone_key)
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if query := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        prompt = get_similar("ns1", query, open_ai_client, pinecone)
        stream = get_completion(prompt, openai_api_key)

        # # Generate a response using the OpenAI API.
        # stream = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[
        #         {"role": m["role"], "content": m["content"]}
        #         for m in st.session_state.messages
        #     ],
        #     stream=True,
        # )

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
