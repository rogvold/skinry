import cv2
import numpy as np
import math
import fd

def read_image(fileName, type):
    image = cv2.imread(fileName, type)
    return image

def save_image(image, fileName):
    cv2.imwrite(fileName, image)

def print_time(time1):
    time2 = cv2.getTickCount()
    time = (time2 - time1)/ cv2.getTickFrequency()
    return time

def draw_face(image, result_points):
    for i in range(1, len(result_points)):
        cv2.line(image, result_points[i - 1], result_points[i],  (0, 0, 255), 2)
    return image

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
    black = (255, 255, 255)

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

def delete_unused_keypoints(image, key_points, result_points, eyes_coordinates, nose_coordinates, mouth_coordinates):
    new_kp = []
    dist = 0.03 * max(image.shape[0], image.shape[1])
    min_size = 0.007 * max(image.shape[0], image.shape[1])
    max_size = 0.055 * max(image.shape[0], image.shape[1])

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
    min_size = 40
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

    if length_red == 0:
        length_red = 1
    if length_size == 0:
        length_size = 1

    for kp in key_points:
        x = int(kp.pt[0])
        y = int(kp.pt[1])
        color = original_image[y][x][2] - min_red
        size = kp.size - min_size
        point = 100 + 75 * (float(color) / length_red) + 50 * (float(size) / length_size)
        score += point

    score = int(score)
    return score

def sift(image, contrast_threshold, edge_threshold, sigma):
    sift = cv2.SIFT(0, 5, contrast_threshold, edge_threshold, sigma)
    key_points = sift.detect(image, None)
    return key_points

def get_otsu(image, thresh_val, type):
    #image = cv2.medianBlur(image,5)
    r, image = cv2.threshold(image, thresh_val, 255, type)
    return image

def grid_sift(image, octaves, contrast_thresholds, edge_thresholds, sigmas, delta):
    points = {}
    good_points = []

    for octave in octaves:
        for contrast_threshold in contrast_thresholds:
            for edge_threshold in edge_thresholds:
                for sigma in sigmas:
                    sift = cv2.SIFT(0, octave, contrast_threshold, edge_threshold, sigma)
                    key_points = sift.detect(image, None)
                    for kp in key_points:
                        x = int(kp.pt[0])
                        y = int(kp.pt[1])
                        coords = (x,y)
                        if not points.has_key(coords):
                            points[coords] = [kp, 1]
                        else:
                            points[coords][1] += 1

    for point in points.items():
        if point[1][1] > delta:
            good_points.append(point[1][0])

    return good_points

def grid_otsu(roi, result_points, eyes_coordinates, nose_coordinates, mouth_coordinates,
              threshs, delta):
    points = {}
    good_points = []

    for thresh_val in threshs:
        new_roi = get_otsu(roi, thresh_val, type=cv2.THRESH_TRUNC)

        key_points = sift(new_roi, contrast_threshold=0.02, edge_threshold=10, sigma=1.6)
        #key_points = delete_unused_keypoints(new_roi, key_points, result_points, eyes_coordinates,
        #                                     nose_coordinates, mouth_coordinates)
        for kp in key_points:
            x = int(kp.pt[0])
            y = int(kp.pt[1])
            coords = (x,y)
            if not points.has_key(coords):
                points[coords] = [kp, 1]
            else:
                points[coords][1] += 1

    for point in points.items():
        if point[1][1] > delta:
            good_points.append(point[1][0])

    return good_points

def sift_grid_search(roi, image, result_points, eyes_coordinates, nose_coordinates, mouth_coordinates, **kwargs):
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    roi = get_otsu(roi, **kwargs)

    octaves = [5]
    contrast_thresholds = [0.015, 0.02, 0.025]
    edge_thresholds = [10]
    sigmas = [1.2, 1.4, 1.6, 1.8]

    key_points = grid_sift(roi, octaves, contrast_thresholds, edge_thresholds, sigmas, delta=4)

    key_points = delete_unused_keypoints(roi, key_points, result_points, eyes_coordinates,
                                         nose_coordinates, mouth_coordinates)

    key_points = delete_repeating_points(key_points)

    score = get_score(image, key_points)
    result_image = cv2.drawKeypoints(image, key_points, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    return result_image, score

def otsu_grid_search(roi, image, result_points, eyes_coordinates, nose_coordinates, mouth_coordinates):
    threshs = [160, 190, 200, 210]
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    key_points = grid_otsu(roi, result_points, eyes_coordinates, nose_coordinates, mouth_coordinates, threshs=threshs,
                           delta=1)
    key_points = delete_unused_keypoints(roi, key_points, result_points, eyes_coordinates,
                                         nose_coordinates, mouth_coordinates)
    key_points = delete_repeating_points(key_points)

    score = get_score(image, key_points)
    result_image = cv2.drawKeypoints(image, key_points, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    return result_image, score

def mono_search(roi, image, result_points, eyes_coordinates, nose_coordinates, mouth_coordinates, **kwargs):
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    #roi = get_otsu(roi, thresh_val=135, type=cv2.THRESH_BINARY)
    roi = get_otsu(roi, **kwargs)

    key_points = sift(roi, contrast_threshold=0.02, edge_threshold=10, sigma=1.6)
    key_points = delete_unused_keypoints(roi, key_points, result_points, eyes_coordinates,
                                         nose_coordinates, mouth_coordinates)
    key_points = delete_repeating_points(key_points)

    score = get_score(image, key_points)
    result_image = cv2.drawKeypoints(image, key_points, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    #result_image = roi
    #score = 0

    return result_image, score

def detect_deffects(file_name):
    new_file_name = 'uploads/' + file_name
    time = cv2.getTickCount()
    result_points, eyes_coordinates, nose_coordinates, mouth_coordinates, image = fd.get_param(new_file_name)
    roi = crop_face(image, result_points)
    #roi = crop_limbs(roi, eyes_coordinates, nose_coordinates, mouth_coordinates)

    result_image, score = otsu_grid_search(roi, image, result_points, eyes_coordinates, nose_coordinates, mouth_coordinates)

    #result_image, score = sift_grid_search(roi, image, result_points, eyes_coordinates, nose_coordinates, mouth_coordinates,
    #                                  thresh_val=200, type=cv2.THRESH_TRUNC)

    #result_image, score = mono_search(roi, image, result_points, eyes_coordinates, nose_coordinates, mouth_coordinates,
    #                                  thresh_val=200, type=cv2.THRESH_TRUNC)

    result_image = draw_face(result_image, result_points)

    print 'total score - ' + str(score)
    print 'total time - ' + str(print_time(time))

    return_file_name = 'proc_' + file_name
    new_file_name = 'uploads/' + return_file_name
    save_image(result_image, new_file_name)

    return return_file_name, score

#TODO refactor
#TODO create libraries
#TODO classes?
#TODO sift grid decrease delta
#TODO min and max size???
#TODO combined grid
#TODO limbs in one array
#TODO time optimization
#TODO binary thresholding?
#TODO points alongside contour in the case of bad face recognition (clasterization?)
#TODO play with contrast, brightness, blur
#TODO no filter?
#TODO FAST?
#TODO real deffects near limbs? resize photo?
#TODO cheecks, relief?
#TODO genetic algorythm






