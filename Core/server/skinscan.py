import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import fd
import kpproc

def read_image(fileName, type):
    image = cv2.imread(fileName, type)
    return image

def save_image(image, fileName):
    cv2.imwrite(fileName, image)

def print_time(time1):
    time2 = cv2.getTickCount()
    time = (time2 - time1) / cv2.getTickFrequency()
    return time

def draw_face(image, result_points):
    for i in range(1, len(result_points)):
        cv2.line(image, result_points[i - 1], result_points[i],  (0, 0, 255), 2)
    cv2.line(image, result_points[0], result_points[len(result_points) - 1],  (0, 0, 255), 2)
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

def change_constrast(image, alpha, beta):
    array_alpha = np.array([alpha])
    array_beta = np.array([beta])

    cv2.add(image, array_beta, image)
    cv2.multiply(image, array_alpha, image)

    return image

def sift(image, contrast_threshold, edge_threshold, sigma):
    sift = cv2.SIFT(0, 5, contrast_threshold, edge_threshold, sigma)
    key_points = sift.detect(image, None)
    return key_points

def get_blur(image, param=5):
    image = cv2.medianBlur(image, param)
    return image

def get_otsu(image, thresh_val, type):
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

def grid_otsu(roi,threshs, delta):
    points = {}
    good_points = []

    for thresh_val in threshs:
        new_roi = get_otsu(roi, thresh_val, type=cv2.THRESH_TRUNC)

        key_points = sift(new_roi, contrast_threshold=0.02, edge_threshold=10, sigma=1.6)
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

def sift_grid_search(roi, image, result_points, limbs, **kwargs):
    roi = change_constrast(roi, 2.0, -70.0)
    roi = get_blur(roi, 9)
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    roi = get_otsu(roi, **kwargs)

    octaves = [5]
    contrast_thresholds = [0.02, 0.025]
    edge_thresholds = [10]
    sigmas = [1.2, 1.6]

    key_points = grid_sift(roi, octaves, contrast_thresholds, edge_thresholds, sigmas, delta=2)
    key_points = kpproc.delete_unused_keypoints(roi, key_points, result_points, limbs)
    key_points = kpproc.delete_repeating_points(key_points)

    score = kpproc.get_score(image, key_points)
    result_image = cv2.drawKeypoints(image, key_points, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    return result_image, score

def otsu_grid_search(roi, image, result_points, limbs):
    threshs = [220, 230, 240]
    roi = change_constrast(roi, alpha=2.0, beta=-70.0)
    roi = get_blur(roi, 9)
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    key_points = grid_otsu(roi, threshs, delta=2)
    key_points = kpproc.delete_unused_keypoints(roi, key_points, result_points, limbs)
    key_points = kpproc.delete_repeating_points(key_points)

    score = kpproc.get_score(image, key_points)
    result_image = cv2.drawKeypoints(image, key_points, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    return result_image, score

def mono_search(roi, image, result_points, limbs, **kwargs):
    roi = change_constrast(roi, alpha=2.0, beta=-70.0)
    roi = get_blur(roi, 9)

    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    #roi = get_otsu(roi, thresh_val=135, type=cv2.THRESH_BINARY)
    roi = get_otsu(roi, **kwargs)

    key_points = sift(roi, contrast_threshold=0.02, edge_threshold=10, sigma=1.6)
    key_points = kpproc.delete_unused_keypoints(roi, key_points, result_points, limbs)
    key_points = kpproc.delete_repeating_points(key_points)

    score = kpproc.get_score(image, key_points)
    result_image = cv2.drawKeypoints(image, key_points, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    #result_image = roi
    #score = 0

    return result_image, score

def process_photo(file_name):
    result_points, eyes_coordinates, nose_coordinates, mouth_coordinates, image = fd.get_param(file_name)
    roi = crop_face(image, result_points)
    limbs = [nose_coordinates, mouth_coordinates, eyes_coordinates]

    #roi = kpproc.crop_limbs(roi, limbs)

    #result_image, score = otsu_grid_search(roi, image, result_points, limbs)
    result_image, score = sift_grid_search(roi, image, result_points, limbs, thresh_val=220, type=cv2.THRESH_TRUNC)
    #result_image, score = mono_search(roi, image, result_points, limbs, thresh_val=220, type=cv2.THRESH_TRUNC)

    result_image = draw_face(result_image, result_points)

    return result_image, score

def process_files(name):
    who_folders = os.listdir(name)

    for who_folder in who_folders:
        num_folders = os.listdir(name + '/' + who_folder)

        for num_folder in num_folders:
            files = os.listdir(name + '/' + who_folder + '/' + num_folder)

            for file in files:
                if not 'proc_' in file:
                    path = name + '/' + who_folder + '/' + num_folder + '/'
                    file_name = path + file
                    try:
                        image, score = process_photo(file_name)
                        new_file_name = path + 'proc_otsugrid_contrast' + file
                        save_image(image, new_file_name)
                    except ValueError:
                        print file_name + '_ERROR'

def detect_deffects(file_name):
    new_file_name = 'uploads/' + file_name
    time = cv2.getTickCount()

    result_image, score = process_photo(new_file_name)

    print 'total score - ' + str(score)
    print 'total time - ' + str(print_time(time))

    return_file_name = 'proc_' + file_name
    new_file_name = 'uploads/' + return_file_name
    save_image(result_image, new_file_name)

    return return_file_name, score

#process_files('photo')
#detect_deffects('1.jpg')

#TODO contrast params, need grid?, new otsu and sift params
#TODO time optimization
#TODO median blur
#TODO combined grid
#TODO binary thresholding?
#TODO get contrast with hist

#TODO points alongside contour in the case of bad face recognition (clasterization?)
#TODO FAST?
#TODO real deffects near limbs? resize photo?
#TODO cheecks, relief?
#TODO genetic algorythm






