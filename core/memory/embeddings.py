import math
from typing import List, Tuple

class LocalVectorEngine:
    """Local Vector Embeddings & Cosine Similarity search engine."""

    def __init__(self, dimension: int = 768):
        self.dimension = dimension

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if len(v1) != len(v2) or not v1:
            return 0.0
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_v1 = math.sqrt(sum(a * a for a in v1))
        norm_v2 = math.sqrt(sum(b * b for b in v2))
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        return dot_product / (norm_v1 * norm_v2)

    def search_similar(self, query_vec: List[float], candidates: List[Tuple[str, List[float]]], top_k: int = 5) -> List[Tuple[str, float]]:
        scores = []
        for doc_id, vec in candidates:
            score = self.cosine_similarity(query_vec, vec)
            scores.append((doc_id, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
