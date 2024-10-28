from dotenv import load_dotenv
from pkgs import MemoryGenerator, LangChainExecutor 
import os

if __name__ == "__main__":
    load_dotenv()
    llm_executor = LangChainExecutor(os.getenv("LLM_MODEL"))
    memory_generator = MemoryGenerator(llm_executor)
    package_name = input("Package name: ")
    request = input("Request: ")
    # "com.ss.android.ugc.trill"
    # com.gsm.customer
    memory_generator.generate_memory(package_name, request)
