import numpy as np
import cv2
import sys
import math

def crop_limbs(masked_image, limbs):
    black = (255, 255, 255)
    nose_coordinates = limbs[0]
    mouth_coordinates = limbs[1]
    eyes_coordinates = limbs[2]

    from_x, to_x, from_y, to_y = get_coords(nose_coordinates, alpha=0, beta=0,
                                            width=nose_coordinates[2], height=0)
    masked_image[from_y:to_y, from_x:to_x] = black

    from_x, to_x, from_y, to_y = get_coords(mouth_coordinates, alpha=0.15, beta=0,
                                            width=mouth_coordinates[2], height=0)
    masked_image[from_y:to_y, from_x:to_x] = black

    cur_width = max(eyes_coordinates[0][2], eyes_coordinates[1][2])
    cur_height = max(eyes_coordinates[0][3], eyes_coordinates[1][3])

    from_x, to_x, from_y, to_y = get_coords(eyes_coordinates[0], alpha=0.2, beta=0,
                                            width=cur_width, height=cur_height)
    masked_image[from_y:to_y, from_x:to_x] = black

    from_x, to_x, from_y, to_y = get_coords(eyes_coordinates[1], alpha=0.2, beta=0,
                                            width=cur_width, height=cur_height)
    masked_image[from_y:to_y, from_x:to_x] = black

    return masked_image

def get_coords(array, alpha, beta, width, height):
    from_y = array[1] - beta * height
    to_y = from_y + array[3] + 2 * beta * height
    from_x = array[0] - alpha * width
    to_x = from_x + array[2] + 2 * alpha * width
    return int(from_x), int(to_x), int(from_y),int(to_y)

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

def check_border(x, y, result_points, dist):
    for i in range(0, len(result_points) - 1):
        x1 = result_points[i][0]
        x2 = result_points[i + 1][0]
        y1 = result_points[i][1]
        y2 = result_points[i + 1][1]
        if is_close(x, y, x1, y1, x2, y2, dist):
            return True

    x1 = result_points[0][0]
    x2 = result_points[len(result_points) - 1][0]
    y1 = result_points[0][1]
    y2 = result_points[len(result_points) - 1][1]
    if is_close(x, y, x1, y1, x2, y2, dist):
        return True

    return False

def delete_unused_keypoints(image, key_points, result_points, limbs):
    new_kp = []
    dist = 0.03 * max(image.shape[0], image.shape[1])
    print round(0.007 * max(image.shape[0], image.shape[1]))
    min_size = max(3.0, round(0.007 * max(image.shape[0], image.shape[1])))
    max_size = 0.055 * max(image.shape[0], image.shape[1])
    nose_coordinates = limbs[0]
    mouth_coordinates = limbs[1]
    eyes_coordinates = limbs[2]

    for kp in key_points:
        if kp.size < min_size or kp.size > max_size:
            new_kp.append(kp)
            continue

        x = int(kp.pt[0])
        y = int(kp.pt[1])

        if image[y][x] == 0:
           new_kp.append(kp)
           continue

        cur_width = nose_coordinates[2]
        cur_height = nose_coordinates[3]

        from_x, to_x, from_y, to_y = get_coords(nose_coordinates, alpha=0, beta=0,
                                                width=cur_width, height=cur_height)
        if to_x > x > from_x and to_y > y > from_y:
            new_kp.append(kp)
            continue

        cur_height = mouth_coordinates[3]
        cur_width = mouth_coordinates[2]

        from_x, to_x, from_y, to_y = get_coords(mouth_coordinates, alpha=0.15, beta=0,
                                                width=cur_width, height=cur_height)
        if to_x > x > from_x and to_y > y > from_y:
            new_kp.append(kp)
            continue

        cur_width = max(eyes_coordinates[0][2], eyes_coordinates[1][2])
        cur_height = max(eyes_coordinates[0][3], eyes_coordinates[1][3])

        from_x, to_x, from_y, to_y = get_coords(eyes_coordinates[0], alpha=0.2, beta=0,
                                                width=cur_width, height=cur_height)
        if to_x > x > from_x and to_y > y > from_y:
            new_kp.append(kp)
            continue

        from_x, to_x, from_y, to_y = get_coords(eyes_coordinates[1], alpha=0.2, beta=0,
                                                width=cur_width, height=cur_height)
        if to_x > x > from_x and to_y > y > from_y:
            new_kp.append(kp)
            continue

        if check_border(x, y, result_points, dist=dist):
            new_kp.append(kp)
            continue

    key_points = list(set(key_points) - set(new_kp))
    return key_points

def delete_repeating_points(good_points):
    repeating_points = []

    for kp1 in good_points:
        for kp2 in good_points:
            if kp1 != kp2:
                x1 = int(kp1.pt[0])
                y1 = int(kp1.pt[1])
                x2 = int(kp2.pt[0])
                y2 = int(kp2.pt[1])
                dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                if dist < kp1.size and kp1.size > kp2.size:
                    repeating_points.append(kp1)

    good_points = list(set(good_points) - set(repeating_points))

    return good_points

def get_score(original_image, key_points):
    max_red = 0
    min_red = 255
    max_size = 0
    min_size = 255
    score = 0

    for kp in key_points:
        x = int(kp.pt[0])
        y = int(kp.pt[1])

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

    for kp in key_points:
        x = int(kp.pt[0])
        y = int(kp.pt[1])
        color = original_image[y][x][2] - min_red
        size = kp.size - min_size
        red_score = 0
        size_score = 0.0

        if length_size == 0:
            size_score = 25.0
        else:
            size_score = 25 * (float(size) / length_size)

        if length_red == 0:
            red_score = 25.0
        else:
            red_score = 25 * (float(color) / length_red)

        point = 50 + red_score + size_score
        score += point

    score = int(score)
    return score



