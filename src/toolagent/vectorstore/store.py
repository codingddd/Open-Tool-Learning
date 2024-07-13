from typing import Dict, List

from ..vectorstore._prototype import BasicVectorStore
from ..embedding._prototype import BasicEmbedder


class VectorStore(BasicVectorStore):
    def __init__(self) -> None:
        self.vector_length = -1
        self.storage: Dict[str,List]

    def add(self, embedder: BasicEmbedder, key_id: str, input_text: str) -> None:
        vector = embedder(input_text)
        if self.vector_length < 0:
            self.vector_length = len(vector)
        else:
            if self.vector_length != len(vector):
                pass #TODO 存储张量维度不一致的Error
        self.storage[key_id] = vector

    def remove(self, key_id: str) -> None:
        del self.storage[key_id]