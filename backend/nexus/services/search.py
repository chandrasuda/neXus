import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity
import os

class SearchEngine:
    def __init__(self):
        self.embedding_dim = 1536 # Default for OpenAI ada-002

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        """
        from openai import OpenAI
        
        # Try OpenAI/Grok key
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROK_API_KEY")
        if api_key:
            try:
                # Basic check to avoid calling Grok if it doesn't support embeddings endpoint yet
                # We'll default to OpenAI endpoint if OPENAI_API_KEY is present
                base_url = "https://api.openai.com/v1"
                if not os.getenv("OPENAI_API_KEY") and os.getenv("GROK_API_KEY"):
                     # Hypothethical Grok embedding endpoint, or fallback to random if not supported
                     pass 

                client = OpenAI(api_key=api_key, base_url=base_url)
                if "api.openai.com" in base_url:
                     resp = client.embeddings.create(input=text, model="text-embedding-3-small")
                     return resp.data[0].embedding
            except Exception as e:
                print(f"Embedding API failed: {e}")
        
        # Mock embedding for demonstration
        np.random.seed(abs(hash(text)) % (2**32)) 
        return np.random.rand(self.embedding_dim).tolist()

    def compute_similarity(self, query_vector: List[float], document_vectors: List[List[float]]) -> List[float]:
        query_vec = np.array(query_vector).reshape(1, -1)
        doc_vecs = np.array(document_vectors)
        
        if len(doc_vecs) == 0:
            return []

        similarities = cosine_similarity(query_vec, doc_vecs)
        return similarities[0].tolist()

    def search(self, query_vector: List[float], documents: List[Dict[str, Any]], vector_key: str = "embedding", top_k: int = 5) -> List[Dict[str, Any]]:
        if not documents:
            return []

        doc_vectors = [doc[vector_key] for doc in documents]
        scores = self.compute_similarity(query_vector, doc_vectors)
        
        scored_docs = []
        for i, score in enumerate(scores):
            doc_with_score = documents[i].copy()
            doc_with_score["score"] = score
            scored_docs.append(doc_with_score)
            
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]
