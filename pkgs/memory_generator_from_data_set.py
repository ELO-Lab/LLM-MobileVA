from control_phone import open_app, close_app, take_screenshot, dump_ui, input_text
from pkgs.utils import encode_image
from pkgs.ui_dump_parser import interactable_classes, extract_interactable_elements_by_class, generete_elements
from pkgs.prompts import identifying_next_memory_generate_action_tmpl
from pkgs.screen import Screen
from pkgs.flow import Flow
import base64
import os 
import time 
import json
import jsonpickle
import uuid
import copy

class MemoryGenerator:
    # generate memory will create memory step to complete a app flow
    def generate_memory(
        self,
        app_package,
        request
    ):
        # close app if open
        close_app(app_package)
        # open app
        open_app(app_package)
        previous_action = "content_desc,action,data"
        screens = [] 
        
        while True:
            user_input = input("Is flow completed(y/n): ")
            if user_input == "y":
                # TODO: save flow 
                break
            if user_input != "n":
                print("Invalid input")
                continue

            while True:
                try:
                    dataset_path = input("path json file of the current screen: ")
                    dataset_path = fr"{dataset_path}"
                    with open(dataset_path, "r") as f:
                        json_data = f.read()                    
                    break
                except FileNotFoundError:
                    print("Invalid path")
                    continue

            # Read Screen from dataset
            screen: Screen = jsonpickle.decode(json_data)
            user_guide = input("Guide to complete current step: ")
            element_index, action, additional_data = self.get_next_memory_generate_action(
                request, 
                screen,
                user_guide, 
                previous_action
            )            
            element_index = int(element_index)
            data = ""
            if action == "input":
                data = input(f"Need Input: {additional_data}\n")
            if action == "answer":
                print(f"Answer from VA: {additional_data}")

            previous_action = previous_action + f"{screen.ui_elements[element_index].content_desc},{action},{data}"            
            screen.execute_action(element_index, action, data)
            screens.append(screen)
        
        save_flow = input("Save flow(y/n): ")
        if save_flow == "y":
            # save memory to file
            flow = Flow(app_package, request, screens)
            os.makedirs(f"data/flows/{app_package}", exist_ok=True)
            flow_id = str(uuid.uuid4())
            save_path = f"data/flows/{app_package}/{flow_id}.json"
            with open(save_path, "w") as f:
                f.write(jsonpickle.encode(flow))
                print(f"Flow saved to file: {save_path}")
        
        return

    def __init__(self, llm_executor):
        self.llm_executor = llm_executor
        return
    

    def get_next_memory_generate_action(
            self, 
            request, 
            current_screen,
            user_guide, 
            previous_action
        ):
        current_screen.user_guide = user_guide
        user_input = copy.deepcopy(identifying_next_memory_generate_action_tmpl["user_input"])
        user_input.append("### Request:\n" + request)
        user_input.append("### Current UI Elements:\n" + current_screen.get_csv_elements())
        user_input.append("### User's Guide:\n" + user_guide)
        user_input.append("### Previous Actions:\n" + previous_action)
        
        response = self.llm_executor.execute(identifying_next_memory_generate_action_tmpl["model_input"], user_input)
        response = json.loads(response)    

        element_index = response["index"]  
        action = response["action"]
        additional_data = response["additional_data"]

        return element_index, action, additional_data
