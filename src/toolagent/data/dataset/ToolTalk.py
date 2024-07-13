import ast
import json
import os
import re

from toolagent.utils import read_JSON, write_JSON


class ToolTalk:
    def __init__(self, folder_path="", tool_folder_path="", write_filename=""):
        self.folder_path = folder_path
        self.write_filename = write_filename
        self.tool_folder_path = tool_folder_path
        self.all_apis = {}
        self.get_tool_information()
        self.data = []
        self.system_prompt = (
            "You are a helpful assistant. Here is some user data:"
            "\nlocation: {location}"
            "\ntimestamp: {timestamp}"
            "\nusername (if logged in): {username}"
        )
        self.load_data()

    def load_data(self):
        raw_data = []
        if self.folder_path != "":
            all_data_file_name = os.listdir(self.folder_path)
            for filename in all_data_file_name:
                now_data_filename = os.path.join(self.folder_path, filename)
                now_data = read_JSON(now_data_filename)
                raw_data.append([now_data, filename])

        for data, filename in raw_data:
            temp_data = {}
            temp_data["id"] = filename
            raw_conversations = data["conversation"]
            candidate_api_names = data["apis_used"]
            all_candidate_apis = []
            for candidate_api_name in candidate_api_names:
                all_candidate_apis.append(self.all_apis[candidate_api_name])
            temp_data["candidate_tools"] = all_candidate_apis
            user_information = data["metadata"]
            if user_information.get("username", -1) == -1:
                username_now = data["user"]["username"]
            else:
                username_now = user_information["username"]
            self.system_prompt = self.system_prompt.replace(
                "{location}", user_information["location"]
            )
            self.system_prompt = self.system_prompt.replace(
                "{timestamp}", user_information["timestamp"]
            )
            self.system_prompt = self.system_prompt.replace("{username}", username_now)

            final_conv = [{"role": "system", "content": self.system_prompt}]
            for i in raw_conversations:
                temp_conv = {}
                temp_conv["role"] = i["role"]
                temp_conv["content"] = i["text"]
                if i.get("apis", -1) != -1:
                    temp_conv["function_call"] = []
                    temp_conv["function_result"] = []
                    for used_apis in i["apis"]:
                        temp_function_call = {}
                        temp_function_call["name"] = used_apis["request"]["api_name"]
                        temp_function_call["parameters"] = used_apis["request"][
                            "parameters"
                        ]
                        if used_apis["response"] != None:
                            temp_function_call["function_result"] = used_apis[
                                "response"
                            ]
                        else:
                            temp_function_call["function_result"] = used_apis[
                                "exception"
                            ]
                        temp_conv["function_call"].append(temp_function_call)
                final_conv.append(temp_conv)

            temp_data["conversations"] = final_conv
            query = ""
            for i in final_conv:
                if i["role"] == "user":
                    query = i["content"]
                    break
            temp_data["query"] = query
            self.data.append(temp_data)

    def get_tool_information(self):
        all_py_file_name = os.listdir(self.tool_folder_path)
        all_py_file_name.remove("api.py")
        all_py_file_name.remove("exceptions.py")
        all_py_file_name.remove("__init__.py")
        all_py_file_name.remove("utils.py")
        for file_name in all_py_file_name:
            now_data_file = os.path.join(self.tool_folder_path, file_name)
            return_apis = get_all_tool_and_information(now_data_file)
            for api in return_apis:
                self.all_apis[api["name"]] = api


def get_all_tool_and_information(filename):
    apis = []
    with open(filename, "r") as source_code:
        tree = ast.parse(source_code.read())
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            attributes = []
            for sub_node in ast.iter_child_nodes(node):
                if isinstance(sub_node, ast.Assign):  # 找到类中的赋值语句
                    for target in sub_node.targets:
                        if isinstance(target, ast.Name):  # 类属性赋值
                            try:
                                value = ast.literal_eval(sub_node.value)
                                attributes.append((target.id, value))
                            except ValueError:  # 如果值不是常量，无法解析
                                attributes.append((target.id, None))

            classes.append((class_name, attributes))

    for api_name, all_parameters in classes:
        now_api = {}
        now_api["name"] = api_name
        for parameter_name, content in all_parameters[:3]:
            if parameter_name == "description":
                now_api["description"] = content
            elif parameter_name == "parameters":
                now_api["parameters"] = content
            elif parameter_name == "output":
                now_api["output"] = content
        if (
            now_api.get("description", -1) != -1
            and now_api.get("parameters", -1) != -1
            and now_api.get("output", -1) != -1
        ):
            apis.append(now_api)

    return apis
