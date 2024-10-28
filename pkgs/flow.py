from pkgs.prompts import generate_flow_desc_tmpl
from pkgs.screen import Screen
from pkgs.ui_element import UIElement
from pkgs.llm_executor import LangChainExecutor
from typing import List
import os 
import copy
import requests
import json
import base64

class Flow:
    def __init__(self, app_package="", user_request="", screens=None, empty_data =False):
        if empty_data:
            return
        self.app_package = app_package
        self.user_request = user_request
        self.screens = screens
        self.generate_desc()
        return

    def generate_desc(self):
        # send screen_shot_file to LLM to analyze the screen
        llm_executor = LangChainExecutor(os.getenv("LLM_MODEL"))
        user_input = copy.deepcopy(generate_flow_desc_tmpl["user_input"])
        user_input.append(f"### Request:\n {self.user_request}")
        step_data = "### Step:\nscreen_desc,user_guide,element_content_desc,action\n"
        for screen in self.screens:
            step_data += screen.get_data_for_flow_desc() + "\n"
        user_input.append(step_data)
        response = llm_executor.execute(generate_flow_desc_tmpl["model_input"], user_input)
        print(response)
        self.content_desc = response
    
    @staticmethod
    def load_flows_json(json_data: json) -> List['Flow']:
        flows = []       
        for flow_data in json_data:
            screens = []            
            for screen_data in flow_data['screens']:
                ui_elements = [
                    UIElement(
                        image=element_data['image'],
                        id=element_data['id'],
                        android_class=element_data['android_class'],
                        resource_id=element_data['resource_id'],
                        text=element_data['text'],
                        content_desc=element_data['content_desc'],
                        bound=element_data['bound'],
                        actions=element_data['actions']
                    ) for element_data in screen_data['ui_elements']
                ]
                screen = Screen(empty_data=True)
                screen.app_package = screen_data['app_package']
                screen.uuid = screen_data['uuid']
                screen.ui_data = screen_data['ui_data']
                screen.screen_shot = base64.b64decode(screen_data['screen_shot']) if screen_data['screen_shot'] else None
                screen.screen_desc = screen_data['screen_desc']
                screen.user_guide = screen_data['user_guide']
                screen.execute_element_index = screen_data['execute_element_index']
                screen.execute_action = screen_data['execute_action']
                screen.ui_elements = ui_elements
                screens.append(screen)
            
            flow = Flow(empty_data=True)
            flow.app_package = flow_data['app_package']
            flow.user_request = flow_data['user_request']
            flow.screens = flow_data['screens']
            flow.flow_desc = flow_data['flow_desc']
            flows.append(flow)
        
        return flows
