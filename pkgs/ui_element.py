# defind UI_Element class 
import os
from pkgs.prompts import generate_element_content_desc_tmpl
from control_phone import tap, input_text, swipe
from pkgs.utils import requests_openai
import requests
import json 
import copy

class UIElement:
    def __init__(
            self, 
            image, # base64 image
            id,
            android_class,
            resource_id,
            text,
            content_desc,
            bound, 
            actions):
        self.id = id
        self.image = image
        self.android_class = android_class
        self.resource_id = resource_id  # for accessibility
        self.text = text
        self.content_desc = content_desc
        self.bound = bound
        self.actions = actions

    def generate_content_desc(self, llm_executor):
        user_input = copy.deepcopy(generate_element_content_desc_tmpl["user_input"])
        user_input.append(f"android_class,resource_id,text,content_desc\n{self.android_class},{self.resource_id},{self.text},{self.content_desc}")
        response = llm_executor.execute_with_image(generate_element_content_desc_tmpl["model_input"], user_input, self.image)
        print(response)
        self.content_desc = response

    def center(self): 
        center_x = int(self.bound[0]) + int(self.bound[2] - self.bound[0]) / 2
        center_y = int(self.bound[1]) + int(self.bound[3] - self.bound[1]) / 2
        return center_x, center_y

    def execute_action(self, action, data):
        center_x = int(self.bound[0]) + int(self.bound[2] - self.bound[0]) / 2
        center_y = int(self.bound[1]) + int(self.bound[3] - self.bound[1]) / 2

        if action == "tap" or action == "select" or action == "click":
            tap(
                center_x,
                center_y
            )
            print("done tap")

        if action == "input":
            tap(
                center_x,
                center_y
            )            
            input_text(data)
            print("done input " + data)
    

        if action == "swipe_up":
            swipe(center_x, center_y, center_x, center_y * 0.5)   
            print("done swipe up")

        if action == "swipe_down":
            swipe(center_x, center_y, center_x, center_y * 1.5)   
            print("done swipe down")

        if action == "swipe_right":
            swipe(center_x, center_y, center_x * 1.5, center_y)   
            print("done swipe right")

        if action == "swipe_left":
            swipe(center_x, center_y, center_x * 0.5, center_y)   
            print("done swipe left")

        return
    
