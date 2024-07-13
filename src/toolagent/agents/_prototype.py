from __future__ import annotations


class BasicAgent:
    """A basic class for agent.

    Agent Information:
        self.name
        self.description

    Foundation Model:
        self.llm
    """

    def __init__(self) -> None:
        self.name: str
        self.description: str
        self.llm

    def load_llm(self) -> None:
        pass


class ChatAgent(BasicAgent):
    """A chat agent with tool learning and retrieval modules.

    Chat Relevant Information:
        self.chat_management

    Function/Tool Calling Module:
        self.tool_calling

    Retrieval Module:
        self.retrieval
    """

    def __init__(self) -> None:
        self.chat_management
        self.tool_calling
