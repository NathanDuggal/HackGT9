import cv2
import numpy as np
from tkinter import Tk, filedialog
import os
import dlib
import math
import time

# define a video capture object
vid = cv2.VideoCapture(0)

detector = dlib.get_frontal_face_detector()

predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

start_time = time.time()

def cart_to_polar(x, y):
    theta = np.arctan2(x,y) * 180/math.pi
    r = np.sqrt(x**2 + y**2)
    position = [theta, r]
    return position

def difference_between_x_points(points):
    top_point = points[0] #retrieving from tuple of points (0 through 2)
    bottom_point = points[2]
    return top_point[0] - bottom_point[0] #x values of top and bottom points
    

def ratio_between_points(points):
    distances = []
    ratios = []
    for c,point in list(enumerate(points))[:-1]:
        distances.append(math.dist(point, points[c+1]))
    for c,distance in list(enumerate(distances))[:-1]:
        ratios.append(distance / distances[c+1])
    return ratios


calibrated_nod_list = []
calibrated_nod = 0
calibrated_tilt_list = []
calibrated_tilt = 0


while(True):
    # Capture the video frame
    # by frame

    ret, frame = vid.read()
    scale_percent = 25 # percent of original size
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    dim = (width, height)

    # resize image
    frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

    gray = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    if (len(faces) != 0):
        face = faces[0]
        x1 = face.left() # left point
        y1 = face.top() # top point
        x2 = face.right() # right point
        y2 = face.bottom() # bottom point

        # Look for the landmarks
        landmarks = predictor(image=gray, box=face)

        points = [8, 33, 27] #bottom, middle, top
        point_list = []
        for n in points:
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            point_list.append((x,y))

            # Draw a circle
            cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 255, 0), thickness=-1)


        ratio = ratio_between_points(point_list)[0] #nodding (y)
        difference = difference_between_x_points(point_list) #tilting (x)

        if (time.time() - start_time < 5):
            calibrated_nod_list.append(ratio)
            calibrated_nod = np.mean(calibrated_nod_list)

            calibrated_tilt_list.append(difference)
            calibrated_tilt = np.mean(calibrated_tilt_list)

        joystick_y = np.clip((ratio - calibrated_nod) * 4, -1, 1)

        joystick_x = np.clip((difference - calibrated_tilt)/50, -1, 1)

        theta = cart_to_polar(joystick_x, joystick_y)[0]
        r = cart_to_polar(joystick_x, joystick_y)[1]


        if r > 1: #if r > 1
            r = 1

        print(theta)
        print(r)
        

    # Display the resulting frame
    cv2.imshow('frame', frame)
      
    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
  
# After the loop release the cap object
vid.release()

# Destroy all the windows
cv2.destroyAllWindows()