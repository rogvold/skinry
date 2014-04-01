import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
import cv2
import cv2.cv as cv
import sys

def rotate(A, B, C):
    return (B[0] - A[0]) * (C[1] - B[1]) - (B[1] - A[1]) * (C[0] - B[0])

def grahamscan(A):
    n = len(A)
    if n < 3:
        return []
    P = range(n)

    for i in range(1,n):
        if A[i][0] < A[0][0]:
            P[i], P[0] = P[0], P[i]

    for i in range(2,n):
        j = i
        while j > 1 and (rotate(A[P[0]], A[P[j - 1]], A[P[j]]) < 0):
            P[j], P[j-1] = P[j-1], P[j]
            j -= 1
      
    S = [P[0],P[1]]
    for i in range(2,n):
        while rotate(A[S[-2]], A[S[-1]], A[P[i]]) < 0:
            del S[-1]
        S.append(P[i])

    B = []
    for s in S:
        B.append(A[s])

    return B
    
def detect_face_and_organs(img):
    scale_factor = 1.1
    H, W = img.shape[:2]

    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')
    nose_cascade = cv2.CascadeClassifier('haarcascade_mcs_nose.xml')
    mouth_cascade = cv2.CascadeClassifier('haarcascade_mcs_mouth.xml')

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    to_do = True
    for sf in [1.1, 1.01]:
        if to_do == False:
            break
        for mn in [3, 5, 7]:
            face = face_cascade.detectMultiScale(gray, sf, mn, cv2.cv.CV_HAAR_SCALE_IMAGE, (H / 8, W / 8))
            if len(face) > 0:
                to_do = False
                break

    if len(face) == 0:
        raise ValueError("Error: No face. May be your eyes are closed")

    face_obtained = False
    #getting face, eyes, nose, mouth
    for (x,y,w,h) in face:
        y -= 0.1 * (y + h / 2)
        h += 0.2 * (y + h / 2)
        y = max(int(y), 0)
        h = min(int(h), H - 1 - y)

        if H * W > 10 * h * w:
            break

        face_obtained = True

        roi = img[y:y + h, x:x + w]
        roi_gray = gray[y:y + h, x:x + w]

        eyes_coordinates = [(0, 0, 0, 0), (0, 0, 0, 0)]
        nose_coordinates = (0, 0, 0, 0)
        mouth_coordinates = (0, 0, 0, 0)

        eyess = []
        #define eyes
        to_do = True
        for sf in [1.1, 1.05]:
            if to_do == False:
                break
            for mn in [3, 5, 7]:
                eyes = eye_cascade.detectMultiScale(roi_gray, sf, mn)
                eyess.append(eyes)
                if len(eyes) >= 2:
                    to_do = False
                    break

        for eye in eyess:
            if len(eye) > len(eyes):
                eyes = eye

        for i, (ex, ey, ew, eh) in enumerate(eyes):
            delta = int(0.3 * eh)
            ey = max(0, ey - delta)
            eh += delta
            eyes[i] = (ex, ey, ew, eh)


        nose = nose_cascade.detectMultiScale(roi_gray, scale_factor, 5, 0, (h / 10, w / 10))
        mouth = mouth_cascade.detectMultiScale(roi_gray, scale_factor, 5, 0 , (h / 10, w / 10))

        if len(eyes) == 0:
            for (nx, ny, nw, nh) in nose:
                if (nx < int(0.6 * w) and nx > int(0.2 * w) and ny > int(0.3 * h) and ny < int(0.6 * h)):
                    nose_coordinates = (nx, ny, nw, nh)
                    break
            for (mx, my, mw, mh) in mouth:
                if (mx < int(0.6 * w) and mx > int(0.2 * w) and my > int(0.6 * h)):
                    mouth_coordinates = (mx, my, mw, mh)
                    break

        if len(eyes) == 1:
            eyes_coordinates[0] = eyes[0]
            for (nx, ny, nw, nh) in nose:
                if (ny > (eyes_coordinates[0][1] + int(0.2 * eyes_coordinates[0][3])) and
                abs(ny - eyes_coordinates[0][1] - eyes_coordinates[0][3]) < h / 7):
                    nose_coordinates = (nx, ny, nw, nh)
                    break
            for (mx, my, mw, mh) in mouth:
                if (my > nose_coordinates[1] + int(nose_coordinates[3] * 0.7) and
                    my > eyes_coordinates[0][1] + eyes_coordinates[0][3]):
                    mouth_coordinates = (mx, my, mw, mh)
                    break

        if len(eyes) > 2:
            for i in range(len(eyes) - 2, -1, -1):
                for j in range(i, len(eyes) - 1):
                    if eyes[j][0] > eyes[j + 1][0]:
                        eyes[j], eyes[j + 1] = eyes[j + 1], eyes[j]

            eyes_coordinates[0] = eyes[0]
            for i in range(1, len(eyes)):
                if (eyes[i][0] > eyes[0][0] + eyes[0][2] and abs(eyes[0][1] - eyes[i][1]) < h / 7):
                    eyes_coordinates[1] = eyes[i]
                    break
            eyes = [eyes_coordinates[0], eyes_coordinates[1]]

        if len(eyes) == 2:
            eyes_coordinates[0] = eyes[0]
            eyes_coordinates[1] = eyes[1]

            if eyes_coordinates[0][0] > eyes_coordinates[1][0]:
                eyes_coordinates[0], eyes_coordinates[1] = eyes_coordinates[1], eyes_coordinates[0]
            for (nx, ny, nw, nh) in nose:
                if (nx > eyes_coordinates[0][0] + int(eyes_coordinates[0][2] * 0.3) and
                    nx < eyes_coordinates[1][0] and ny > (eyes_coordinates[0][1] + 
                    int(0.6 * eyes_coordinates[0][3])) and
                    abs(ny - eyes_coordinates[0][1] - eyes_coordinates[0][3]) < h / 7):
                    nose_coordinates = (nx, ny, nw, nh)
                    break
            for (mx, my, mw, mh) in mouth:
                if (my > nose_coordinates[1] + int(nose_coordinates[3] * 0.7) and
                    (mx > eyes_coordinates[0][0] or abs(mx - eyes_coordinates[0][0]) < 0.1 * w) and
                    mx < eyes_coordinates[1][0]  and mx + mw > eyes_coordinates[1][0] and 
                    my > eyes_coordinates[0][1] + eyes_coordinates[0][3]):
                    mouth_coordinates = (mx, my, mw, mh)
                    break

    if face_obtained == False:
        raise ValueError('Face is too small')

    return roi, eyes_coordinates, nose_coordinates, mouth_coordinates


