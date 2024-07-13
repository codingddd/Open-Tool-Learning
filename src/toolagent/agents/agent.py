"""Main Agent

"""

from typing import Any, List

from ._prototype import ChatAgent
from ..model._prototype import FoundationLanguageModel
from ..chat._prototype import BasicChatManagementModule
from ..tool._prototype import BasicToolCallingModule
from ..retrieval._prototype import BasicRetriever

from ..chat import ChatManagementModule
from ..tool import ToolCallingModule


class Agent(ChatAgent):
    def __init__(
        self,
        name: str = "Agent",
        description: str = "A chat agent which is euipped with tool learning and RAG.",
    ) -> None:
        self.name: str = name
        self.description: str = description

        self.llm: FoundationLanguageModel = None

        self.chat_management: BasicChatManagementModule = None
        self.tool_calling: BasicToolCallingModule = None
        self.retriever: BasicRetriever = None

    def load_llm(self, model_name, model_checkpoint) -> None:
        from ..model.llm import AutoModel

        self.llm = AutoModel(model_name, checkpoint_path=model_checkpoint)

    def load_retriever(self, retriever_input: BasicRetriever) -> None:
        self.retriever = retriever_input

    def load_chat_module(self) -> None:
        self.chat_management = ChatManagementModule()

    def load_tool_module(self) -> None:
        self.tool_calling = ToolCallingModule()

    def chat(self) -> Any:
        pass

    def pipeline(self, dataset) -> Any:
        pass
