import re
import json
import os
from tool.tool import SysTool

from dependency.apibank.apis.api import API
from dependency.tooltalk.apis import ALL_APIS
from dependency.tooltalk.apis.account import ACCOUNT_DB_NAME, DeleteAccount, UserLogin, LogoutUser, RegisterUser

class BasicLoader:

    def __init__(self) -> None:
        pass

    def load_executable_tools(self):
        pass

    def get_executable_tools(self):
        pass

class APIbankLoader(BasicLoader):
    def __init__(self, args):
        self.args = args
        self.apis_dir = self.args.apis_dir  # /public/home/wlchen/hhan/my-tool-learning/api-bank/lv3_apis
        self.database_dir = self.args.database_dir #/public/home/wlchen/hhan/my-tool-learning/api-bank/init_database
        self.apis = []
        self.init_databases = {}
        self.inited_tools = {} #the dict for callable module
        self.token_checker = None
        self.executable_tools = {} #the dict for SysTool class
        self.load_executable_tools()
        
    
    def load_executable_tools(self):
        import importlib.util

        all_apis = []
        # import all the file in the apis folder, and load all the classes
        except_files = ['__init__.py', 'api.py']
        for file in os.listdir(self.apis_dir):
            if file.endswith('.py') and file not in except_files:
                api_file = file.split('.')[0]
                basename = os.path.basename(self.apis_dir)
                module = importlib.import_module(f'{basename}.{api_file}')
                classes = [getattr(module, x) for x in dir(module) if isinstance(getattr(module, x), type)]
                for cls in classes:
                    if issubclass(cls, API) and cls is not API:
                        all_apis.append(cls)

        classes = all_apis

        init_database_dir = self.database_dir
        for file in os.listdir(init_database_dir):
            if file.endswith('.json'):
                database_name = file.split('.')[0]
                with open(os.path.join(init_database_dir, file), 'r') as f:
                    self.init_databases[database_name] = json.load(f)

        # Get the description parameter for each class
        for cls in classes:
            if issubclass(cls, object) and cls is not object:
                name = cls.__name__
                cls_info = {
                    'source': "APIbank",
                    'name': name,
                    'class': cls,
                    'description': cls.description,
                    'input_parameters': cls.input_parameters,
                    'output_parameters': cls.output_parameters,
                    'callable': True,
                    'remote': False,
                }
                
                if hasattr(cls, 'database_name') and cls.database_name in self.init_databases:
                    cls_info['database'] = self.init_databases[cls.database_name]
                
                self.executable_tools[cls_info["name"]] = SysTool(**cls_info)  
                
                self.apis.append(cls_info)
                
        for cls_info in self.apis:
            self.init_tool(cls_info["name"])
        
    
        if 'CheckToken' in [api['name'] for api in self.apis]:
            self.token_checker = self.inited_tools["CheckToken"] #修改代码后不知道是否还需要维护self.token_checker这个变量
            
    def get_api_by_name(self, name: str):
        """
        Gets the API with the given name.

        Parameters:
        - name (str): the name of the API to get.

        Returns:
        - api (dict): the API with the given name.
        """
        for api in self.apis:
            if api['name'] == name:
                return api
        raise Exception('invalid tool name.')
    

    def init_tool(self, tool_name: str, *args, **kwargs):
        """
        Initializes a tool with the given name and parameters.

        Parameters:
        - tool_name (str): the name of the tool to initialize.
        - args (list): the positional arguments to initialize the tool with.
        - kwargs (dict): the parameters to initialize the tool with.

        Returns:
        - tool (object): the initialized tool.
        """
        # Get the class for the tool
        api_class = self.get_api_by_name(tool_name)['class']#拿到定义的类的类别class
        temp_args = []

        if 'init_database' in self.get_api_by_name(tool_name):
            # Initialize the tool with the init database
            temp_args.append(self.get_api_by_name(tool_name)['init_database'])
        
        if tool_name != 'CheckToken' and 'token' in self.get_api_by_name(tool_name)['input_parameters']:
            temp_args.append(self.token_checker)

        args = temp_args + list(args)
        tool = api_class(*args, **kwargs)#返回定义的实例(到这里有.database，如果是python代码内定义了self.database)

        self.inited_tools[tool_name] = tool
        return tool
    
    def get_executable_tools(self):
        return self.executable_tools, self.inited_tools
        
    def command_line(self):
        """
        Starts the command line interface for the tool manager.
        """
        mode = 'function_call' # 'function_call' or 'qa'
        if mode == 'qa':
            while True:
                tool_keywords = input('Please enter the keywords for the tool you want to use (\'exit\' to exit):\n')
                tool_searcher = self.executable_tools['ToolSearcher']
                d = {"module": self.inited_tools['ToolSearcher'], "param_dict": {"keywords": tool_keywords}}
                response = tool_searcher(**d)
                api_name = response['output']['name'] 
                
                api_name = "QueryMeeting"
                param_dict = {"user_name": "John"}
                    
                if api_name not in self.executable_tools:
                    raise Exception('Tool is not within the scope of executable tools')
                else:
                    t = self.executable_tools[api_name]
                    d = {"module": self.inited_tools[api_name], "param_dict": param_dict}
                    result = t(**d)
                    return result
                        
        elif mode == 'function_call':
            while True:
                # command = input('Please enter the command for the tool you want to use: \n')
                command = "API-Request: [ToolSearcher(keywords='QueryMeeting')]"
                command = "API-Request: [QueryMeeting(user_name='John')]"
            
                api_name, param_dict = self.parse_api_call(command)
            
                if api_name not in self.executable_tools:
                    raise Exception('Tool is not within the scope of executable tools')
                else:
                    t = self.executable_tools[api_name]
                    d = {"module": self.inited_tools[api_name], "param_dict": param_dict}
                    result = t(**d)
                    return result
        
        
    def parse_api_call(self, text):
        pattern = r"\[(\w+)\((.*)\)\]"
        match = re.search(pattern, text, re.MULTILINE)

        api_name = match.group(1)
        params = match.group(2)

        param_pattern = r"(\w+)\s*=\s*['\"](.+?)['\"]|(\w+)\s*=\s*(\[.*\])|(\w+)\s*=\s*(\w+)"
        param_dict = {}
        for m in re.finditer(param_pattern, params):
            if m.group(1):
                param_dict[m.group(1)] = m.group(2)
            elif m.group(3):
                param_dict[m.group(3)] = m.group(4)
            elif m.group(5):
                param_dict[m.group(5)] = m.group(6)
        return api_name, param_dict
    
    
        

