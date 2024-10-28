from time import time, sleep
from xml.etree.ElementTree import indent
from pkgs import Executor, screen_from_api_data, LangChainExecutor
import sys
import argparse
import os
from dotenv import load_dotenv
import jsonpickle

parser = argparse.ArgumentParser()

parser.add_argument("-d", "--dataset", help="Dataset folder")
parser.add_argument("-f", "--flows", help="Flows folder")
parser.add_argument("-u", "--no-user_guide", help="Include user guide", type=bool, default=False)
parser.add_argument("-m", "--no-memory", help="Include memory", type=bool, default=False)
parser.add_argument("-c", "--no-cache", help="Load cached screen", type=bool, default=False)

args = parser.parse_args()

load_dotenv()
model_name = os.getenv("LLM_MODEL")
# llm_executor = NewLLMExecutor(model_name)
llm_executor = LangChainExecutor(model_name)

executor = Executor(llm_executor, not args.no_user_guide, not args.no_memory)

def load_data_set(dataset_folder):
    apps = {} 
    for app in os.listdir(dataset_folder):
        app_folder = os.path.join(dataset_folder, app)
        if os.path.isdir(app_folder):
            app_flows = []
            for flow_name in os.listdir(app_folder):
                flow_folder = os.path.join(app_folder, flow_name)
                if os.path.isdir(flow_folder):
                    lines = []
                    with open(flow_folder + "/info.txt", 'r') as file:
                       for line in file:
                            lines.append(line.strip())
                    flow = {
                        "request": lines[0],
                        "path": flow_folder, 
                        "actions": lines[1:],
                    }
                    app_flows.append(flow)
            apps[app] = app_flows
    return apps

def evaluate_actions(apps):
    results = {}
    trace = {}
    for app, flows in apps.items():
        results[app] = {
            "total_action": 0,
            "total_correct_action": 0,
            "total_tap_action": 0,
            "total_correct_tap_action": 0,
            "total_input_action": 0,
            "total_correct_input_action": 0,
            "total_swipe_action": 0,
            "total_correct_swipe_action": 0,
            "total_sucessful_flows": 0,
            "total_flows": 0,

            "incorrect_actions": [],
            "flows":[]
        }
        trace[app] = [] 
        for flow in flows:
            results[app]["total_flows"] += 1
            success = True
            request = flow["request"]
            app_flows = executor.query_app_flows(app)
            similar_flows_id = executor.query_simular_flow_ids(request, app_flows)
            similar_flows = executor.query_flow_by_ids(similar_flows_id, app)
            previous_action = "content_desc,action,data\n" 
            trace_flow = {
                "request": request,
                "actions": []
            }
            for action in flow["actions"]:
                action_data = action.split(",")
                if not args.no_cache and os.path.exists(flow["path"] + f"/screen_{action_data[0]}.json"):
                    with open(flow["path"] + f"/screen_{action_data[0]}.json", "r") as f:
                        screen = jsonpickle.decode(f.read())
                else:
                    screen = screen_from_api_data(
                        app,
                        flow["path"] + f"/screen_{action_data[0]}.png", 
                        flow["path"] + f"/window_dump_{action_data[0]}.xml", 
                        llm_executor )
                try:
                    element_index, next_action, completed, additional_data = executor.get_next_action(request, similar_flows, screen, previous_action)
                except Exception as e:
                    # some flows are deny by llm policy
                    # so we skip them
                    print(e)
                    print(f"Error: {app}, {flow['path']}, {action}")
                    continue
                element_index = int(element_index)
                if element_index < 0:
                    previous_action += f"screen,{next_action},screen\n"
                else:
                    previous_action += f"{screen.ui_elements[element_index].content_desc},{next_action},{screen.ui_elements[element_index].text}\n"
                print(request, screen.ui_elements[element_index].id, next_action, completed)
                results[app]["total_action"] += 1

                if action_data[1] == "tap":
                    results[app]["total_tap_action"] += 1
                if action_data[1] == "input":
                    results[app]["total_input_action"] += 1
                if action_data[1] == "swipe_up" or action_data[1] == "swipe_down" or action_data[1] == "swipe_left" or action_data[1] == "swipe_right":
                    results[app]["total_swipe_action"] += 1
                 
                if element_index < 0:
                    element_id = "screen"
                else:
                    element_id = screen.ui_elements[element_index].id
                
                if element_id == action_data[2]  and next_action == action_data[1]:
                    results[app]["total_correct_action"] += 1
                    if next_action == "tap":
                        results[app]["total_correct_tap_action"] += 1
                    if next_action == "input":
                        results[app]["total_correct_input_action"] += 1
                    if next_action == "swipe_up" or next_action == "swipe_down" or next_action == "swipe_left" or next_action == "swipe_right":
                        results[app]["total_correct_swipe_action"] += 1
                else:
                    success = False
                    results[app]["incorrect_actions"].append({
                        "request": request,
                        "element_id": screen.ui_elements[element_index].id,
                        "action": next_action,
                        "expected_action": action_data[1],
                        "expected_element_id": action_data[2],
                    })
                trace_flow["actions"].append({
                    "grouth_truth": action,
                    "screen": screen,
                    "element_index": element_index, 
                    "action": next_action, 
                    "completed": completed
                })
                if "gemini" in os.environ.get("LLM_MODEL"):
                    # wait for gemini to reset
                    sleep(5)


            trace[app].append(trace_flow)
            if success:
                results[app]["total_sucessful_flows"] += 1
    
    rs_file_name = f"{model_name}"
    if args.no_user_guide:
        rs_file_name += "_no_user_guide"
    if args.no_memory:
        rs_file_name += "_no_memory"
    # save trace
    save_path = f"./evaluate_result/trace_{rs_file_name}.json"
    with open(save_path, "w") as f:
        f.write(jsonpickle.encode(trace, indent=4))
        print(f"Result saved to file: {save_path}")
    # save result 
    save_path = f"./evaluate_result/result_{rs_file_name}.json"
    with open(save_path, "w") as f:
        f.write(jsonpickle.encode(results, indent=4))
        print(f"Result saved to file: {save_path}")

    print(results)
    
def main():
    print(args)
    apps = load_data_set(args.dataset)
    evaluate_actions(apps)

if __name__ == "__main__":
    main()
