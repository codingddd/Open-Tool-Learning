from typing import List, Dict

class BasicVectorStore:
    def __init__(self) -> None:
        self.vector_length: int
        self.storage: Dict[str, List]

    def add(self) -> None:
        raise NotImplementedError
    
    def remove(self) -> None:
        raise NotImplementedError