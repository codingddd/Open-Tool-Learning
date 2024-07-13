from .ChatGPT import ChatGPT
from .ChatGLM import ChatGLM
from .MOSS import MOSS
from .ChatYuan import ChatYuan
from .CPM_Bee import CPM_Bee
from .LLaMA import LLaMA
from .LLaMA_LoRA import LLaMA_LoRA
from .Baichuan import Baichuan
from .InternLM import InternLM
from .Qwen import Qwen
from .Mistral import Mistral

__all__ = [
    "Auto_Model",
    "ChatGPT",
    "ChatGLM",
    "MOSS",
    "ChatYuan",
    "CPM_Bee",
    "LLaMA",
    "LLaMA_LoRA",
    "Baichuan",
    "InternLM",
    "Qwen",
    "Mistral"
]

def Auto_Model(model_name,model_path,distribute=False):
    match model_name:
        case "ChatGLM":
            return ChatGLM(model_path,distribute=distribute)
        case "MOSS":
            return MOSS(model_path)
        case "ChatYuan":
            return ChatYuan(model_path)
        case "CPM_Bee":
            return CPM_Bee(model_path)
        case "LLaMA":
            return LLaMA(model_path)
        case "LLaMA_LoRA":
            return LLaMA_LoRA(model_path)
        case "Baichuan":
            return Baichuan(model_path)
        case "InternLM":
            return InternLM(model_path)
        case "Qwen":
            return Qwen(model_path)
        case "Mistral":
            return Mistral(model_path)