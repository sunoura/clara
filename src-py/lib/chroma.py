import chromadb
from datetime import datetime
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional, Union

chroma_client = chromadb.Client()
# chroma_client = chromadb.PersistentClient(path="../data/memory/chroma_db")

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-mpnet-base-v2"
)

class ChromaOps:
	def __init__(self):
		self.client = chroma_client

	def create_collection(self, name: str, description: str):
		collection = self.client.create_collection(
			name=name,
			embedding_function=sentence_transformer_ef,
			metadata={
				"description": description,
				"created": str(datetime.now())
			}  
		)
		return collection
	
	def get_collection(self, name: str):
		return self.client.get_collection(name=name)
	
	def delete_collection(self, name: str):
		self.client.delete_collection(name=name)

	def add_doc(self, collection_name: str, document: str, 
				metadata: Optional[Dict] = None, doc_id: Optional[str] = None):
		"""Add a single document to a collection"""
		collection = self.get_collection(collection_name)
		
		# Generate ID if not provided
		if doc_id is None:
			doc_id = f"doc_{datetime.now().timestamp()}"
		
		collection.add(
			documents=[document],
			metadatas=[metadata] if metadata else None,
			ids=[doc_id]
		)
		return doc_id

	def add_data(self, collection_name: str, documents: List[str], 
				 metadatas: Optional[List[Dict]] = None, ids: Optional[List[str]] = None):
		"""Add multiple documents to a collection"""
		collection = self.get_collection(collection_name)
		
		# Generate IDs if not provided
		if ids is None:
			ids = [f"doc_{i}_{datetime.now().timestamp()}" for i in range(len(documents))]
		
		collection.add(
			documents=documents,
			metadatas=metadatas,
			ids=ids
		)
		return ids

	def update_doc(self, collection_name: str, doc_id: str, 
				   document: Optional[str] = None, metadata: Optional[Dict] = None):
		"""Update a single document in a collection"""
		collection = self.get_collection(collection_name)
		
		update_params = {"ids": [doc_id]}
		if document is not None:
			update_params["documents"] = [document]
		if metadata is not None:
			update_params["metadatas"] = [metadata]
			
		collection.update(**update_params)

	def update_data(self, collection_name: str, ids: List[str], 
					documents: Optional[List[str]] = None, 
					metadatas: Optional[List[Dict]] = None):
		"""Update multiple documents in a collection"""
		collection = self.get_collection(collection_name)
		
		update_params = {"ids": ids}
		if documents is not None:
			update_params["documents"] = documents
		if metadatas is not None:
			update_params["metadatas"] = metadatas
			
		collection.update(**update_params)

	def delete_doc(self, collection_name: str, doc_id: str):
		"""Delete a single document from a collection by ID"""
		collection = self.get_collection(collection_name)
		collection.delete(ids=[doc_id])

	def delete_data(self, collection_name: str, ids: Optional[List[str]] = None, 
					where: Optional[Dict] = None, where_document: Optional[Dict] = None):
		"""Delete multiple documents from a collection"""
		collection = self.get_collection(collection_name)
		
		delete_params = {}
		if ids is not None:
			delete_params["ids"] = ids
		if where is not None:
			delete_params["where"] = where
		if where_document is not None:
			delete_params["where_document"] = where_document
			
		collection.delete(**delete_params)

	def query_doc(self, collection_name: str, query_text: str, 
				  n_results: int = 10, where: Optional[Dict] = None, 
				  where_document: Optional[Dict] = None):
		"""Query documents from a collection with a single query"""
		collection = self.get_collection(collection_name)
		
		query_params = {
			"query_texts": [query_text],
			"n_results": n_results
		}
		if where is not None:
			query_params["where"] = where
		if where_document is not None:
			query_params["where_document"] = where_document
			
		return collection.query(**query_params)

	def query_data(self, collection_name: str, query_texts: List[str], 
				   n_results: int = 10, where: Optional[Dict] = None, 
				   where_document: Optional[Dict] = None):
		"""Query documents from a collection with multiple queries"""
		collection = self.get_collection(collection_name)
		
		query_params = {
			"query_texts": query_texts,
			"n_results": n_results
		}
		if where is not None:
			query_params["where"] = where
		if where_document is not None:
			query_params["where_document"] = where_document
			
		return collection.query(**query_params)

	