"""
chroma_utils.py

This module handles creation and saving of a FAISS vectorstore index
from a list of documents using HuggingFace sentence embeddings.

Used for semantic search and retrieval in LangChain-based RAG pipelines.
"""
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Load your docs (sample)
documents = [Document(page_content="your content here", metadata={"source": "xyz"})]

# Use the same embedding model you now query with
embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Create a new FAISS index
vectorstore = FAISS.from_documents(documents, embedding_function)

# Save the new index
vectorstore.save_local("vectorstore_sentry/")