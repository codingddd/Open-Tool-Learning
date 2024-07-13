from __future__ import annotations

from typing import Any, Dict, List

from toolagent.embedding._prototype import BasicEmbedder
from toolagent.retrieval._prototype import BasicRetriever
from toolagent.vectorstore._prototype import BasicVectorStore


class BasicToolCallingModule:
    set_list: List[str]
    tools_set: Dict[str, BasicToolPool]
    retriever: BasicRetriever

    def __init__(self) -> None:
        self.set_list: List[str]
        self.tools_set: Dict[str, BasicToolPool]
        self.retriever: BasicRetriever


class BasicToolPool:
    id_list: List[str]
    tools: Dict[str, List[BasicTool]]
    vectors: BasicVectorStore
    embedder: BasicEmbedder

    def __init__(self) -> None:
        self.id_list: List[str]
        self.tools: Dict[str, List[BasicTool]]
        self.vectors: BasicVectorStore
        self.embedder: BasicEmbedder

    def add_tool(self) -> None:
        raise NotImplementedError

    def remove_tool(self) -> None:
        raise NotImplementedError


class BasicTool:
    tool_name: str
    tool_description: str
    callable: bool

    def __init__(self) -> None:
        self.tool_name
        self.tool_description

        self.callable

    def __call__(self):
        pass

    def __eq__(self, other) -> bool:
        # if isinstance(other, class_name):
        #     return self.name == other.name
        # return False
        raise NotImplementedError

    def __hash__(self) -> Any:
        # return hash((self.name, self.description))
        raise NotImplementedError


class BasicLocalTool(BasicTool):
    pass


class BasicRemoteTool(BasicTool):
    pass
