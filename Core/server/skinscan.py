import sys
import cv2
import cv2.cv
import cv
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

def print_time(time1):
    time2 = cv2.getTickCount()
    time = (time2 - time1)/ cv2.getTickFrequency()
    return time

def sift(image, contrast_threshold, edge_threshold, sigma):
    sift = cv2.SIFT(0, 3, contrast_threshold, edge_threshold, sigma)
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

def get_coords(array, alpha, beta, width, height):
    from_y = array[1] - beta * height
    to_y = from_y + array[3] + 2 * beta * height
    from_x = array[0] - alpha * width
    to_x = from_x + array[2] + 2 * alpha * width
    return int(from_x), int(to_x), int(from_y),int(to_y)

def crop_limbs(masked_image, eyes_coordinates, nose_coordinates, mouth_coordinates):
    black = (0, 0, 0)

    from_x, to_x, from_y, to_y = get_coords(nose_coordinates, alpha=0, beta=0, width=0, height=0)
    masked_image[from_y:to_y, from_x:to_x] = black

    from_x, to_x, from_y, to_y = get_coords(mouth_coordinates, alpha=0.2, beta=0, width=mouth_coordinates[2], height=0)
    masked_image[from_y:to_y, from_x:to_x] = black

    cur_width = max(eyes_coordinates[0][2], eyes_coordinates[1][2])
    cur_height = max(eyes_coordinates[0][3], eyes_coordinates[1][3])

    from_x, to_x, from_y, to_y = get_coords(eyes_coordinates[0], alpha=0.1, beta=0.3, width=cur_width, height=cur_height)
    masked_image[from_y:to_y, from_x:to_x] = black

    from_x, to_x, from_y, to_y = get_coords(eyes_coordinates[1], alpha=0.1, beta=0.3, width=cur_width, height=cur_height)
    masked_image[from_y:to_y, from_x:to_x] = black

    return masked_image

def get_otsu(image, thresh_val, max_val):
    #image = cv2.medianBlur(image,5)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    r, image = cv2.threshold(image, thresh_val, max_val, cv2.THRESH_TRUNC)
    return image

def is_close(x, y, x1, y1, x2, y2, dist):
    h = 0
    sc = (x2 - x1) * (x - x1) + (y - y1) * (y2 - y1)
    if sc <= 0:
        h = math.sqrt((x - x1)**2 + (y - y1)**2)
    else:
        if (x2 - x1)**2 + (y2 - y1)**2 <= sc:
            h = math.sqrt((x - x2)**2 + (y - y2)**2)
        else:
            h = abs(((x1 - x2) * (y - y1) + (y2 - y1) * (x - x1)) / (math.sqrt((x2 - x1)**2 + (y2 - y1)**2)))
    return h < dist

def check_border(x, y, result_points):
    for i in range(0, len(result_points) - 1):
        x1 = result_points[i][0]
        x2 = result_points[i + 1][0]
        y1 = result_points[i][1]
        y2 = result_points[i + 1][1]
        if is_close(x, y, x1, y1, x2, y2, dist=25.0):
            return True

    x1 = result_points[0][0]
    x2 = result_points[len(result_points) - 1][0]
    y1 = result_points[0][1]
    y2 = result_points[len(result_points) - 1][1]
    if is_close(x, y, x1, y1, x2, y2, dist=25.0):
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

        x = int(kp.pt[0])
        y = int(kp.pt[1])

        if image[y][x] == 0:
           new_kp.append(kp)
           continue

        cur_width = nose_coordinates[2]
        cur_height = nose_coordinates[3]

        from_x, to_x, from_y, to_y = get_coords(nose_coordinates, alpha=0.2, beta=0.2, width=cur_width, height=cur_height)
        if to_x > x > from_x and to_y > y > from_y:
            new_kp.append(kp)
            continue

        cur_height = mouth_coordinates[3]
        cur_width = mouth_coordinates[2]

        from_x, to_x, from_y, to_y = get_coords(mouth_coordinates, alpha=0.25, beta=0.2, width=cur_width, height=cur_height)
        if to_x > x > from_x and to_y > y > from_y:
            new_kp.append(kp)
            continue

        cur_width = max(eyes_coordinates[0][2], eyes_coordinates[1][2])
        cur_height = max(eyes_coordinates[0][3], eyes_coordinates[1][3])

        from_x, to_x, from_y, to_y = get_coords(eyes_coordinates[0], alpha=0.15, beta=0.35, width=cur_width, height=cur_height)
        if to_x > x > from_x and to_y > y > from_y:
            new_kp.append(kp)
            continue

        from_x, to_x, from_y, to_y = get_coords(eyes_coordinates[1], alpha=0.15, beta=0.35, width=cur_width, height=cur_height)
        if to_x > x > from_x and to_y > y > from_y:
            new_kp.append(kp)
            continue

        if check_border(x, y, result_points):
            new_kp.append(kp)
            continue

        size = kp.size
        color = original_image[y][x][2]
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
        x = int(kp.pt[0])
        y = int(kp.pt[1])
        color = original_image[y][x][2] - min_red
        size = kp.size - min_size
        point = 100 + 75 * (float(color) / length_red) + 50 * (float(size) / length_size)
        score += point

    score = int(score)
    return key_points, score

def detect_deffects(file_name):
    new_file_name = 'uploads/' + file_name
    time = cv2.getTickCount()
    result_points, eyes_coordinates, nose_coordinates, mouth_coordinates, image = fd.get_param(new_file_name)
    roi = crop_face(image, result_points)
    roi = crop_limbs(roi, eyes_coordinates, nose_coordinates, mouth_coordinates)

    roi = get_otsu(roi, 200, 255)

    key_points = sift(roi, contrast_threshold=0.02, edge_threshold=15, sigma=2)
    key_points, score = delete_unused_keypoints(key_points, result_points, eyes_coordinates, nose_coordinates, mouth_coordinates, roi, image)
    result_image = cv2.drawKeypoints(image, key_points, flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    print 'total score - ' + str(score)
    print 'total time - ' + str(print_time(time))

    return_file_name = 'proc_' + file_name
    new_file_name = 'uploads/' + return_file_name
    save_image(result_image, new_file_name)
    return return_file_name, score