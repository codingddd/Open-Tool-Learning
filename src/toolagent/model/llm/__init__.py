from .LLaMA import LLaMA

__all__ = [
    "LLaMA"
]

def AutoModel(model_name, *args, **kwargs):
    match model_name:
        case "LLaMA":
            return LLaMA(*args, **kwargs)