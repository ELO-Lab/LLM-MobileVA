from pkgs import Executor 
from dotenv import load_dotenv
from control_phone import swipe_up, swipe_down, swipe_left, swipe_right, open_app
from control_phone import take_screenshot, dump_ui, input_text, tap
import requests
import os
import time
load_dotenv()

map_app_name_to_package = {
    "Tiktok": "com.ss.android.ugc.trill",
    "XanhSM": "com.gsm.customer"
}

def check_health():
    try:
        response = requests.get(f"{os.getenv('API_URL')}/check-health")
        json_res = response.json()
        if json_res["success"]:
            return True
    except Exception as e:
        print(e)
        return False
def identify_app(request):
    try:
        response = requests.get(f"{os.getenv('API_URL')}/identify-app", params={"request": request})
        json_res = response.json()
        if json_res["success"]:
            return json_res["apps"]
        else:
            return None
    except Exception as e:
        print(e)
        return None

def similar_flows(app_package, request):
    try:
        response = requests.get(f"{os.getenv('API_URL')}/similar-flows", params={"app_package": app_package, "request": request})
        json_res = response.json()
        if json_res["success"]:
            return json_res["similar_flow_ids"]
        else:
            return None
    except Exception as e:
        print(e)
        return None

def get_action(app_package, request, flow_ids, previous_action):
    tmp_screen_shot_file = "tmp_screen.png" 
    tmp_dump_file = "tmp_dump.xml"
    take_screenshot(tmp_screen_shot_file)
    dump_ui(tmp_dump_file)
    try:
        # Define the form data as a dictionary
        form_data = {
            'app_package': app_package,
            'request': request,
            'similar_flow_ids': flow_ids,
            'previous_action': previous_action 
        }
        # Open the file you want to upload
        files = {
            'image': open(tmp_screen_shot_file, 'rb'),
            'xml_file': open(tmp_dump_file, 'rb')
        }
        
        # Send the POST request with the form data and the file
        response = requests.post(f"{os.getenv('API_URL')}/next-action", data=form_data, files=files)
        json_res = response.json()
        if json_res["success"]:
            return json_res["element_position"], json_res["action"], json_res["completed"], json_res["additional_data"], json_res["element_content_desc"]
        else:
            return None
    except Exception as e:
        print(e)
        return None

def main():
    # check health of the system
    if not check_health():
        print("System is not healthy")
        return 
    # ask user request
    request = input("Enter your request: ")
    # identify app
    apps = identify_app(request) 
    if len(apps) == 0:
        print("No app found")
        return
    print("Apps found:", apps)
    if len(apps) > 1:
        app = input("Enter the app package: ")
    else:
        app = apps[0]

    app = map_app_name_to_package[app]
    # get similar flows  
    similar_flows_ids = similar_flows(app, request)
    if not similar_flows_ids:
        print("No similar flows found")
        return
    print("Similar flows found:", similar_flows_ids)
    # execute loop
    similar_flows_ids = ",".join(similar_flows_ids)
    previous_action = "content_desc,action,data\n"
    step_count = 0

    # open app 
    open_app(app)
    while True:
        # take screen shot and get screen description 
        # get next action
        element_position, action, completed, additional_data, element_content_desc = get_action(
            app, 
            request, 
            similar_flows_ids, 
            previous_action)
        data = ""
        if action == "input":
            data = input(f"Input {additional_data}: ")
            tap(element_position[0], element_position[1])
            time.sleep(0.5)
            input_text(data)
        if action == "tap" or action == "click":
            tap(element_position[0], element_position[1])
        if action == "swipe_up":
            swipe_up()
        if action == "swipe_down":
            swipe_down()
        if action == "swipe_left":
            swipe_left()
        if action == "swipe_right":
            swipe_right()
        if action == "return":
            break

        previous_action += f"{element_content_desc},{action},{data}\n"
        if completed:
            break

        step_count += 1 
        if step_count > 5:
            break
        # wait for the action to complete
        time.sleep(2)

if __name__ == "__main__":
    main()
        
