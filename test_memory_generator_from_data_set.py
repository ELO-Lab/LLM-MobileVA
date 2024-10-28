from dotenv import load_dotenv
from pkgs import LangChainExecutor
from pkgs.memory_generator_from_data_set import MemoryGenerator
import os

if __name__ == "__main__":
    load_dotenv()
    llm_executor = LangChainExecutor(os.getenv("LLM_MODEL"))
    memory_generator = MemoryGenerator(llm_executor)
    package_name = input("Package name: ")
    request = input("Request: ")
    # "com.ss.android.ugc.trill"
    # com.gsm.customer
    # com.ubercab
    memory_generator.generate_memory(package_name, request)
