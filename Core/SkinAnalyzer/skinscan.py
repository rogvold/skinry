import sys
import cv2
import cv2.cv
import numpy as np
import math
from matplotlib import pyplot as plt
import fd
JPG = '.jpg'

def read_image(fileName, type):
    image = cv2.imread(fileName, type)
    return image

def save_image(image, fileName):
    cv2.imwrite(fileName, image)

def save_show_image(image, fileName):
    cv2.imwrite(fileName, image)
    cv2.imshow(fileName,image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def print_time(time1):
    time2 = cv2.getTickCount()
    time = (time2 - time1)/ cv2.getTickFrequency()
    print time

def create_BGR_hist(image):
    color = ('B','G','R')
    for i, col in enumerate(color):
        histr = cv2.calcHist([image],[i], None, [256], [0,256])
        plt.plot(histr, color = col)
        plt.xlim([0,256])
    plt.show()

def find_circles(image, type1, type2, min, max):
    cimg = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    circles = cv2.HoughCircles(image, cv2.cv.CV_HOUGH_GRADIENT ,1, 40, type1, type2, min, max)
    circles = np.uint16(np.around(circles))
    for i in circles[0,:]:
        cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
        cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)
    return cimg

def sift(image, contrastThreshold, edgeThreshold, sigma):
    sift = cv2.SIFT(0, 3, contrastThreshold, edgeThreshold, sigma)
    key_points = sift.detect(image, None)
    return key_points


def crop_face(image, result_points):
    mask = np.zeros(image.shape, dtype=np.uint8)
    white = (255, 255, 255)

    corners = []
    for point in result_points:
        corners.append((point[0], point[1]))

    roi_corners = np.array([corners], dtype=np.int32)
    cv2.fillPoly(mask, roi_corners, white)
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image

def crop_limbs(masked_image, eyes_coordinates, nose_coordinates, mouth_coordinates):
    black = (0, 0, 0)

    from_y = nose_coordinates[1]
    to_y = from_y + nose_coordinates[3]
    from_x = nose_coordinates[0]
    to_x = from_x + nose_coordinates[2]
    masked_image[from_y:to_y, from_x:to_x] = black

    width = mouth_coordinates[3]
    alpha = 0.2

    from_y = mouth_coordinates[1]
    to_y = from_y + mouth_coordinates[3]
    from_x = mouth_coordinates[0] - alpha * width
    to_x = from_x + mouth_coordinates[2] + 2 * alpha * width
    masked_image[from_y:to_y, from_x:to_x] = black

    width = max(eyes_coordinates[0][3], eyes_coordinates[1][3])
    height = max(eyes_coordinates[0][2], eyes_coordinates[1][2])
    alpha = 0.1
    beta = 0.3

    from_y = eyes_coordinates[0][1] - beta * height
    to_y = from_y + eyes_coordinates[0][3] + 2 * beta * height
    from_x = eyes_coordinates[0][0] - alpha * width
    to_x = from_x + eyes_coordinates[0][2] + 2 * alpha * width
    masked_image[from_y:to_y, from_x:to_x] = black

    from_y = eyes_coordinates[1][1] - beta * height
    to_y = from_y + eyes_coordinates[1][3] + 2 * beta * height
    from_x = eyes_coordinates[1][0] - alpha * width
    to_x = from_x + eyes_coordinates[1][2] + 2 * alpha * width
    masked_image[from_y:to_y, from_x:to_x] = black

    return masked_image

def get_otsu(image):
    #image = cv2.medianBlur(image,5)
    r, image = cv2.threshold(image, 200, 255, cv2.THRESH_TRUNC)
    return image

def check_border(x, y, result_points):
    for i in range(0, len(result_points) - 1):
        x1 = result_points[i][0]
        x2 = result_points[i + 1][0]
        y1 = result_points[i][1]
        y2 = result_points[i + 1][1]
        h = abs(((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)) / (math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))))
        if h < 20:
            return True
    return False

