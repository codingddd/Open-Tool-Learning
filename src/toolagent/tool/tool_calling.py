
from ..tool._prototype import BasicToolCallingModule
from ..retrieval._prototype import BasicRetriever

class ToolCallingModule(BasicToolCallingModule):
    def __init__(self, retriever: BasicRetriever) -> None:
        self.set_list = []
        self.tools_set = dict()
        self.retriever = retriever
