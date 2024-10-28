from PIL import Image
from io import StringIO,BytesIO
from pkgs.ui_element import UIElement
import base64
import os
import pandas as pd
import uuid
import xml.etree.ElementTree as ET

interactable_classes = [
    'android.widget.Button',
    'android.widget.EditText',
    'android.widget.CheckBox',
    'android.widget.Switch',
    'android.widget.RadioButton',
    'android.widget.ToggleButton',
    'android.widget.TextView',
    'android.widget.ImageView',
    'android.view.View',
    'android.view.ViewGroup'
    # Add other interactable class names as needed
]

def extract_interactable_elements_by_class(xml_dump, interactable_classes):
    tree = ET.parse(xml_dump)
    root = tree.getroot()

    interactable_elements = []
    last_valid_bounds = None

    for elem in root.iter():
        class_name = elem.get('class')
        clickable = elem.get('clickable') == 'true'
        focusable = elem.get('focusable') == 'true'
        enabled = elem.get('enabled') == 'true'
        if class_name in interactable_classes:
            bounds = elem.get('bounds')
            if bounds == "[0,0][0,0]" and last_valid_bounds:
                bounds = last_valid_bounds
            else:
                last_valid_bounds = bounds

            # Parse bounds
            bounds_parts = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
            x1, y1, x2, y2 = map(int, bounds_parts)

            element_info = {
                'id': elem.get('id'),
                'class': class_name.split('.')[-1],
                'resource-id': elem.get('resource-id'),
                'clickable': clickable,
                'text': (elem.get('text') or '').replace(',', '').replace('\n', ''),
                'content-desc': (elem.get('content-desc') or '').replace(',', ''),
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2
            }
            interactable_elements.append(element_info)

    # Second pass to adjust bounds of elements with [0,0][0,0]
    for i in range(1, len(interactable_elements)):
        if interactable_elements[i]['x1'] == interactable_elements[i]['x2'] == interactable_elements[i]['y1'] == interactable_elements[i]['y2'] == 0:
            interactable_elements[i]['x1'] = interactable_elements[i-1]['x1']
            interactable_elements[i]['y1'] = interactable_elements[i-1]['y1']
            interactable_elements[i]['x2'] = interactable_elements[i-1]['x2']
            interactable_elements[i]['y2'] = interactable_elements[i-1]['y2']

    # check if unclickable elements and remove
    interactable_elements = remove_unclickable_elements(interactable_elements, class_name= "View")
    interactable_elements = remove_unclickable_elements(interactable_elements, class_name= "ViewGroup")
    interactable_elements = check_and_remove_empty_text_and_desc(interactable_elements, class_name= "ViewGroup")
    # Generate CSV string
    element_csv = 'id,class,resource-id,text,content-desc,x1,y1,x2,y2\n'
    for element in interactable_elements:
        element_csv += f"{element['id']},{element['class']},{element['resource-id']},{element['text']},{element['content-desc']},{element['x1']},{element['y1']},{element['x2']},{element['y2']}\n"

    #print(element_csv)
    return element_csv  

def check_and_remove_empty_text_and_desc(elements, class_name="View"):
    filtered_elements = []
    for elem in elements:
        if elem['class'] == class_name and elem['text'] == "" and elem['content-desc'] == "":
            continue
        filtered_elements.append(elem)
    return filtered_elements

def remove_unclickable_elements(elements, class_name="View"):
    clickable_elements = []
    for elem in elements:
        if elem['class'] == class_name and elem['clickable'] == 'false':
            continue
        clickable_elements.append(elem)
    return clickable_elements    

