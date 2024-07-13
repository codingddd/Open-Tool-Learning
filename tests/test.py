import sys
sys.dont_write_bytecode = True

import otl
from otl.agents import Agent


if __name__ == "__main__":
    agent = Agent()

    checkpoint_path = "..."
    agent.load_llm("LLaMA", checkpoint_path)
    agent.load_module()

    
