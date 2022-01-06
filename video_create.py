import glob
import cv2
import numpy as np

DESIRED_SIZE = (800, 600)
SLIDE_TIME = 5 # Seconds each image
FPS = 24

fourcc = cv2.VideoWriter.fourcc(*'X264')
writer = cv2.VideoWriter('output.avi', fourcc, FPS, DESIRED_SIZE)

for file_name in glob.iglob('*.jpeg'):
    img = cv2.imread(file_name)

    # Resize image to fit into DESIRED_SIZE
    height, width, _ = img.shape
    proportion = min(DESIRED_SIZE[0]/width, DESIRED_SIZE[1]/height)
    new_size = (int(width*proportion), int(height*proportion))
    img = cv2.resize(img, new_size)

    # Centralize image in a black frame with DESIRED_SIZE
    target_size_img = np.zeros((DESIRED_SIZE[1], DESIRED_SIZE[0], 3), dtype='uint8') 
    width_offset = (DESIRED_SIZE[0] - new_size[0]) // 2
    height_offset = (DESIRED_SIZE[1] - new_size[1]) // 2
    target_size_img[height_offset:height_offset+new_size[1], 
                    width_offset:width_offset+new_size[0]] = img

    for _ in range(SLIDE_TIME * FPS):
        writer.write(target_size_img)

writer.release()