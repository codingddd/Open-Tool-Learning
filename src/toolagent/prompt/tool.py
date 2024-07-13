
from toolagent.tool._prototype import BasicTool

class ToolPrompt:
    def __init__(self) -> None:
        self.prompt_for_retrieval = "Tool Name: {}\nTool Description: {}"

    def get_prompt_for_retrieval(self, tool: BasicTool) -> str:
        name = tool.tool_name
        description = tool.tool_description
        return self.prompt_for_retrieval.format(name, description)