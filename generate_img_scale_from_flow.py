import os
import jsonpickle
import uuid
from PIL import Image
from io import BytesIO
import shutil 
import base64
from pkgs.screen import Screen 

def load_flow_data(app_package: str, flow_data_folder="data_set"):
    for app in os.listdir(flow_data_folder):
        if app == app_package:
            app_folder = os.path.join(flow_data_folder, app)
            flows = []
            if os.path.isdir(app_folder):
                for flow_file in os.listdir(app_folder):
                    with open(f"{app_folder}/{flow_file}", "r") as f:
                        data = f.read()
                        flow = jsonpickle.decode(data)
                        flow.id = flow_file.split(".")[0]
                        flows.append(flow)
                app_data = {
                    'app_package': app,
                    'flows': flows
                }
    return app_data

def generate_detect_element_dataset(app_data, number_of_scale_image=40):
    app_package = app_data['app_package']
    print("app_package: ", app_package)
    flows = app_data['flows']
    classes_number = 0
    package_dir = f"detect_element_dataset/{app_package}"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    for flow in flows:
        screens = extract_elements_from_flow(flow)
        train_dir = f"{package_dir}/train"
        valid_dir = f"{package_dir}/valid"
        test_dir = f"{package_dir}/test"
        os.makedirs(train_dir, exist_ok=True)
        os.makedirs(test_dir, exist_ok=True)
        os.makedirs(valid_dir, exist_ok=True)
        for screen in screens:
            scale_factor = 0.05
            scale_factor_step = 0.01
            screen_shot = screen['screen_shot']
            bounds = screen['execute_element_bound']
            screen_id = screen['screen_id']
            for index in range(number_of_scale_image):
                ratio = ((index +1) / number_of_scale_image)
                if ratio <= 0.8: # 70% for the training dataset 
                    generate_images_and_labels(train_dir, screen_shot, bounds, screen_id, classes_number, scale_factor, scale_factor_step)
                elif 0.8 < ratio <= 1: # 20% for the validation dataset
                    generate_images_and_labels(valid_dir, screen_shot, bounds, screen_id, classes_number, scale_factor, scale_factor_step)
                else: # 10 % for the testing dataset 
                    generate_images_and_labels(test_dir, screen_shot, bounds, screen_id, classes_number, scale_factor, scale_factor_step)
                scale_factor = scale_factor + scale_factor_step
            classes_number = classes_number + 1
    names = ""
    for index in range(classes_number):
        names = names + "\n" + f"- {index}"
    data = f"""
names:{names}
nc: {classes_number}
test: {test_dir}/images
train: {train_dir}/images
val: {valid_dir}/images        
"""
    with open(f"{package_dir}/data.yaml", "w") as f:
        f.write(data)
    print("Successfully generate dataset !!!")

def generate_images_and_labels(output_dir, screen_shot, bounds, screen_id, classes_number, scale_factor, scale_factor_step):
    image_dir = f"{output_dir}/images"
    label_dir = f"{output_dir}/labels"
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(label_dir, exist_ok=True)
    if os.path.isdir(image_dir):
        image_path = f"{image_dir}/{screen_id}"
        img_width, img_height, scaled_bounds = scale_image_and_bounds(screen_shot, image_path, bounds, scale_factor)
        print("scaled_bounds: ", scaled_bounds)
    if os.path.isdir(label_dir):
        label_path = f"{label_dir}/{screen_id}_{img_width}_{img_height}.txt"
        bouding_box = generate_bounding_box(classes_number, label_path, scaled_bounds, img_width, img_height)
        print("bounding_box: ", bouding_box)

def extract_elements_from_flow(flow):
    screens = []
    for screen in flow.screens:
        execute_element_index = screen.execute_element_index
        for index, ui_element in enumerate(screen.ui_elements):
            if index == execute_element_index:
                bound = ui_element.bound
                screen = {
                    'screen_id': str(uuid.uuid4()),
                    'screen_shot': screen.screen_shot,
                    'execute_element_bound': bound
                }
                screens.append(screen)
    return screens

def scale_image_and_bounds(base64_image, output_image_path, bounds: list, scale_factor):
    image_data = base64.b64decode(base64_image)
    original_image = Image.open(BytesIO(image_data))
    print("image size: ", original_image.size)
    width, height = original_image.size
    scaled_width = int(width * scale_factor)
    scaled_height = int(height * scale_factor)
    scaled_image = original_image.resize((scaled_width, scaled_height), Image.LANCZOS)
    print("scaled_image: ", scaled_image.size)
    scaled_image.save(f"{output_image_path}_{scaled_width}_{scaled_height}.png")
    scaled_bounds = []
    for bound in bounds:
        scaled_bounds.append(int(bound) *  scale_factor)
    
    return scaled_width, scaled_height, scaled_bounds

def generate_bounding_box(classes_number, save_path, bounds, img_width, img_height):
    x1, y1, x2, y2 = bounds
    center_x = (x1 + x2) / 2 / img_width
    center_y = (y1 + y2) / 2 / img_height
    width = (x2 - x1) / img_width
    height = (y2 - y1) / img_height
    with open(save_path, "w") as file:
        file.write(f"{classes_number} {center_x} {center_y} {width} {height}")
    return [center_x, center_y, width, height]

if __name__ == "__main__":
    map_app_name_to_package = {
    "amazon": "com.amazon.mShop.android.shopping",
    "doordash": "com.dd.doordash",
    "facebook": "com.facebook.katana",
    "youtube": "com.google.android.youtube",
    "tiktok": "com.ss.android.ugc.trill",
    "gsm": "com.gsm.customer",
    "uber": "com.ubercab"
    }

    # Extract the keys and convert them to a list
    app_names = list(map_app_name_to_package.keys())
    print(app_names)
    
    while True:
        try:
            app_name = input("Enter the app name: ")
            app_package = map_app_name_to_package[app_name]
            flow_data = load_flow_data(app_package, flow_data_folder="data/flows")
            print(flow_data['app_package'])
            generate_detect_element_dataset(flow_data, number_of_scale_image=40)
        except KeyError:
            print("Invalid app name")