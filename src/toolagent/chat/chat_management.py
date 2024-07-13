from ..chat._prototype import BasicChatManagementModule

class ChatManagementModule(BasicChatManagementModule):
    def __init__(self) -> None:
        self.system_message: str = "You are a helpful assistant."

        self.chat_history
        self.chat_template
    
    def clear_history(self) -> None:
        self.chat_history = [{"role": "system", "content": self.system_message}]