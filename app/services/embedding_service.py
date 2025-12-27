from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from typing import List

class EmbeddingService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer('BAAI/bge-m3', trust_remote_code=True, device=self.device, model_kwargs={"dtype": torch.float16})

    def encode(self, text: str) -> List[float]:
        """Encode single text to embedding vector"""
        embedding = self.model.encode([text])[0]
        return embedding.tolist()

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Encode multiple texts to embedding vectors"""
        embeddings = self.model.encode(texts)
        return [emb.tolist() for emb in embeddings]

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

embedding_service = EmbeddingService()