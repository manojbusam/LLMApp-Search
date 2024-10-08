"""
Vector Database Indexing Program

Author: Manoj Busam
Date: April 22, 2024

This program implements vector database indexing using the following tools:
- Amazon S3 for document storage
- TensorFlow for processing
- OpenAI's ChatGPT for generating embeddings(text-embedding-ada-002)
- Pinecone for vector storage and retrieval

The program includes functionalities for:
1. Downloading documents from S3.
2. Chunking documents using recursive chunking.
3. Generating embeddings for each chunk using OpenAI.
4. Indexing the embeddings in Pinecone for efficient retrieval.
5. Searching for similar content based on user queries.

"""
import boto3
import tensorflow as tf
import openai
import pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize S3 client
s3 = boto3.client('s3')

# Initialize OpenAI
openai.api_key = 'your-openai-api-key'

# Initialize Pinecone
pinecone.init(api_key='your-pinecone-api-key', environment='your-environment')
index = pinecone.Index('your-index-name')

def download_from_s3(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    return response['Body'].read().decode('utf-8')

def recursive_chunk(text, max_chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return text_splitter.split_text(text)

def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']

def index_document(bucket, key):
    # Download document from S3
    document = download_from_s3(bucket, key)
    
    # Chunk the document
    chunks = recursive_chunk(document)
    
    # Get embeddings for each chunk
    embeddings = [get_embedding(chunk) for chunk in chunks]
    
    # Index embeddings in Pinecone
    vectors = [(f"{key}_{i}", embedding, {"text": chunk}) 
               for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))]
    index.upsert(vectors=vectors)

 

# Example usage
if __name__ == "__main__":
    # Index a document
    index_document('your-bucket-name', 'your-document-key')
