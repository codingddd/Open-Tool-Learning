import json
import re


class one_data:

    def __init__(self, data, template="default"):
        self.data = data
        self.template = template
        self.id = self.data["id"]
        self.conversations = self.data["conversations"]
        self.candidate_tools = self.data["candidate_tools"]
        self.system = ""
        self.query = self.data["query"]
        self.chat_conv = []
        self.chat_prompt = []

        self.convert_to_model_conversations()
        self.convert_to_model_input_str()

    def convert_to_model_conversations(self):

        conversations = self.data["conversations"]
        now_conv = []
        for temp_role in conversations:
            now_conv.append(temp_role)
            if temp_role["role"] == "assistant" and temp_role.get("function_result", -1) != -1:
                temp_data = {}
                temp_data["candidate_tools"] = self.data["candidate_tools"]
                temp_data["conversations"] = now_conv[:]
                self.chat_conv.append(temp_data)


    def convert_to_model_input_str(self):

        template = {}
        if self.template == "default":
            template["system"] = "System: "
            template["user"] = "User: "
            template["assistant"] = "Assistant: "
            template["function_result"] = "Function result:"
        else:
            if type(template) == type(""):
                template = json.loads(self.template)
            else:
                assert type(template) == type({})
                template = template
        for data in self.chat_conv:
            now_data_str = ""
            conversations = data["conversations"]

            for i in range(len(conversations)-1):
                now_conv = conversations[i]
                if now_conv["role"] == "system":
                    prompt = now_conv["content"].replace("[candidate_tools]", str(self.candidate_tools))
                    now_data_str += template[now_conv["role"]] + prompt
                    self.system = prompt
                elif now_conv["role"] == "assistant":
                    if now_conv.get("function_result", -1) != -1:
                        now_data_str += template[now_conv["role"]] + now_conv["content"] + template["function_result"] + str(now_conv["function_result"])
                    else:
                        now_data_str += template[now_conv["role"]] + now_conv["content"]
                else:
                    now_data_str += template[now_conv["role"]] + now_conv["content"]

            final_prompt = now_data_str
            assert conversations[-1]["role"] == "assistant"
            gold_answer = conversations[-1]["content"]

            self.chat_prompt.append({"prompt": final_prompt, "gold_answer": gold_answer})