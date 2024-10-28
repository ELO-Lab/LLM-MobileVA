from control_phone import open_app, close_app, take_screenshot, dump_ui, input_text
from pkgs.prompts import query_similar_flows_tmpl
from pkgs.prompts import identifying_next_execute_action_tmpl
from pkgs.prompts import identifying_next_execute_action_with_only_user_guide_tmpl
from pkgs.prompts import identifying_next_execute_action_with_only_similar_flow_tmpl
from pkgs.prompts import indentifying_next_execute_action_with_only_current_screen_tmpl
import jsonpickle
import os
import json 
import copy 
import time
from pkgs.utils import requests_openai
from pkgs.screen import Screen 

def similar_flows_to_json(similar_flows, remove_user_guide=False):
    json_flows = []
    for flow in similar_flows:
        json_flow = {
            "flow description": flow.flow_desc,
            "steps": [] 
        }
        for screen in flow.screens:
            json_flow["steps"].append(screen.get_data_for_flow_desc(remove_user_guide) + "\n")
        json_flows.append(json_flow)
    rs = json.dumps(json_flows)
    print(rs)
    return rs

def user_guides_from_flows(similar_flows):
    user_guildes = []  
    for flow in similar_flows:
        flow_guide = []
        for screen in flow.screens:
            flow_guide.append(screen.user_guide)
        user_guildes.append(flow_guide)
    rs = json.dumps(user_guildes)
    return rs 

class Executor:
    def __init__(self, llm_executor, with_memory=True, with_user_guide=True):
        self.llm_executor = llm_executor
        self.with_memory = with_memory
        self.with_user_guide = with_user_guide
        return

    def query_app_flows(self, app_package):
        flows_dir = f"data/flows/{app_package}"
        flows = []
        if not os.path.exists(flows_dir):
            return flows
        for flow_file in os.listdir(flows_dir):
            with open(f"{flows_dir}/{flow_file}") as f:
                data = f.read()
                flow = jsonpickle.decode(data)
                flow.id = flow_file.split(".")[0]
                flows.append(flow)
        return flows 

    def query_simular_flow_ids(self, request, flows):
        user_input = copy.deepcopy(query_similar_flows_tmpl["user_input"])
        user_input.append("### Request:\n" + request)
        flows_input =  "### Flows:\n"
        for flow in flows:
            flow_desc = flow.flow_desc.replace(",", " ").replace("\n", ".")
            flows_input += f"{flow_desc},{flow.user_request}\n"
        user_input.append(flows_input)
        response = self.llm_executor.execute(query_similar_flows_tmpl["model_input"], user_input)
        if response == "":
            return []
        flow_indexs = response.strip().split(",") 
        if flow_indexs[0] == "-1":
            return []
        # remove invalid indexs
        flow_indexs = [flow_index for flow_index in flow_indexs if int(flow_index) < len(flows)]
        similar_flows = [flows[int(index)] for index in flow_indexs]
        similar_flow_ids = [flow.id for flow in similar_flows]
        return similar_flow_ids

    def query_flow_by_ids(self, flow_ids, app_package):
        flows_dir = f"data/flows/{app_package}"
        flows = []
        if not os.path.exists(flows_dir):
            return flows
        for flows_id in flow_ids:
            with open(f"{flows_dir}/{flows_id}.json") as f:
                data = f.read()
                flow = jsonpickle.decode(data)
                flow.id = flows_id
                flows.append(flow)
        return flows 

    def get_next_action(self, request, similar_flows, current_screen, previous_action):
        response = ""
        if self.with_memory:
            if self.with_user_guide:
                json_flows = similar_flows_to_json(similar_flows)
                user_input = copy.deepcopy(identifying_next_execute_action_tmpl["user_input"])
                user_input.append("### Request:\n" + request)
                user_input.append("### Current UI Elements:\n" + current_screen.get_csv_elements())
                user_input.append("### Previous Actions:\n" + previous_action)
                user_input.append("### Similar flow guide:\n" + json_flows)
                response = self.llm_executor.execute(identifying_next_execute_action_tmpl["model_input"], user_input)
            else:
                json_flows = similar_flows_to_json(similar_flows, True)
                user_input = copy.deepcopy(identifying_next_execute_action_with_only_similar_flow_tmpl["user_input"])
                user_input.append("### Request:\n" + request)
                user_input.append("### Current UI Elements:\n" + current_screen.get_csv_elements())
                user_input.append("### Previous Actions:\n" + previous_action)
                user_input.append("### Similar flow guide:\n" + json_flows)
                response = self.llm_executor.execute(identifying_next_execute_action_with_only_similar_flow_tmpl["model_input"], user_input)
        else:
            if self.with_user_guide:
                json_user_guides = user_guides_from_flows(similar_flows)
                user_input = copy.deepcopy(identifying_next_execute_action_with_only_user_guide_tmpl["user_input"])
                user_input.append("### Request:\n" + request)
                user_input.append("### Current UI Elements:\n" + current_screen.get_csv_elements())
                user_input.append("### Previous Actions:\n" + previous_action)
                user_input.append("### User guide:\n" + json_user_guides)
                response = self.llm_executor.execute(identifying_next_execute_action_with_only_user_guide_tmpl["model_input"], user_input)
            else:
                user_input = copy.deepcopy(indentifying_next_execute_action_with_only_current_screen_tmpl["user_input"])
                user_input.append("### Request:\n" + request)
                user_input.append("### Current UI Elements:\n" + current_screen.get_csv_elements())
                user_input.append("### Previous Actions:\n" + previous_action)
                response = self.llm_executor.execute(indentifying_next_execute_action_with_only_current_screen_tmpl["model_input"], user_input)

        response = json.loads(response)    

        element_index = int(response["index"])
        action = response["action"]
        if action == "click" or action == "touch":
            action = "tap"

        completed = response["completed"]
        additional_data = response["additional_data"]
        if completed == "True" or completed == "true" or completed == "TRUE" or completed == "1" or completed == 1 or action == "return":
            completed = True

        return element_index, action, completed, additional_data
