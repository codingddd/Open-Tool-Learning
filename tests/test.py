import sys
sys.dont_write_bytecode = True

import toolagent  # noqa: E402, F401
from toolagent.agents import Agent  # noqa: E402


if __name__ == "__main__":
    agent = Agent()

    checkpoint_path = "..."
    agent.load_llm("LLaMA", checkpoint_path)
    agent.load_module()

    
