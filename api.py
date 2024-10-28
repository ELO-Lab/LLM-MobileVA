from fastapi import FastAPI, HTTPException, Request, Depends, File, UploadFile, Form
from pkgs import Executor, Screen, AppIdentifier, LangChainExecutor
import base64
import os
import tempfile
import uuid
from dotenv import load_dotenv

load_dotenv()
llm_executor = LangChainExecutor(os.getenv("LLM_MODEL"))
app = FastAPI()

###########
@app.get("/check-health")
async def check_health():
    response = {
        "success": True
    }
    return response

@app.get("/identify-app")
async def identify_app(request: str):
    app_identifier = AppIdentifier(llm_executor)
    rs = app_identifier.identify_app(request)
    response = {
        "success": True,
        "apps": rs["apps"]
    }
    return response

@app.get("/similar-flows")
async def similar_flows(app_package: str, request: str):
    executor = Executor(llm_executor)
    flows = executor.query_app_flows(app_package)  
    similar_flow_ids = executor.query_simular_flow_ids(request, flows)

    response = {
        "app_package": app_package,
        "request": request,
        "similar_flow_ids": similar_flow_ids,
        "success": True
    }
    return response

@app.post("/next-action")
async def next_action(
        app_package: str = Form(...), 
        request: str = Form(...),
        similar_flow_ids: str = Form(...),
        previous_action: str = Form(...),
        image: UploadFile = File(...),
        xml_file: UploadFile = File(...),
    ):
     # Create temporary files for the image and XML
    with tempfile.NamedTemporaryFile(delete=False) as tmp_image, tempfile.NamedTemporaryFile(delete=False) as tmp_xml:
        image_path = tmp_image.name 
        xml_path = tmp_xml.name
        # Write the uploaded files to the temporary files
        tmp_image.write(await image.read())
        tmp_xml.write(await xml_file.read())
    
    try:
        executor = Executor(llm_executor, False, False)
        similar_flow_ids = similar_flow_ids.split(",")
        similar_flow = executor.query_flow_by_ids(similar_flow_ids, app_package)
        print("similar_flow", similar_flow)
        # Process the files as needed
        screen = Screen(empty_data=True)
        screen.screen_from_api_data(app_package, image_path, xml_path, llm_executor)
        element_index, action, completed, additional_data = executor.get_next_action(request, similar_flow, screen, previous_action)       
        element_position = screen.get_element_center(element_index)
        # Create the response
        response = {
            "app_package": app_package,
            "request": request,
            "similar_flows_id": similar_flow_ids,
            "element_position":  element_position,
            "action": action,
            "completed": completed,
            "additional_data": additional_data,
            "success": True
        }
        if element_index == -1:
            response["element_content_desc"] = "screen"
        else:
            response["element_content_desc"] = screen.ui_elements[element_index].content_desc

    finally:
        # Delete the temporary files
        os.remove(image_path)
        os.remove(xml_path)
    
    return response


if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    load_dotenv()
    # load ip and port from os    
    api_url = os.getenv('API_URL', 'http://0.0.0.0:3000')
    ip = api_url.split(":")[1].replace("//", "")
    port = int(api_url.split(":")[2])
    uvicorn.run(app, host=ip, port=port)
