import json
from .._tool import BasicTool



class SysTool(BasicTool):
    
    def __init__(self, **args):
        assert "source" in args
        assert "name" in args
        self.source = args.get("source")
        self.tool_name = args.get("name")
        self.tool_description = args.get("description", None)
        self.input_parameters = args.get("input_parameters", None)
        self.output_parameters = args.get("output_parameters", None)
        self.database = args.get("database", None)
        self.callable_path = args.get("callable_path", None)
        self.callable = args.get("callable", "UNK")
        self.remote = args.get("remote", "UNK")
        self.required = args.get("required", "UNK")

    def __call__(self, **kwargs):
        if self.source == "Tooleyes":
            try:
                # from ..dependency.tooleyes.Tool_Library.Random.Random.tool import random
                exec(
                    f"""from ..{'.'.join(kwargs["path"].split('/')[::])}.tool import {kwargs["action"]}""")
                result = eval(kwargs["action"])(**kwargs["action_input"])
                result = json.dumps(result, ensure_ascii=False)
                return {"observation": result, 'action': kwargs["action"]}
            except Exception as e:
                return {"error": str(e), "action": kwargs["action"]}
                
        elif self.source == "APIbank":
            try:
                param_dict = kwargs["param_dict"]
                tool_module = kwargs["module"]
                processed_parameters = {}
                for input_key in param_dict:
                    input_value = param_dict[input_key]
                    assert input_key in self.input_parameters, 'invalid parameter name. parameter: {}'.format(input_key)
                    required_para = self.input_parameters[input_key]

                    required_type = required_para['type']
                    if required_type == 'int':
                        if isinstance(input_value, str):
                            assert input_value.isdigit(), 'invalid parameter type. parameter: {}'.format(input_value)
                        processed_parameters[input_key] = int(input_value)
                    elif required_type == 'float':
                        if isinstance(input_value, str):
                            assert input_value.replace('.', '', 1).isdigit(), 'invalid parameter type.'
                        processed_parameters[input_key] = float(input_value)
                    elif required_type == 'str':
                        processed_parameters[input_key] = input_value
                    elif required_type == 'list(str)':
                        # input_value = input_value.replace('\'', '"')
                        processed_parameters[input_key] = input_value
                    elif required_type == 'list':
                        # input_value = input_value.replace('\'', '"')
                        processed_parameters[input_key] = input_value
                    elif required_type == 'bool':
                        processed_parameters[input_key] = input_value == 'True'
                    else:
                        raise Exception('invalid parameter type.')
                
                result = tool_module.call(**processed_parameters)
                return result
            except Exception as e:
                raise Exception('tool call false')
        
        elif self.source == "APItalk":
            try:
                param_dict = kwargs["param_dict"]
                tool_module = kwargs["module"]
                
                result = tool_module.call(**param_dict)
                return result
            except Exception as e:
                return {"error": str(e), "action": kwargs["action"]}
            
            

    def __eq__(self, other):
        # if isinstance(other, class_name):
        #     return self.name == other.name
        # return False
        raise NotImplementedError

    def __hash__(self):
        # return hash((self.name, self.description))
        raise NotImplementedError
    