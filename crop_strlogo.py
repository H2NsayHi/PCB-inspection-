import os
import cv2

# Define the paths
image_path = 'label_2.jpg'
label_file_path = 'label_2.txt'
output_folder = 'text_detect_data'

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Load the image
image = cv2.imread(image_path)
image_height, image_width = image.shape[:2]

# Read the label file
with open(label_file_path, 'r') as file:
    lines = file.readlines()

# Process each line
for idx, line in enumerate(lines):
    parts = line.strip().split()
    class_name = parts[0]
    x_center = float(parts[1])
    y_center = float(parts[2])
    width = float(parts[3])
    height = float(parts[4])
    
    if class_name in ["6"]:
        # Calculate the bounding box coordinates
        x1 = int((x_center - width / 2) * image_width)
        y1 = int((y_center - height / 2) * image_height)
        x2 = int((x_center + width / 2) * image_width)
        y2 = int((y_center + height / 2) * image_height)
        
        # Crop the image
        cropped_image = image[y1:y2, x1:x2]
        
        # Check if idx is within specified intervals and rotate if necessary
        if (8 <= idx <= 15) or (24 <= idx <= 31) or (40 <= idx <= 47):
            cropped_image = cv2.rotate(cropped_image, cv2.ROTATE_180)
        
        # Save the cropped image
        output_path = os.path.join(output_folder, f"{class_name}_{idx}.jpg")
        cv2.imwrite(output_path, cropped_image)

print("Cropping and saving completed.")
