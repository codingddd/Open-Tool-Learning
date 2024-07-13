from __future__ import annotations


class FoundationLanguageModel:
    model_name: str
    def __init__(self) -> None:
        self.model_name

    def __call__(self):
        raise NotImplementedError


class LocalLanguageModel(FoundationLanguageModel):
    def __init__(self) -> None:
        self.tokenizer
        self.llm


class RemoteLanguageModel(FoundationLanguageModel):
    pass