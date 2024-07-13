from typing import Dict, Set, Tuple

from toolagent.embedding._prototype import BasicEmbedder
from toolagent.prompt.tool import ToolPrompt
from toolagent.tool._prototype import BasicTool, BasicToolPool
from toolagent.utils import generate_random_key
from toolagent.vectorstore import TensorStore
from toolagent.vectorstore._prototype import BasicVectorStore


class ToolPool(BasicToolPool):
    def __init__(self) -> None:
        pass

class RetrievableToolPool(BasicToolPool):
    def __init__(self, embedder: BasicEmbedder) -> None:
        self.id_list: Set[str] = set()
        self.tools: Dict[str, BasicTool] = dict()
        self.vectors: BasicVectorStore = TensorStore()
        self.embedder: BasicEmbedder = embedder
        self.toolprompt = ToolPrompt()

    def add_tool(self, tool: BasicTool, check: bool = False) -> str:
        if check:
            check_flag, check_tool_id = self.check_duplication(tool)
            if check_flag:
                return check_tool_id
        tool_id = None
        while True:
            tool_id = generate_random_key()
            if tool_id not in self.id_list:
                break
        self.id_list.add(tool_id)
        self.tools[tool_id] = tool
        self.vectors.add(self.embedder, tool_id, self.toolprompt.get_prompt_for_retrieval(tool)) #TODO TensorStore add方法
        return tool_id

    def remove_tool(self, tool_id: str) -> None:
        self.id_list.remove(tool_id)
        del self.tools[tool_id]
        self.vectors.remove(tool_id) #TODO TensorStore remove方法

    def check_duplication(self, tool: BasicTool) -> Tuple[bool, str]:
        for tool_id in self.tools:
            if tool == self.tools[tool_id]:
                return True, tool_id
        return False, None
