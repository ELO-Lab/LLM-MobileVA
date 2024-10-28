from pkgs import GeminiExecutor, OpenAiExecutor
from pkgs.prompts import identify_app_tmpl
import os
import copy
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
    gemini_executor = GeminiExecutor(os.getenv("GEMINI_API_KEY"), "gemini-1.5-flash")
    user_input = copy.deepcopy(identify_app_tmpl["user_input"])
    user_input.append("Available app: Tiktok, Shoppe, Youtube, XanhSM, Facebook")
    user_input.append("Request: I want to watch a video.")
    rs = gemini_executor.execute(identify_app_tmpl["model_input"], user_input)
    print(rs)

    openai_executor = OpenAiExecutor(os.getenv("OPEN_AI_API_KEY"), "gpt-4o-mini")
    rs = openai_executor.execute(identify_app_tmpl["model_input"], user_input)
    print(rs)

