# defind screen class 
from control_phone import  take_screenshot, dump_ui, input_text, swipe, get_screen_size
from pkgs.prompts import  generate_screen_desc_tmpl
from pkgs.utils import requests_openai
from pkgs.ui_element import UIElement
from pkgs.ui_dump_parser import interactable_classes, extract_interactable_elements_by_class, generete_elements
import base64
import concurrent.futures
import copy
import json
import re
import requests
import time
import uuid
import os 

def screen_from_api_data(app_package, img_file, ui_file, llm_executor):
    screen = Screen("", True)
    screen.screen_from_api_data(app_package, img_file, ui_file, llm_executor)
    return screen

class Screen:
    def __init__(
        self, 
        app_package="",
        empty_data = False,
        llm_executor=None
    ):
        if empty_data:
            return
        self.app_package = app_package
        self.uuid = str(uuid.uuid4())
        os.makedirs("data", exist_ok=True)
        self.img_file = f"data/screen_{self.uuid}.png"
        self.ui_file = f"data/window_dump_{self.uuid}.xml"
        take_screenshot(self.img_file)
        self.ui_data = dump_ui(self.ui_file)
        self.llm_executor = llm_executor
        csv_elements = extract_interactable_elements_by_class(self.ui_file, interactable_classes)
        elements = generete_elements(self.img_file, csv_elements)

        self.screen_shot = base64.b64encode(open(self.img_file, "rb").read()).decode('utf-8')
        # Use ThreadPoolExecutor to run the tasks in parallel
        with concurrent.futures.ThreadPoolExecutor(20) as executor:
            futures = [executor.submit(element.generate_content_desc, llm_executor) for element in elements]
            screen_desc_futures = [executor.submit(self.generate_desc)]
            futures += screen_desc_futures
            # Optional: wait for all futures to complete and handle exceptions
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()  # This will raise any exceptions caught during execution
                except Exception as e:
                    print(f"An error occurred: {e}")
        
        self.ui_elements: list[UIElement] = elements

    def get_csv_elements(self):
        csv_elements = "index,android_class,resource_id, text,content_desc,x1,y1,x2,y2\n"
        for index, element in enumerate(self.ui_elements): 
            csv_elements += f"{index},{element.android_class},{element.resource_id},{element.text},{element.content_desc},{element.bound[0]},{element.bound[1]},{element.bound[2]},{element.bound[3]}\n"
        return csv_elements

    def execute_action(self, element_index, action, data): 
        self.execute_element_index = element_index
        self.execute_action = action
        if element_index < 0:
            self.execute_actions(action)
            return
        element = self.ui_elements[element_index]
        element.execute_action(action, data)

    def execute_actions(self, action):
        w, h = get_screen_size()
        center_x = w / 2
        center_y = h / 2

        if action == "swipe_up":
            swipe(center_x, center_y, center_x, 0)   
            print("done swipe up")
        if action == "swipe_down":
            swipe(center_x, center_y, center_x, h)   
            print("done swipe down")
        if action == "swipe_right":
            swipe(center_x, center_y, w, center_y)   
            print("done swipe right")
        if action == "swipe_left":
            swipe(center_x, center_y, 0, center_y)   
            print("done swipe left")

    def save_to_db(self):
        # TODO
        return

    def generate_desc(self):
        # send screen_shot_file to LLM to analyze the screen
        user_input = copy.deepcopy(generate_screen_desc_tmpl["user_input"])
        response = self.llm_executor.execute_with_image(generate_screen_desc_tmpl["model_input"], user_input, self.screen_shot)
        self.screen_desc = response

    def get_data_for_flow_desc(self, remove_user_guide=False):
        execute_element_desc = "execute on screen"
        if self.execute_element_index >= 0:
            execute_element_desc = self.ui_elements[self.execute_element_index].content_desc

        if remove_user_guide:
            return f"{self.screen_desc},{execute_element_desc},{self.execute_action}"
        return f"{self.screen_desc},{self.user_guide},{execute_element_desc},{self.execute_action}"

    def generate_element_content_desc(self, element):
        element.generate_content_desc(self.llm_executor)

    def screen_from_api_data(self, app_package, img_file, ui_file, llm_executor):
        self.app_package = app_package
        self.img_file = img_file
        self.ui_file = ui_file 
        self.llm_executor = llm_executor
        csv_elements = extract_interactable_elements_by_class(self.ui_file, interactable_classes)
        elements = generete_elements(self.img_file, csv_elements)

        self.screen_shot = base64.b64encode(open(self.img_file, "rb").read()).decode('utf-8')
        # Use ThreadPoolExecutor to run the tasks in parallel
        with concurrent.futures.ThreadPoolExecutor(10) as executor:
            futures = [executor.submit(element.generate_content_desc, llm_executor) for element in elements]
            screen_desc_futures = [executor.submit(self.generate_desc)]
            futures += screen_desc_futures
            # Optional: wait for all futures to complete and handle exceptions
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()  # This will raise any exceptions caught during execution
                except Exception as e:
                    print(f"An error occurred: {e}")
        
        self.ui_elements: list[UIElement] = elements

    def get_element_center(self, element_index):
        if element_index < 0:
            return 0, 0
        element = self.ui_elements[element_index]
        return element.center() 
