import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
import cv2
import cv2.cv as cv
import sys
from scipy import ndimage

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
    faces = []

    for i, angle in enumerate([0, 90, 180, 270]):
        gray_angle = ndimage.rotate(gray, angle)
        
        to_do = True
        for sf in [1.1, 1.01]:
            if to_do == False:
                break
            for mn in [3, 5, 7]:
                face = face_cascade.detectMultiScale(gray_angle, sf, mn, cv2.cv.CV_HAAR_SCALE_IMAGE, (H / 8, W / 8))
                if mn == 3 and sf == 1.1:
                    faces.append(face)
                if len(face) > 0:
                    faces[i] = face
                    to_do = False
                    break

    is_face = False
    for face in faces:
        if len(face) > 0:
            is_face = True
            break
    if is_face == False:
        raise ValueError('Error: No face. May be your eyes are closed')

    #getting face, eyes, nose, mouth
    for i, face in enumerate(faces):
        for (x,y,w,h) in face:
            y -= 0.1 * (y + h / 2)
            h += 0.2 * (y + h / 2)
            y = max(int(y), 0)
            h = min(int(h), H - 1 - y)

            if H * W > 10 * h * w:
                break

            img = ndimage.rotate(img, 90 * i)
            gray = ndimage.rotate(gray, 90 * i)

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

            return roi, eyes_coordinates, nose_coordinates, mouth_coordinates

    raise ValueError('Face is too small')


def define_contours(img):
    train = pd.read_csv('train.csv')[:3000]
    X_train = np.asarray(train[range(0, 3)])
    Y_train = np.asarray(train[[3]]).ravel()

    estimator = KNeighborsClassifier(n_neighbors = 3, weights = 'distance')
    estimator.fit(X_train, Y_train)

    r, g, b = cv2.split(img)
    h, w = img.shape[:2]
    delta = h / 30

    j = 1 + delta
    points = []
    points.append((int(0.4 * w), 20))
    points.append((int(0.6 * w), 20))

    for i in range(1, 30):
        test = zip(b[j], g[j], r[j])
        res = estimator.predict(test)
        x1 = x2 = -1

        count = 0
        for k in range(int(0.5 * w), w):
            if res[k] == 1:
                count += 1
                if count > 30:
                    x2 = k
            else:
                count = 0

        count = 0
        for k in range(int(w / 2), -1, -1):
            if res[k] == 1:
                count += 1
                if count > 30:
                    x1 = k
            else:
                count = 0


        if x1 >= 10:
            points.append((x1, j))
        if x2 > -1 and x2 <= w - 9:
            points.append((x2, j))

        if i == 28:
            j = h - 20
        else:
            j += delta

    points.append((int(0.4 * w), h - 1))
    points.append((int(0.6 * w), h - 1))

    points = grahamscan(points)

    return points

def get_right_x(center, axes, y):
    return int(center[0] + axes[0] * pow(1.0 - 1.0 * (center[1] -
        y) * (center[1] - y) / (axes[1] * axes[1]), 0.5))

def get_left_x(center, axes, y):
    return int(center[0] - axes[0] * pow(1.0 - 1.0 * (center[1] -
        y) * (center[1] - y) / (axes[1] * axes[1]), 0.5))

def change_points(img, points, border1 = 5, border2 = 2):
    center = (img.shape[1] / 2, img.shape[0] / 2)
    axes = (int(0.45 * img.shape[1]), int(0.48 * img.shape[0]))

    dic = dict()
    for p in points:
        if dic.get(p[1]) == None:
            dic[p[1]] = (p[0], -1)
        else:
            dic[p[1]] = (p[0], dic[p[1]][0])

    h, w = img.shape[:2]
    delta = h / 30
    j = 1 + delta
    count_left = 0
    count_right = 0
    result_points = []
    result_points.append((int(0.4 * w), 1))
    result_points.append((int(0.6 * w), 1))

    for i in range(1, 30):
        if j > h * 0.25 and j < h * 0.75:
            border = border1
        else:
            border = border2
        if abs(j - h / 2) < axes[1]:
            val = dic.get(j)
            if val == None:
                count_left += 1
                count_right += 1
            else:
                if val[0] == -1:
                    if val[1] == -1:
                        count_left += 1
                        count_right += 1
                    else:
                        if val[1] > w / 2:
                            count_right = 0
                            count_left += 1
                            x = get_right_x(center, axes, j)
                            if abs(x - val[1]) > 1.0 * w / border:
                                result_points.append((int(x), j))
                            else:
                                result_points.append((val[1], j))
                        else:
                            count_left = 0
                            count_right += 1
                            x = get_left_x(center, axes, j)
                            if abs(x - val[1]) > 1.0 * w / border:
                                result_points.append((int(x), j))
                            else:
                                result_points.append((val[1], j))
                else:
                    if val[1] == -1:
                        if val[0] > w / 2:
                            count_right = 0
                            count_left += 1
                            x = get_right_x(center, axes, j)
                            if abs(x - val[0]) > 1.0 * w / border:
                                result_points.append((int(x), j))
                            else:
                                result_points.append((val[0], j))
                        else:
                            count_left = 0
                            count_right += 1
                            x = get_left_x(center, axes, j)
                            if abs(x - val[0]) > 1.0 * w / border:
                                result_points.append((int(x), j))
                            else:
                                result_points.append((val[0], j))
                    else:
                        count_right = 0
                        count_left = 0
                        if val[0] > val[1]:
                            val = (val[1], val[0])
                        x = get_right_x(center, axes, j)
                        if abs(x - val[1]) > 1.0 * w / border:
                            result_points.append((int(x), j))
                        else:
                            result_points.append((val[1], j))
                        x = get_left_x(center, axes, j)
                        if abs(x - val[0]) > 1.0 * w / border:
                            result_points.append((int(x), j))
                        else:
                            result_points.append((val[0], j))

            if count_left > 10:
                x = get_left_x(center, axes, j)
                result_points.append((int(x), j))
                count_left = 0
            if count_right > 10:
                x = get_right_x(center, axes, j)
                result_points.append((int(x), j))
                count_right = 0
        else:
            val = dic.get(j)
            if val != None:
                if val[0] != -1:
                    result_points.append((val[0], j))
                if val[1] != -1:
                    result_points.append((val[1], j))

        if i == 28:
            j = h - 20
        else:
            j += delta

    result_points.append((int(0.4 * w), h - 1))
    result_points.append((int(0.6 * w), h - 1))

    result_points = grahamscan(result_points)

    return result_points

def resize(img):
    shape = img.shape
    min_shape = min(shape[0], shape[1])

    if min_shape > 1000:
        coef = 1000.0 / min_shape
        img = cv2.resize(img, (0,0), fx=coef, fy=coef)

    return img

def get_param(file_name):
    img = cv2.imread(file_name)
    if img == None:
        raise ValueError('No image' + file_name)
    img = resize(img)
    face_image, eyes_coordinates, nose_coordinates, mouth_coordinates = detect_face_and_organs(img)
    # 'result_points' - array of contour's points
    result_points = define_contours(face_image)
    result_points = change_points(face_image, result_points)
    
    return result_points, eyes_coordinates, nose_coordinates, mouth_coordinates, face_image