def check_border1(x, y, result_points):
    for point in result_points:
        if ((x - point[0]) * (x - point[0]) + (y - point[1]) * (y - point[1])) < 400:
            return True
    return False

def delete_unused_keypoints(key_points, result_points, eyes_coordinates, nose_coordinates, mouth_coordinates, image, original_image):
    new_kp = []
    max_red = 0
    min_red = 255
    max_size = 0
    min_size = 40
    score = 0

    for kp in key_points:
        if kp.size < 5 or kp.size > 40:
            new_kp.append(kp)
            continue

        x = round(kp.pt[0])
        y = round(kp.pt[1])

        if image[y][x] == 0:
           new_kp.append(kp)
           continue

        from_y = nose_coordinates[1]
        to_y = from_y + nose_coordinates[3]
        from_x = nose_coordinates[0]
        to_x = from_x + nose_coordinates[2]
        if x > from_x and x < to_x and y > from_y and y < to_y:
            new_kp.append(kp)
            continue

        width = mouth_coordinates[3]
        alpha = 0.2

        from_y = mouth_coordinates[1]
        to_y = from_y + mouth_coordinates[3]
        from_x = mouth_coordinates[0] - alpha * width
        to_x = from_x + mouth_coordinates[2] + 2 * alpha * width
        if x > from_x and x < to_x and y > from_y and y < to_y:
            new_kp.append(kp)
            continue

        width = max(eyes_coordinates[0][3], eyes_coordinates[1][3])
        height = max(eyes_coordinates[0][2], eyes_coordinates[1][2])
        alpha = 0.1
        beta = 0.3

        from_y = eyes_coordinates[0][1] - beta * height
        to_y = from_y + eyes_coordinates[0][3] + 2 * beta * height
        from_x = eyes_coordinates[0][0] - alpha * width
        to_x = from_x + eyes_coordinates[0][2] + 2 * alpha * width
        if x > from_x and x < to_x and y > from_y and y < to_y:
            new_kp.append(kp)
            continue

        from_y = eyes_coordinates[1][1] - beta * height
        to_y = from_y + eyes_coordinates[1][3] + 2 * beta * height
        from_x = eyes_coordinates[1][0] - alpha * width
        to_x = from_x + eyes_coordinates[1][2] + 2 * alpha * width
        if x > from_x and x < to_x and y > from_y and y < to_y:
            new_kp.append(kp)
            continue

        if check_border(x, y, result_points):
            new_kp.append(kp)
            continue

        size = kp.size
        color =  original_image[y][x][2]
        if color > max_red:
            max_red = color
        if color < min_red:
            min_red = color
        if size > max_size:
            max_size = size
        if size < min_size:
            min_size = size

    length_red = max_red - min_red
    length_size = max_size - min_size
    key_points = list(set(key_points) - set(new_kp))

    for kp in key_points:
        x = round(kp.pt[0])
        y = round(kp.pt[1])
        color = original_image[y][x][2] - min_red
        size = kp.size - min_size
        point = 100 + 75 * (float(color) / length_red) + 50 * (float(size) / length_size)
        print point
        score += point

    score = int(score)
    return key_points, score

def detect_deffects(file_name):
    new_file_name = 'uploads/' + file_name
    result_points, eyes_coordinates, nose_coordinates, mouth_coordinates, image = fd.get_param(new_file_name)
    roi = crop_face(image, result_points)
    roi = crop_limbs(roi, eyes_coordinates, nose_coordinates, mouth_coordinates)

    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    roi = get_otsu(roi)

    key_points = sift(roi, contrastThreshold=0.02, edgeThreshold=15, sigma=2)
    key_points, score = delete_unused_keypoints(key_points, result_points, eyes_coordinates, nose_coordinates, mouth_coordinates, roi, image)
    result_image = cv2.drawKeypoints(image, key_points, flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    print 'total score - ' + str(score)

    new_file_name = 'uploads/' + 'face' + file_name
    save_image(result_image, new_file_name)
    return 'face' + file_name

#detect_deffects('1.jpg')