def define_contours(img):
    train = pd.read_csv('train.csv')[:3000]
    X_train = np.asarray(train[range(0, 3)])
    Y_train = np.asarray(train[[3]]).ravel()

    estimator = KNeighborsClassifier(n_neighbors = 3, weights = 'distance')
    estimator.fit(X_train, Y_train)

    r, g, b = cv2.split(img)
    h, w = img.shape[:2]
    delta = h / 30

    j = 1
    points = []

    for i in range(0, 30):
        test = zip(b[j], g[j], r[j])
        res = estimator.predict(test)
        x1 = x2 = -1
        
        count = 0
        for k in range(int(0.5 * w), w):
            if res[k] == 1:
                count += 1
                if count > 20:
                    x2 = k
            else:
                count = 0
        
        count = 0
        for k in range(int(w / 2), -1, -1):
            if res[k] == 1:
                count += 1
                if count > 20:
                    x1 = k
            else:
                count = 0
        

        if x1 >= 10:
            points.append((x1, j))
        if x2 > -1 and x2 <= w - 9:
            points.append((x2, j))
        
        if i == 28:
            j = h - 5
        else:
            j += delta

    points.append((int(0.4 * w), h - 1))
    points.append((int(0.6 * w), h - 1))

    points = grahamscan(points)
    
    return points

def get_param(file_name):
    img = cv2.imread(file_name)
    if img == None:
        raise ValueError("No image" + file_name)
    
    face_image, eyes_coordinates, nose_coordinates, mouth_coordinates = detect_face_and_organs(img)
    # 'result_points' - array of contour's points
    result_points = define_contours(face_image)
    
    return result_points, eyes_coordinates, nose_coordinates, mouth_coordinates, face_image