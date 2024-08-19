import cv2
import numpy as np
import random
import os

# Create the output directory if it doesn't exist
output_dir = 'output_files'
os.makedirs(output_dir, exist_ok=True)

# Load the image
image_path = 'label_2.jpg'
image = cv2.imread(image_path)
img_height, img_width = image.shape[:2]

# Load the label file
label_path = 'label_2.txt'
with open(label_path, 'r') as f:
    labels = [line.strip().split() for line in f]

# Convert label data to numeric values
labels = [(int(label[0]), float(label[1]), float(label[2]), float(label[3]), float(label[4])) for label in labels]

# Helper function to check if bbox A contains bbox B
def contains_bbox(bbox_a, bbox_b):
    ax1, ay1, ax2, ay2 = bbox_a
    bx1, by1, bx2, by2 = bbox_b
    return ax1 <= bx1 and ax2 >= bx2 and ay1 <= by1 and ay2 >= by2

# Convert center coordinates to corners for each label
def get_bbox_coords(label):
    class_label, x_center, y_center, width, height = label
    box_width = width * img_width
    box_height = height * img_height
    box_x_center = x_center * img_width
    box_y_center = y_center * img_height

    x1 = box_x_center - box_width / 2
    y1 = box_y_center - box_height / 2
    x2 = box_x_center + box_width / 2
    y2 = box_y_center + box_height / 2

    return (x1, y1, x2, y2)

# Draw a piece on the image at the bounding box location
def draw_piece(image, c_label):
    _, x_center, y_center, width, height = c_label
    box_width = width * img_width
    box_height = height * img_height
    box_x_center = x_center * img_width
    box_y_center = y_center * img_height

    x1 = int(box_x_center - box_width / 2)
    y1 = int(box_y_center - box_height / 2)
    x2 = int(box_x_center + box_width / 2)
    y2 = int(box_y_center + box_height / 2)

    # Get the color of the top center pixel
    top_center_x = max(x1, 0)
    top_center_y = max(y1, 0)
    if 0 <= top_center_y < img_height and 0 <= top_center_x < img_width:
        piece_color = tuple(image[top_center_y, top_center_x].tolist())
    else:
        piece_color = (0, 0, 0)  # Default to black if the pixel is out of bounds

    # Define the size of the overlapping piece
    piece_width = int(box_width)
    piece_height = int(box_height)
    piece_x1 = random.randint(x1, x2 - piece_width)
    piece_y1 = random.randint(y1, y2 - piece_height)
    piece_x2 = piece_x1 + piece_width
    piece_y2 = piece_y1 + piece_height

    # Draw the piece
    cv2.rectangle(image, (piece_x1, piece_y1), (piece_x2, piece_y2), piece_color, -1)

# Probability of drawing a piece over a bounding box
draw_probability = 0.2  # 50% chance

# Run the process 10 times
for i in range(1, 101):
    # Make a copy of the image to modify
    modified_image = image.copy()

    # Prepare to store new labels
    new_labels = []

    # Process each label for overlap checking and drawing
    for parent_label in labels:
        parent_class, px_center, py_center, p_width, p_height = parent_label
        parent_bbox = get_bbox_coords(parent_label)

        if parent_class == 6:
            has_class_0 = has_class_7 = False

            for child_label in labels:
                child_class, _, _, _, _ = child_label
                if child_class in [0, 7]:
                    child_bbox = get_bbox_coords(child_label)
                    if contains_bbox(parent_bbox, child_bbox) and random.random() < draw_probability:
                        if child_class == 0:
                            has_class_0 = True
                        elif child_class == 7:
                            has_class_7 = True
                        draw_piece(modified_image, child_label)

            # Determine the label based on the presence of class 0 and 7
            if has_class_0 and has_class_7:
                label = 'MISS_STR_LOGO'
            elif has_class_0:
                label = 'MISS_LOGO'
            elif has_class_7:
                label = 'MISS_STR'
            else:
                label = 'STR_LOGO_OK'

            new_labels.append(f'{label} {px_center} {py_center} {p_width} {p_height}')

        elif parent_class == 5:
            has_class_3 = False

            for child_label in labels:
                child_class, _, _, _, _ = child_label
                if child_class == 3:
                    child_bbox = get_bbox_coords(child_label)
                    if contains_bbox(parent_bbox, child_bbox) and random.random() < draw_probability:
                        has_class_3 = True
                        draw_piece(modified_image, child_label)

            # Determine the label based on the presence of class 3
            if has_class_3:
                new_labels.append(f'QR_NG {px_center} {py_center} {p_width} {p_height}')
            else:
                new_labels.append(f'QR_OK {px_center} {py_center} {p_width} {p_height}')

    # Write new labels to the file with iteration index
    new_label_file_path = os.path.join(output_dir, f'{i}.txt')
    with open(new_label_file_path, 'w') as f:
        for line in new_labels:
            f.write(f"{line}\n")

    # Save the modified image with iteration index
    modified_image_file_path = os.path.join(output_dir, f'{i}.png')
    cv2.imwrite(modified_image_file_path, modified_image)
