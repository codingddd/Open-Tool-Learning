from ..model.llm.LLaMA import LLaMA
from ..data.dataset.API_Bank import API_Bank
from ..data.dataset.ToolEyes import ToolEyes
from ..data.dataset.ToolTalk import ToolTalk
from ..data.dataset.SoAy import SoAy
from ..data.general_dataset import General_dataset
from ..data.one_data import one_data

import argparse
import re
import json


def main(args):
    test_dataset = get_data(args)
    model = get_model(args)

    if args.eval_mode == "all":
        eval_whole_process(model, test_dataset.data)
        eval_step_by_step(model, test_dataset.data)
    elif args.mode == "step_by_step":
        eval_step_by_step(model, test_dataset.data)
    elif args.mode == "whole":
        eval_whole_process(model, test_dataset.data)


### we only need query, and wo need to seen the whole process
def eval_whole_process(model, all_data):
    max_step = 0
    for data in all_data:
        data = one_data(data)
        query = data.query
        conv = data.conversations
        system = ""
        for i in conv:
            if i["role"] == "system":
                system = i["content"]





### we pass all history message and only eval the performance of model's next step, we only eval response including tool calling
def eval_step_by_step(model, all_data):
    '''
    tool_p
    tool_r
    tool_f1

    parameter_p
    parameter_r
    parameter_f1
    '''

    tool_gold_all = 0
    tool_predict_all = 0
    tool_right_number = 0

    parameter_gold_all = 0
    parameter_predict_all = 0
    parameter_right_number = 0

    for data in all_data:
        data = one_data(data)
        for temp_data in data.chat_prompt:
            model_input, gold_answer = temp_data["prompt"], temp_data["gold_answer"]
            gold_tools = gold_answer.get("function_call", -1)
            output = model.predict(model_input)
            predict_tools = process_model_output(output)
            gold_tools_dict = {}
            if gold_tools != -1:
                tool_gold_all += len(gold_tools)
                for tool in gold_tools:
                    gold_tools_dict[tool["name"]] = tool
                    parameter_gold_all += len(tool["parameters"])

            if predict_tools != None:
                tool_predict_all += len(predict_tools)
                for tool in predict_tools:
                    if tool["name"] in gold_tools_dict:
                        tool_right_number += 1
                        compare_tool = gold_tools_dict[tool["name"]]
                        parameter_predict_all += len(tool["parameters"])

                        for parameter in tool["parameters"]:
                            if parameter in compare_tool["parameters"] and tool["parameters"][parameter] == compare_tool["parameters"][parameter]:
                                parameter_right_number += 1
    tool_p = tool_right_number/tool_predict_all
    tool_r = tool_right_number/tool_gold_all
    tool_f1 = 2*tool_r*tool_p/(tool_r + tool_p)

    parameter_p = parameter_right_number/parameter_predict_all
    parameter_r = parameter_right_number/parameter_gold_all
    parameter_f1 = 2*parameter_r*parameter_p/(parameter_r + parameter_p)

    return (tool_r, tool_r, tool_f1), (parameter_p, parameter_r, parameter_f1)



def get_model(args):
    model_name = args.backbone_model
    model_path = args.model_path
    if model_name == "llama3":
        model = LLaMA(checkpoint_path=model_path)
    else:
        model = LLaMA(checkpoint_path=model_path)
    return model


def get_data(args):
    if args.dataset_name == "API_Bank":
        test_dataset = API_Bank(mode="test", filename=args.data_path, write_filename=args.write_file_path)
    elif args.dataset_name == "ToolEyes":
        test_dataset = ToolEyes(filename=args.data_path, write_filename=args.write_file_path)
    elif args.dataset_name == "ToolTalk":
        test_dataset = ToolTalk(folder_path=args.folder_name, tool_folder_path=args.tool_folder_path, write_filename=args.write_file_path)
    elif args.dataset_name == "SoAy":
        prompt = ""
        test_dataset = SoAy(folder_path=args.folder_name, tool_folder_path=args.tool_folder_path, prompt=prompt)
    else:
        test_dataset = General_dataset(filename=args.data_path)
    return test_dataset


## we need to define the style of model's response
def process_model_output(output):
    used_tool = re.search("\[[\s\S]*\]", output)
    if used_tool != None:
        used_tool = re.search("\[[\s\S]*\]", output).group(0)
    else:
        return None
    try:
        tool = json.loads(used_tool)
    except:
        print("the format of model's response is wrong")
        tool = None

    return tool


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--backbone_model", type=str, default="llama3", required=False, help='the model you choose')
    parser.add_argument("--model_path", type=str, required=True, help="the path of model parameter")
    parser.add_argument("--dataset_name", type=str, default="default", required=False, help='dataset name you choose, if you want to use api_bank, you can choose it')
    parser.add_argument("--data_path", type=str, default="", required=False, help="The specific path of the data")
    parser.add_argument("--folder_name", type=str, default="", required=False, help="the style of ToolTalk")
    parser.add_argument("--output_answer_file", type=str, required=True, help="output file path")
    parser.add_argument("--tool_folder_path", type=str, required=True, help="the folder path of tool")
    parser.add_argument("--write_file_path", type=str, default="", required=False, help="the processed data path ,you can choose to write or not")
    parser.add_argument("--openai_key", type=str, default="", required=False, help="openai key to use chatgpt")
    parser.add_argument("--eval_mode", type=str, default="all", required=False, help="eval step by step or eval the whole process or both")
    args = parser.parse_args()

    main(args)

