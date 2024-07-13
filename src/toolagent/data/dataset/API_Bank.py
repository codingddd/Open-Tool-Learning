from ...utils import read_JSON,write_JSON
import re
import json
'''
Pass in the 'response' file, filename1,filename2,filename3 correspond to level1, level1,level1 respectively
mode means 'train' or 'test'
write_filename1,write_filename2,write_filename3 correspond to the file you want to write
'''
class API_Bank:

    def __init__(self, mode="train", filename="", write_filename=""):
        self.filename = filename
        self.write_filename = write_filename
        self.mode = mode
        self.data = []
        if self.mode == "train":
            self.load_train_data()
        else:
            self.load_test_data()
    def load_test_data(self):
        if "1" in self.filename or "2" in self.filename:
            self.data.extend(process_level12_test(self.filename, self.write_filename))
        else:
            self.data.extend(process_level3_test(self.filename, self.write_filename))
    def load_train_data(self):
        self.data.extend(process_train_data(self.filename))


##############  Convert the fused input into a single step. candidate_tool indicates whether the input contains a candidate tool.
def extract_tool_name_and_parameters(input):
    tool_name = ""
    for i in range(13, len(input)):
        if input[i] != "(":
            tool_name += input[i]
        else:
            break

    parameters = re.search("\(.*\)", input).group(0)
    parameter_dict = {}
    if parameters[0] == "(":
        parameters = parameters[1:]
    if parameters[-1] == ")":
        parameters = parameters[:-1]
    all_parameter_names = []
    if parameters != "":
        first_parameter_name = ""
        for i in parameters:
            if i != "=":
                first_parameter_name += i
            else:
                all_parameter_names.append(first_parameter_name)
                break

        other_parameter_names = re.findall(', [^=]*=', parameters)
        for parameter in other_parameter_names:
            parameter_name_temp = parameter[2:-1]
            all_parameter_names.append(parameter_name_temp)

        parameter_entity = re.split(', [^=]*=', parameters)
        if len(all_parameter_names) != 0:
            parameter_entity[0] = parameter_entity[0].split("=")[1]
            assert len(parameter_entity) == len(all_parameter_names)

            for i in range(len(parameter_entity)):
                parameter_dict[all_parameter_names[i]] = parameter_entity[i]

        for j in parameter_dict:
            if parameter_dict[j][0] == "'":
                parameter_dict[j] = parameter_dict[j][1:]
            if parameter_dict[j][-1] == "'":
                parameter_dict[j] = parameter_dict[j][:-1]


    function_call = {}
    function_call["name"] = tool_name
    function_call["parameters"] = parameter_dict

    return function_call


def process_input(input, candidate_tool):
    conversation = []
    candidate_tool_str = ""
    user_ai_split = input.split("\nUser: ")
    if candidate_tool == True:
        candidate_tool_str = user_ai_split[0]
        user_ai_split = user_ai_split[1:]

    for use_ai in user_ai_split:
        ai_splits = use_ai.split("\nAI: ")
        user = ai_splits[0]
        ais = ai_splits[1:]
        if "\nAPI-Request: " in user:
            raw_split_data = user.split("\nAPI-Request: ")
            user = raw_split_data[0]
            conversation.append({"role":"user", "content": user})
            for i in raw_split_data[1:]:
                request, function_result = i.split("->")
                now_response = {}
                now_response["role"] = "assistant"
                now_response["content"] = "API-Request: " + request
                now_response["function_call"] = [extract_tool_name_and_parameters(request)]
                now_response["function_result"] = [function_result]
                conversation.append(now_response)
        else:
            if user != "":
                if user.startswith("User: "):
                    user = user[6:]
                conversation.append({"role": "user", "content": user})

        for ai in ais:
            if "\nAPI-Request: " in ai:
                raw_split_data = ai.split("\nAPI-Request: ")
                ai = raw_split_data[0]
                conversation.append({"role": "assistant", "content": ai})
                for i in raw_split_data[1:]:
                    request, function_result = i.split("->")
                    now_response = {}
                    now_response["role"] = "assistant"
                    now_response["content"] = "API-Request: " + request
                    now_response["function_call"] = [extract_tool_name_and_parameters(request)]
                    now_response["function_result"] = [function_result]
                    conversation.append(now_response)
            else:
                if ai != "":
                    conversation.append({"role": "assistant", "content": ai})

    return conversation, candidate_tool_str

