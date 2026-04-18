import sys
from agents.curator_agent import run_agent

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py \"<tema da notícia>\"")
        sys.exit(1)
    run_agent(sys.argv[1])