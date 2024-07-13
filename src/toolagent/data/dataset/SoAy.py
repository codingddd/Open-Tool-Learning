import json
import os
import re

from toolagent.utils import read_JSON, write_JSON


class SoAy:
    def __init__(self,folder_path, tool_folder_path, prompt=""):
        self.folder_path = folder_path
        self.tool_folder_path = tool_folder_path
        self.all_apis = []
        self.data = []

        self.prompt = prompt

        self.get_tool_information()
    def load_data(self):
        all_data = []
        filenames = os.listdir(self.folder_path)
        for filename in filenames:
            if not filename.endswith("txt"):
                filepath = os.path.join(self.folder_path, filename)
                temp_data = read_JSON(filepath)

                for data in temp_data:

                    final_data = {}
                    final_data["candidate_tools"] = self.all_apis
                    final_data["id"] = filepath
                    raw_conversation = []
                    if "[candidate_tools]" in self.prompt:
                        self.prompt = self.prompt.replace("[candidate_tools]", self.all_apis)
                    raw_conversation.append({"role": "system", "content": self.prompt})
                    raw_conversation.append({"role": "user", "content": data["Query"]})
                    final_data["conversations"] = raw_conversation
                    query = ""
                    for i in raw_conversation:
                        if i["role"] == "user":
                            query = i["content"]
                            break
                    final_data["query"] = query
                    self.data.append(final_data)
    def get_tool_information(self):
        tool_filename_lst = os.listdir(self.tool_folder_path)
        for temp_name in tool_filename_lst:
            tool_file_name = os.path.join(self.tool_folder_path, temp_name)
            raw_temp_apis = read_JSON(tool_file_name)
            for temp_api in raw_temp_apis:
                now_api = {}
                now_api["name"] = temp_api["function_name"]
                now_api["parameters"] = temp_api["parameters"]
                now_api["output"] = temp_api["return"]
                now_api["description"] = ""
                self.all_apis.append(now_api)


