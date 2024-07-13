from typing import List

from transformers import AutoTokenizer, AutoModelForCausalLM

from ...model._prototype import LocalLanguageModel

class LLaMA(LocalLanguageModel):
    def __init__(self, checkpoint_path: str) -> None:
        self.model_name = 'LLaMA'

        self.checkpoint_path = checkpoint_path

        self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint_path, trust_remote_code=True)
        self.llm = AutoModelForCausalLM.from_pretrained(self.checkpoint_path, trust_remote_code=True, device_map="auto") # torch_dtype=torch.bfloat16,
        self.llm.eval()
        self.history = []


    def __call__(self, 
                 input_text: str, 
                 max_new_length: int=256) -> str:
        inputs = self.tokenizer(input_text, return_tensors="pt")
        try:
            generate_ids = self.llm.generate(inputs.input_ids.cuda(), max_new_tokens=max_new_length)
        except:
            pass
        outputs = self.tokenizer.decode(generate_ids[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True)
        return outputs