class TooleyesLoader(BasicLoader):
    def __init__(self, args) -> None:
        self.args = args
        self.apis_dir = self.args.apis_dir # /public/home/wlchen/hhan/my-tool-learning/Open-Tool-Learning/src/otl/tooleyes/Tool_Library
        self.executable_tools = dict()
        self.load_executable_tools()
        
    
    def load_executable_tools(self): #Tooleyes需要进行同名API排查
   
        for sub_path in os.listdir(self.apis_dir):
            
            for sub_sub_path in os.listdir(self.apis_dir + "/" + sub_path):
            
                file_path = self.apis_dir + "/" + sub_path + "/" + sub_sub_path + "/config_gpt4.json"
                callable_path = self.apis_dir + "/" + sub_path + "/" + sub_sub_path + "/tool.py"
                with open(file_path, 'r') as file:
                    tools = json.load(file)

                for tool in tools:
                    name = tool["name"]
                    if name not in ["ask_to_user", "finish"]:
                        cls_info = {
                            'source': "Tooleyes",
                            'name': name,
                            'description': tool["description"],
                            'input_parameters': tool["parameters"]["properties"],
                            'output_parameters': "UNK",
                            'callable': True,
                            "required" : tool["parameters"]["required"],
                            'remote': "UNK",
                            "callable_path": callable_path
                        }
                    if name not in self.executable_tools:
                        self.executable_tools[name] = [SysTool(**cls_info)]
                    else:
                        self.executable_tools[name].append(SysTool(**cls_info))
    
    
    def get_executable_tools(self):
        return self.executable_tools
    
    def test(self): #仅供调用示例
        
        test_sample = {
        "id": "Turn 1: I'm in need of assistance in generating a random string with a length of 8,please give me one.",
        "conversations": [
            {
                "from": "system",
                "value": "the prompt of conversation"
            },
            {
                "from": "user",
                "value": "I'm in need of assistance in generating a random string with a length of 8,please give me one."
            }
        ],
        "path": "ToolEyes/Tool_Library/Random/Random",
        "scenario": "TG"
        }
        
        api_name = ""
        input_parameters = {}
        path_in_dataset = test_sample["path"].replace("ToolEyes/", "")
        
        import_path = "dependency/tooleyes/" + path_in_dataset
        
        
        if api_name not in self.executable_tools:
            raise Exception('Tool is not within the scope of executable tools')
        else:
            for api in self.executable_tools[api_name]:
                callable_path = api.callable_path
                if re.search(path_in_dataset, callable_path):
                    d = {"action": api_name, "action_input": input_parameters, "path": import_path}
                    result = api(**d)
                    return result
    
    
    
    def react_parser(self, message): #是不是应该专门建一个Tooleyes的文件夹放utils.py里?

        thought_pattern = re.compile("Thought:.*?Action:", re.DOTALL)
        action_pattern = re.compile("Action:\s*([\w_]+)", re.DOTALL)
        action_input_pattern = re.compile("Action Input:\s*({.*?})\s*", re.DOTALL)
        try:
            thought_content = thought_pattern.search(
                message).group().replace("Action:", "")
        except:
            thought_content = 'Thought: \n'
        try:
            action_content = action_pattern.search(
                message).group().replace("Action Input:", "")
        except:
            action_content = 'Action: \n'
        try:
            action_input_content = action_input_pattern.search(message).group()
            action_input_content = action_input_content.replace("\n ", "").replace("\n", "")    
        except:
            action_input_content = 'Action Input: {}'
        return thought_content, action_content, action_input_content
        


