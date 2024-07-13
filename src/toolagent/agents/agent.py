"""Main Agent

"""

from typing import Any, List

from toolagent.chat import ChatManagementModule
from toolagent.chat._prototype import BasicChatManagementModule
from toolagent.model._prototype import FoundationLanguageModel
from toolagent.retrieval._prototype import BasicRetriever
from toolagent.tool import ToolCallingModule
from toolagent.tool._prototype import BasicToolCallingModule
from toolagent.agents._prototype import ChatAgent


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