############ For level 1 and level 2, pass in the response file
def process_level12_test(filename_response, write_file_name=""):
    return_response_data = read_JSON(filename_response)
    ######  The content corresponding to each filename
    file_to_data = {}
    for i in return_response_data:
        if i["file"] in file_to_data:
            file_to_data[i["file"]].append(i)
        else:
            file_to_data[i["file"]] = [i]
    final_data_lst = []
    for file in file_to_data:
        final_data_need = {}
        final_data_need["id"] = file
        final_data = file_to_data[file][-1]
        instruction_raw = final_data["instruction"]
        instruction, candidate_tool_str = instruction_raw.split("\n\nAPI descriptions:\n")
        instruction += "\n\nAPI descriptions:\n[candidate_tools]"
        candidate_tool_str = candidate_tool_str.replace("\n", ",")
        candidate_tool_str = "[" + candidate_tool_str + "]"
        tools = json.loads(candidate_tool_str)


        raw_conversation, _= process_input(final_data["input"], candidate_tool=False)
        raw_conversation.append({"role": "assistant", "content": final_data["expected_output"]})
        raw_conversation.insert(0,{"role": "system", "content": instruction})
        final_data_need["conversations"] = raw_conversation
        final_data_need["candidate_tools"] = tools
        query = ""
        for i in raw_conversation:
            if i["role"] == "user":
                query = i["content"]
                break
        final_data_need["query"] = query
        final_data_lst.append(final_data_need)
    if write_file_name != "":
        write_JSON(write_file_name, final_data_lst)

    return final_data_lst

def process_level3_test(filename_response, write_file_name=""):  # 针对level3， 传入response文件
    return_response_data = read_JSON(filename_response)
    ######  The content corresponding to each filename
    file_to_data = {}
    for i in return_response_data:
        if i["sample_id"] in file_to_data:
            file_to_data[i["sample_id"]].append(i)
        else:
            file_to_data[i["sample_id"]] = [i]
    final_data_lst = []
    for sample_id in file_to_data:
        final_data_need = {}
        final_data_need["id"] = sample_id
        final_data = file_to_data[sample_id][-1]

        instruction_raw = final_data["instruction"].split("\n\nAPI descriptions:\n")[0]
        instruction_raw += "\n\nAPI descriptions:\n[candidate_tools]"
        raw_conversation, candidate_tool_str = process_input(final_data["input"], candidate_tool=True)
        candidate_tool_str = candidate_tool_str.replace("\n", ",")
        candidate_tool_str = "[" + candidate_tool_str + "]"
        tools = json.loads(candidate_tool_str)
        raw_conversation.insert(0, {"role": "system", "content": instruction_raw})
        raw_conversation.append({"role": "assistant", "content": final_data["output"]})
        final_data_need["conversations"] = raw_conversation
        final_data_need["candidate_tools"] = tools
        query = ""
        for i in raw_conversation:
            if i["role"] == "user":
                query = i["content"]
                break
        final_data_need["query"] = query
        final_data_lst.append(final_data_need)
    if write_file_name != "":
        write_JSON(write_file_name, final_data_lst)
    return final_data_lst

def get_query(input):
    query_raw = input.split("\nUser: ")[1]
    query_raw = query_raw.split("\nAI: ")[0]
    if "\nAPI-Request: " in query_raw:
        query_raw = query_raw.split("\nAPI-Request: ")[0]
    return query_raw

def process_train_data(filename, write_file_name=""):   ########  传入对应的response文件
    all_data = read_JSON(filename)
    query_to_data = {}
    for data in all_data:
        query = get_query(data["input"])
        if query not in query_to_data:
            query_to_data[query] = [data]
        else:
            query_to_data[query].append(data)
    final_data_lst = []
    for query in query_to_data:
        final_data_need = {}
        final_data = query_to_data[query][-1]

        final_data_need["id"] = query
        instruction_raw = final_data["instruction"].split("\n\nAPI descriptions:\n")[0]
        instruction_raw += "\n\nAPI descriptions:\n[candidate_tools]"
        raw_conversation, candidate_tool_str = process_input(final_data["input"], candidate_tool=True)
        candidate_tool_str = "[" + candidate_tool_str + "]"
        candidate_tool_str = candidate_tool_str.replace("\n", ",")
        tools = json.loads(candidate_tool_str)
        raw_conversation.insert(0, {"role": "system", "content": instruction_raw})
        raw_conversation.append({"role": "assistant", "content": final_data["output"][4:]})
        final_data_need["conversations"] = raw_conversation
        final_data_need["candidate_tools"] = tools
        query = ""
        for i in raw_conversation:
            if i["role"] == "user":
                query = i["content"]
                break
        final_data_need["query"] = query
        final_data_lst.append(final_data_need)
    if write_file_name != "":
        write_JSON(write_file_name, final_data_lst)
    return final_data_lst






if __name__ == '__main__':
    # filename_api = r"D:\ZX_file\first_study\parameter_filling\dataset\api-bank\test_data\level-1-api.json"
    filename_response = r"D:\ZX_file\first_study\parameter_filling\dataset\api-bank\train_data\lv1-response-train.json"
    write_file_name = r"D:\ZX_file\first_study\parameter_filling\dataset\api-bank\converted\level_1_train.json"
    process_train_data(filename_response, write_file_name)



