import sys
import cv2
import cv2.cv as cv
import numpy as np
from numpy import *

def detect_face_and_organs(img, file_name):
    scale_factor = 1.1
    min_neighbors = 3
    flags = 0
    min_size = (10, 10)

    face_cascade = cv2.CascadeClassifier('cascade\haarcascade_frontalface_alt.xml')
    eye_cascade = cv2.CascadeClassifier('cascade\haarcascade_eye_tree_eyeglasses.xml')
    nose_cascade = cv2.CascadeClassifier('cascade\haarcascade_mcs_nose.xml')
    mouth_cascade = cv2.CascadeClassifier('cascade\haarcascade_mcs_mouth.xml')
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    face = face_cascade.detectMultiScale(gray, scale_factor, min_neighbors, cv2.cv.CV_HAAR_SCALE_IMAGE, min_size)

    if len(face) == 0:
        raise ValueError("No face")

    #getting face, eyes, nose, mouth
    for (x,y,w,h) in face:
        y -= 0.1 * (y + h / 2)
        h += 0.2 * (y + h / 2)
        roi = img[y:y + h, x:x + w]
        face_img = roi.copy()
        roi_gray = gray[y:y + h, x:x + w]

        eyes_coordinates = [(0, 0, 0, 0), (0, 0, 0, 0)]
        nose_coordinates = (0, 0, 0, 0)
        mouth_coordinates = (0, 0, 0, 0)
        
        #define eyes
        eyes = eye_cascade.detectMultiScale(roi_gray, 1.05, 2, flags, min_size)
        if len(eyes) == 0:
            raise ValueError("No eyes")
        for i, (ex, ey, ew, eh) in enumerate(eyes):
            if i > 1:
                break
            eyes_coordinates[i] = (ex, ey, ew, eh)
            cv2.rectangle(roi, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
        
        #define nose
        nose = nose_cascade.detectMultiScale(roi_gray, scale_factor, 20, flags, min_size)
        if len(nose) == 0:
            raise ValueError("No nose")
        for (nx, ny, nw, nh) in nose:
            nose_coordinates = (nx, ny, nw, nh)
            cv2.rectangle(roi, (nx, ny),(nx + nw,ny + nh),(0, 0, 255), 2)
            break
        
        #define mouth
        mouth = mouth_cascade.detectMultiScale(roi_gray, 1.25, 30, flags, (20, 20))
        if len(mouth) == 0:
            raise ValueError("No mouth")
        for (mx, my, mw, mh) in mouth:
            if my > mouth_coordinates[1] and mx < nose_coordinates[0] + nose_coordinates[2]:
                mouth_coordinates = (mx, my, mw, mh)
        cv2.rectangle(roi, (mouth_coordinates[0], mouth_coordinates[1]), (mouth_coordinates[0]
            + mouth_coordinates[2], mouth_coordinates[1] + mouth_coordinates[3]), (0, 255, 255), 2)

    return roi, face_img, eyes_coordinates, nose_coordinates, mouth_coordinates

def define_contours(img, roi):
    r = 0
    g = 0
    b = 0
    all = 0
    
    height, width = img.shape[:2]

    for i in range(3 * height / 8, 5 * height / 8 + 1):
        for j in range(3 * width / 8, 5 * width / 8 + 1):
            x, y, z = img[i, j]
            r += x
            g += y
            b += z
            all += 1

    face_color = cv.CV_RGB(r / all, g / all, b / all)

    contour_points = 60
    face_color_delta = 0.6

    points = arange(4 * contour_points).reshape(2 * contour_points, 2)

    for i in range (0, contour_points):
        cur_height = int((float(height) / contour_points) * (float(i) + 0.5))
        points[i] = (3 * width / 8, cur_height)

        if i > 0 and i + 1 < contour_points:
            for j in range(3 * width / 8, -1, -1):
                x, y, z = img[cur_height, j]
                color = cv.CV_RGB(x, y, z)

                k1 = color[0] / face_color[0]
                k2 = color[1] / face_color[1]
                k3 = color[2] / face_color[2]
            
                if ((1 - k1) * (1 - k1) + (1 - k2) * (1 - k2) + (1 - k3) * (1 - k3) < face_color_delta):
                    points[i] = (j, cur_height)
                else:
                    break

    for i in range (contour_points, 2 * contour_points):
        cur_height = int((float(height) / contour_points) * (float(2 * contour_points - 1 - i) + 0.5))
        points[i] = (5 * width / 8, cur_height)

        if i > contour_points and i + 1 < 2 * contour_points:
            for j in range(5 * width / 8, width):
                x, y, z = img[cur_height, j]
                color = cv.CV_RGB(x, y, z)
                
                k1 = color[0] / face_color[0]
                k2 = color[1] / face_color[1]
                k3 = color[2] / face_color[2]
                
                if ((1 - k1) * (1 - k1) + (1 - k2) * (1 - k2) + (1 - k3) * (1 - k3) < face_color_delta):
                    points[i] = (j, cur_height)
                else:
                    break

    good_points = []
    delta_weight = 30
    beg = 0
    end = 0
    seq = False

    for i in range (2, contour_points):
        if (abs(points[i][0] - points[i - 1][0]) < delta_weight and abs(points[i - 1][0] - points[i - 2][0]) < delta_weight):
            if (seq == False):
                beg = i
                seq = True
        else:
            end = i - 1
            if (seq == True):
                if (end - beg > 5):
                    good_points.append((beg, end))
                seq = False

        if i + 1 == contour_points and seq == True:
            end = contour_points -1
            if (end - beg > 5):
                good_points.append((beg, end))

    result_points = []
    result_points.append(points[0])
    to_add = True

    for gp in good_points:
        start = gp[0]
        end = gp[1]
        if end == contour_points - 1:
            to_add = False
        for i in range(start, end + 1):
            result_points.append(points[i])

    if to_add:
        result_points.append(points[contour_points - 1])

    beg = 0
    end = 0
    seq = False
    good_points = []

    for i in range (contour_points + 2, 2 * contour_points):
        if (abs(points[i][0] - points[i - 1][0]) < delta_weight and abs(points[i - 1][0] - points[i - 2][0]) < delta_weight):
            if (seq == False):
                beg = i
                seq = True
        else:
            end = i - 1
            if (seq == True):
                if (end - beg > 5):
                    good_points.append((beg, end))
                seq = False

        if i + 1 == 2 * contour_points and seq == True:
            end = 2 * contour_points -1
            if (end - beg > 5):
                good_points.append((beg, end))

    result_points.append(points[contour_points])
    to_add = True

    for gp in good_points:
        start = gp[0]
        end = gp[1]
        if  end == 2 * contour_points - 1:
            to_add = False
        for i in range(start, end + 1):
            result_points.append(points[i])

    if to_add:
        result_points.append(points[2 * contour_points - 1])

    for i in range(1, len(result_points)):
        pt1 = (result_points[i][0], result_points[i][1])
        pt2 = (result_points[i - 1][0], result_points[i - 1][1])
        cv2.line(roi, pt1, pt2, cv.CV_RGB(100, 0, 100), 2)

    pt1 = (result_points[0][0], result_points[0][1])
    pt2 = (result_points[len(result_points) - 1][0], result_points[len(result_points) - 1][1])
    cv2.line(roi, pt1, pt2, cv.CV_RGB(100, 0, 100), 2)

    return result_points, roi

def get_param(file_name):
    # while running first argument is picture_filename
    img = cv2.imread(file_name)
    if img == None:
        raise ValueError("No image" + file_name)

    roi, face_image, eyes_coordinates, nose_coordinates, mouth_coordinates = detect_face_and_organs(img, file_name)
    # 'result_points' - array of contour's points
    result_points, roi = define_contours(face_image, roi)
    
    return result_points, eyes_coordinates, nose_coordinates, mouth_coordinates, roi