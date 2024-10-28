from pkgs.prompts import identify_app_tmpl
from pkgs.utils import requests_openai
import copy
import json

available_apps = "Tiktok, Amazon, Youtube, XanhSM, Facebook, Uber, DoorDash, Telegram"

class AppIdentifier:
    def __init__(self, llm_executor):
        self.llm_executor = llm_executor
        return
    
    # generate memory will create memory step to complete a app flow
    def identify_app(
        self,
        request,
    ):
        user_input = copy.deepcopy(identify_app_tmpl["user_input"])
        user_input.append(f"App list: {available_apps}")
        user_input.append(f"Request: {request}")
        print(user_input)
        response = self.llm_executor.execute(identify_app_tmpl["model_input"], user_input)
        response = json.loads(response)    
        return response
