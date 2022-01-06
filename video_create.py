import glob
import cv2

DESIRED_SIZE = (800, 600)
FPS = 24

fourcc = cv2.VideoWriter.fourcc(*'MPEG')
writer = cv2.VideoWriter('output.avi', fourcc, FPS, DESIRED_SIZE)

for file_name in glob.iglob('*.jpeg'):
    img = cv2.imread(file_name)

    for _ in range( FPS):
        writer.write(img)

writer.release()