class TooltalkLoader(BasicLoader):
    def __init__(self, args) -> None:
        self.args = args
        self.init_database_dir = self.args.init_database_dir
        self.ignore_list = self.args.ignore_list if self.args.ignore_list is not None else list()
        self.account_database = self.args.account_database if self.args.account_database is not None else ACCOUNT_DB_NAME
        self.databases = dict()
        self.database_files = dict()
        self.session_token = None
        self.inited_tools = dict() 
        self.now_timestamp = None
        self.apis = {api.__name__: api for api in ALL_APIS if api.__name__ not in self.ignore_list}
        self.executable_tools = dict() #the dict for SysTool class
        
        for file_name, file_path in self.get_names_and_paths(self.init_database_dir):
            database_name, ext = os.path.splitext(file_name)
            if ext == ".json":
                self.database_files[database_name] = file_path
                with open(file_path, 'r', encoding='utf-8') as reader:
                    self.databases[database_name] = json.load(reader)
        if self.account_database not in self.databases:
            raise ValueError(f"Account database {self.account_database} not found")
        
        self.load_executable_tools()


    def load_executable_tools(self):
        
        for key, value in self.apis.items():
            self.get_init_tool(key)
            
        for api_name, cls in self.apis.items():
            description = cls.description
            input_parameters = {}
            output_parameters = cls.output
            required = []
            for k, v in cls.parameters.items():
                if v["required"]:
                    required.append(k)
                del v["required"]
                input_parameters[k] = v
            cls_info = {
                    'source': "Tooltalk",
                    'name': api_name,
                    'class': cls,
                    'description': description,
                    'input_parameters': input_parameters,
                    'output_parameters': output_parameters,
                    'callable': True,
                    'remote': "UNK",
                    'required': required,
                }
            if hasattr(cls, 'database_name') and cls.database_name in self.databases:
                cls_info['database'] = self.databases[cls.database_name]
            
            self.executable_tools[api_name] = SysTool(**cls_info)
            

    def get_init_tool(self, tool_name: str):
        # if tool_name in self.inited_tools:
        #     return self.inited_tools[tool_name]
        cls = self.apis[tool_name]
        account_db = self.databases.get(self.account_database)
        if cls.database_name is not None:
            database = self.databases.get(cls.database_name)
            tool = cls(
                account_database=account_db,
                now_timestamp=self.now_timestamp,
                api_database=database,
            )
        else:
            tool = cls(
                account_database=account_db,
                now_timestamp=self.now_timestamp,
            )

        self.inited_tools[tool_name] = tool
        return tool
    
    def get_executable_tools(self):
        return self.executable_tools, self.inited_tools
    
    def get_names_and_paths(self, input_path):
        if os.path.isdir(input_path):
            files = os.listdir(input_path)
            file_paths = [os.path.join(input_path, name) for name in files]
            file_names_and_paths = [(name, path) for name, path in zip(files, file_paths)]
            return file_names_and_paths
        elif os.path.isfile(input_path):
            return [(os.path.basename(input_path), input_path)]
        else:
            raise ValueError(f"Unknown input path: {input_path}")
    
    def test(self): #仅供调用示例
        api_name = "QueryUser"
        param_dict = {"usename": "justinkool", "email": "justintime@fmail.com"}
        request = {
            "api_name":  api_name,
            "parameters":  param_dict
        }
        if api_name not in self.apis:
            response = {
                "response": None,
                "exception": f"API {api_name} not found"
            }
            return request, response
        if api_name not in self.executable_tools:
            response = {
                "response": None,
                "exception": f"Tool is not excutable"
            }
            return request, response

        tool_module = self.inited_tools[api_name]
        t = self.executable_tools[api_name]
        
        # #Tooltalk本身包含的一些session_token, login, 后续还需要考虑metadata
        # if tool_module.requires_auth:
        #     if self.session_token is None:
        #         response = {
        #             "response": None,
        #             "exception": "User is not logged in"
        #         }
        #         return request, response
        #     param_dict["session_token"] = self.session_token
        # if api_name in [UserLogin.__name__, RegisterUser.__name__] and self.session_token is not None:
        #     username = tool_module.check_session_token(self.session_token)["username"]
        #     response = {
        #         "response": None,
        #         "exception": f"Only one user can be logged in at a time. Current user is {username}.",
        #     }
        #     return request, response
 
        d = {"module":  tool_module, "param_dict": param_dict}
        result = t(**d)
        return result
                      

if __name__ == "__main__":
    pass