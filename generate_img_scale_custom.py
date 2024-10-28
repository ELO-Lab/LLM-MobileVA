import os
import shutil
from PIL import Image
import argparse


def generate_detect_element_dataset(image_path, label_path, number_of_scale_image=20):
    package_dir = f"detect_element_dataset"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)

    train_dir = f"{package_dir}/train"
    valid_dir = f"{package_dir}/valid"
    test_dir = f"{package_dir}/test"
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(valid_dir, exist_ok=True)

    scale_factor = 0.1
    scale_factor_step = 0.02
    for index in range(number_of_scale_image):
        ratio = ((index + 1) / number_of_scale_image)
        if ratio <= 0.8:  # 80% for the training dataset
            output_dir = train_dir
        elif 0.8 < ratio <= 1:  # 10% for the validation dataset
            output_dir = valid_dir
        else:  # 10% for the testing dataset
            output_dir = test_dir
        
        generate_images_and_labels(output_dir, image_path, label_path, scale_factor)
        scale_factor += scale_factor_step
    print("\n Successfully generated dataset!")

def generate_images_and_labels(output_dir, image_path, label_path, scale_factor):
    image_dir = f"{output_dir}/images"
    label_dir = f"{output_dir}/labels"
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(label_dir, exist_ok=True)

    # Scale the image and adjust bounding boxes
    scaled_image, img_width, img_height, scaled_bounds = scale_image_and_bounds(image_path, label_path, scale_factor)

    # Save the scaled image
    base_filename = os.path.basename(image_path)
    image_save_path = f"{image_dir}/{os.path.splitext(base_filename)[0]}_{int(scale_factor * 100)}.png"
    scaled_image.save(image_save_path)

    # Save the scaled labels
    label_save_path = f"{label_dir}/{os.path.splitext(base_filename)[0]}_{int(scale_factor * 100)}.txt"
    with open(label_save_path, 'w') as f:
        for bounding_box in scaled_bounds:
            # Ensure class ID is written as an integer and other values as floats
            class_id = int(bounding_box[0])  # Explicitly cast to int to avoid float representation
            center_x = bounding_box[1]
            center_y = bounding_box[2]
            box_width = bounding_box[3]
            box_height = bounding_box[4]

            # Use formatted string to control the output
            f.write(f"{class_id} {center_x:.10f} {center_y:.10f} {box_width:.10f} {box_height:.10f}\n")


def scale_image_and_bounds(image_path, label_path, scale_factor):
    original_image = Image.open(image_path)
    width, height = original_image.size
    scaled_width = int(width * scale_factor)
    scaled_height = int(height * scale_factor)

    # Resize the image
    scaled_image = original_image.resize((scaled_width, scaled_height), Image.LANCZOS)

    # Read and scale bounding boxes
    scaled_bounds = []
    with open(label_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            class_id, center_x, center_y, box_width, box_height = map(float, line.split())

            # Scale the bounding boxes
            scaled_center_x = center_x * scaled_width
            scaled_center_y = center_y * scaled_height
            scaled_box_width = box_width * scaled_width
            scaled_box_height = box_height * scaled_height

            # Normalize to new image size
            scaled_bounds.append([
                class_id,
                scaled_center_x / scaled_width,
                scaled_center_y / scaled_height,
                scaled_box_width / scaled_width,
                scaled_box_height / scaled_height
            ])

    return scaled_image, scaled_width, scaled_height, scaled_bounds


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate dataset for element detection.')
    parser.add_argument('--d', type=str, required=True, help='Path to the image file.')
    parser.add_argument('--l', type=str, required=True, help='Path to the label file.')
    parser.add_argument('--n', type=int, default=20, help='Number of scaled images to generate.') # Config selecting samples

    args = parser.parse_args()
    image_path = args.d
    label_path = args.l
    number_of_scale_image = args.n

    generate_detect_element_dataset(image_path, label_path, number_of_scale_image)
    '''
    python ./generate_img_scale_custom.py --d ./images/example.png --l ./labels/1.txt 
    '''