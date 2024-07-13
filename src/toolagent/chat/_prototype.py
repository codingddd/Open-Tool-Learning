from typing import Any, List

class BasicChatManagementModule:
    system_message: str
    chat_template: Any
    chat_history: List[dict]

    def __init__(self) -> None:
        self.system_message: str
        self.chat_history: List[dict]
        self.chat_template

    def clear_history(self) -> None:
        self.chat_history = [{"role": "system", "content": self.system_message}]