def crop_elements(screen_img, element_csv, output_folder):
    # Load the screen image
    screen_image = Image.open(screen_img)
    # Read the CSV file
    elements_df = pd.read_csv(StringIO(element_csv))
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    # Loop through each row in the DataFrame and save the cropped images
    for index, row in elements_df.iterrows():
        x1, y1, x2, y2 = row['x1'], row['y1'], row['x2'], row['y2']
        if x1 == x2 == y1 == y2 == 0:
            continue
        # Crop the image
        cropped_image = screen_image.crop((x1, y1, x2, y2))
        # Create a unique filename
        filename = f"cropped_element_{index}.png"
        # Save the cropped image
        cropped_image.save(os.path.join(output_folder, filename))
    print(f"Cropped images saved to {output_folder}")


# Define a function to check if two elements overlap significantly
def is_significantly_overlapping(elem1, elem2, threshold=1):
    x1_min, y1_min, x1_max, y1_max = elem1['x1'], elem1['y1'], elem1['x2'], elem1['y2']
    x2_min, y2_min, x2_max, y2_max = elem2['x1'], elem2['y1'], elem2['x2'], elem2['y2']
    
    overlap_x_min = max(x1_min, x2_min)
    overlap_y_min = max(y1_min, y2_min)
    overlap_x_max = min(x1_max, x2_max)
    overlap_y_max = min(y1_max, y2_max)
    
    overlap_width = max(0, overlap_x_max - overlap_x_min)
    overlap_height = max(0, overlap_y_max - overlap_y_min)
    
    overlap_area = overlap_width * overlap_height
    elem1_area = (x1_max - x1_min) * (y1_max - y1_min)
    elem2_area = (x2_max - x2_min) * (y2_max - y2_min)
    
    # Calculate the overlap ratio for each element
    overlap_ratio_elem1 = overlap_area / elem1_area if elem1_area > 0 else 0
    overlap_ratio_elem2 = overlap_area / elem2_area if elem2_area > 0 else 0
    
    # Check if either overlap ratio is greater than the threshold
    return overlap_ratio_elem1 > threshold or overlap_ratio_elem2 > threshold


def remove_invalid_elements(elements):
    valid_elements = []
    for index, elem in elements.iterrows():
        if elem['x1'] == elem['x2'] == elem['y1'] == elem['y2'] == 0:
            continue
        if elem['x1'] >= elem['x2'] or elem['y1'] >= elem['y2']:
            continue
        valid_elements.append(elem)
    return valid_elements

# Check for and remove overlapping elements
def remove_overlapping_elements(elements):
    unique_elements = []
    for elem in elements:
        is_unique = True
        for unique_elem in unique_elements:
            if is_significantly_overlapping(elem, unique_elem):
                is_unique = False
                break
        if is_unique:
            unique_elements.append(elem)
    return unique_elements

def generete_elements(screen_img, element_csv): 
    # Load the screen image
    screen_image = Image.open(screen_img)
    # Read the CSV file
    elements_df = pd.read_csv(StringIO(element_csv))
    elements_df = remove_invalid_elements(elements_df)
    elements_df = remove_overlapping_elements(elements_df)
    # Loop through each row in the DataFrame and save the cropped images
    elements = []
    for row in elements_df:
        x1, y1, x2, y2 = row['x1'], row['y1'], row['x2'], row['y2']
        if x1 == x2 == y1 == y2 == 0:
            continue
        # Crop the image
        cropped_image = screen_image.crop((x1, y1, x2, y2))
        buffer = BytesIO()
        cropped_image.save(buffer, format='PNG')
        # Get the raw bytes from the buffer
        raw_bytes = buffer.getvalue()
        # Encode the raw bytes to a base64 string
        base64_string = base64.b64encode(raw_bytes).decode('utf-8')
        element = UIElement(
            base64_string,  
            row['id'],
            row['class'],
            row['resource-id'],  # Resource ID is optional, could be Non
            row['text'],
            row['content-desc'],
            (x1, y1, x2, y2),
            []
        )
        elements.append(element)       
        print(f"{len(elements)},{element.id},{element.android_class},{element.resource_id},{element.text},{element.content_desc},{element.bound}")
    return elements

