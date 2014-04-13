import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import fd
import kpproc

def read_image(fileName, type=cv2.IMREAD_COLOR):
    """
    Read the image and return Image object

    Input: string fileName and the type of color
    """

    image = cv2.imread(fileName, type)

    return image

def save_image(image, fileName):
    """
    Save the image

    Input: image and the future fileName of the image
    """

    cv2.imwrite(fileName, image)

def print_time(time1):
    """
    Count the time of end of algorithm and return it

    Input: the time of start of algorithm
    """

    time2 = cv2.getTickCount()
    time = (time2 - time1) / cv2.getTickFrequency()

    return time

def draw_face(image, result_points):
    """
    Draw the contour of face and return processed image

    Input: image and array of points
    """

    for i in range(1, len(result_points)):
        cv2.line(image, result_points[i - 1], result_points[i],  (0, 0, 255), 2)
    cv2.line(image, result_points[0], result_points[len(result_points) - 1],  (0, 0, 255), 2)

    return image

def draw_circles(image, key_points):
    """
    Draw keyPoints and return processed image

    Input: image and array of keyPoints
    """

    for kp in key_points:
        x = int(kp.pt[0])
        y = int(kp.pt[1])
        center = (x, y)
        size = int(kp.size / 2)
        cv2.circle(image, center, size, (255, 0, 0), 1)

    return image

def crop_face(image, result_points):
    """
    Fill the everything except face with black color, return processed image

    Input: image and array of points (contour)
    """

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
    """
    Change the contrast of image, return processed image

    Input: image, contrast coefficient and brightness coefficient
    """

    array_alpha = np.array([alpha])
    array_beta = np.array([beta])

    cv2.add(image, array_beta, image)
    cv2.multiply(image, array_alpha, image)

    return image

def contrast_val(image):
    """
    Return suitable contrast value

    Input: image
    """

    bins = range(170, 230)
    hist,bins = np.histogram(image.ravel(), bins, [0, 256])
    summ = hist.sum()

    if summ < 100000:
        return 1.7
    else:
        return 1.6

def sift(image, contrast_threshold=0.025, edge_threshold=5, sigma=1.0):
    """
    Detect image features, return array of keyPoints

    Input:
        image
        contrast_threshold (as bigger, as more keyPoints will be found)
        edge_threshold (as bigger, as less keyPoints will be found)
        sigma (small values for low-quality photos)
    """

    sift = cv2.SIFT(0, 5, contrast_threshold, edge_threshold, sigma)
    key_points = sift.detect(image, None)
    return key_points

def get_blur(image, param=5):
    """
    Return blurred image

    Input:
        image
        param (big values for more blur)
    """

    image = cv2.medianBlur(image, param)

    return image

def get_otsu(image, thresh_val=220, type=cv2.THRESH_TRUNC):
    """
    Return image with otsu filter

    Input:
        image
        thresh_val (as less, as stronger effect will be)
        type (cv2.THRESH_TRUNC or cv2.THRESH_BINARY)
    """

    r, image = cv2.threshold(image, thresh_val, 255, type)

    return image

def grid_sift(image, contrast_thresholds, edge_thresholds, sigmas, delta):
    """
    Sorting of sift parameters, return most popular keyPoints

    Input:
        image
        contrast thresholds, edge_thresholds, simgas (see 'sift' docs)
        delta (if keyPoint repeats more than delta times, it will be goodPoint)
    """

    points = {}
    good_points = []

    for contrast_threshold in contrast_thresholds:
        for edge_threshold in edge_thresholds:
            for sigma in sigmas:
                key_points = sift(image, contrast_threshold, edge_threshold, sigma)
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
    """
    Algorithm based on sorting parameters of sift, return processed image and skin score

    Input:
        roi (cropped image)
        image (original image)
        result_points (array of points - contour)
        limbs (array of face limbs coordinates)
        kwargs (otsu parameters)
    """

    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    alpha = contrast_val(roi)
    roi = change_constrast(roi, alpha=alpha, beta=-70.0)

    #roi = get_blur(roi, 3)
    roi = get_otsu(roi, **kwargs)

    contrast_thresholds = [0.02, 0.025]
    edge_thresholds = [5]
    sigmas = [1.2, 1.4, 1.6]

    key_points1 = grid_sift(roi, contrast_thresholds, edge_thresholds, sigmas, delta=3)
    key_points2 = sift(roi, contrast_threshold=0.035, edge_threshold=5, sigma=1.0)

    key_points = key_points1 + key_points2

    key_points = kpproc.delete_unused_keypoints(roi, key_points, result_points, limbs)
    key_points = kpproc.delete_repeating_points(key_points)

    score = kpproc.get_score(image, key_points)
    result_image = draw_circles(image, key_points)

    return result_image, score

def grid_otsu(roi, threshs, delta, **kwargs):
    """
    Sorting of otsu parameters, return most popular keyPoints

    Input:
        image
        thresh (see 'otsu' docs)
        delta (if keyPoint repeats more than delta times, it will be goodPoint)
    """

    points = {}
    good_points = []

    for thresh_val in threshs:
        new_roi = get_otsu(roi, thresh_val, type=cv2.THRESH_TRUNC)
        key_points = sift(new_roi, **kwargs)
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

def otsu_grid_search(roi, image, result_points, limbs, **kwargs):
    """
    Algorithm based on sorting parameters of otsu, return processed image and skin score

    Input:
        roi (cropped image)
        image (original image)
        result_points (array of points - contour)
        limbs (array of face limbs coordinates)
    """

    threshs = [190, 200, 210]
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    alpha = contrast_val(roi)
    roi = change_constrast(roi, alpha=alpha, beta=-70.0)

    #roi = get_blur(roi, 3)

    key_points = grid_otsu(roi, threshs, delta=2, **kwargs)
    key_points = kpproc.delete_unused_keypoints(roi, key_points, result_points, limbs)
    key_points = kpproc.delete_repeating_points(key_points)

    score = kpproc.get_score(image, key_points)
    result_image = draw_circles(image, key_points)

    return result_image, score

def mono_search(roi, image, result_points, limbs, **kwargs):
    """
    Algorithm based on simple sift and otsu, return processed image and skin score

    Input:
        roi (cropped image)
        image (original image)
        result_points (array of points - contour)
        limbs (array of face limbs coordinates)
        kwargs (otsu parameters)
    """

    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    alpha = contrast_val(roi)
    roi = change_constrast(roi, alpha=alpha, beta=-70.0)

    #roi = get_blur(roi, 3)
    #roi = get_otsu(roi, thresh_val=135, type=cv2.THRESH_BINARY)

    roi = get_otsu(roi, **kwargs)

    key_points = sift(roi, contrast_threshold=0.035, edge_threshold=5, sigma=1.0)
    key_points = kpproc.delete_unused_keypoints(roi, key_points, result_points, limbs)
    key_points = kpproc.delete_repeating_points(key_points)

    score = kpproc.get_score(image, key_points)
    result_image = draw_circles(image, key_points)

    #result_image = roi
    #score = 0

    return result_image, score

def process_photo(file_name):
    """
    Process photo, use one of the above algorithms, return processed image and skin score

    Input: fileName
    """

    result_points, eyes_coordinates, nose_coordinates, mouth_coordinates, image = fd.get_param(file_name)
    roi = crop_face(image, result_points)
    limbs = [nose_coordinates, mouth_coordinates, eyes_coordinates]

    #result_image, score = otsu_grid_search(roi, image, result_points, limbs,
    #                                       contrast_threshold=0.02, edge_threshold=10, sigma=1.6)
    result_image, score = sift_grid_search(roi, image, result_points, limbs, thresh_val=220, type=cv2.THRESH_TRUNC)
    #result_image, score = mono_search(roi, image, result_points, limbs, thresh_val=220, type=cv2.THRESH_TRUNC)

    result_image = draw_face(result_image, result_points)

    return result_image, score

def process_files(name):
    """
    Detect deffects in folder with photos
    """

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
                        new_file_name = path + 'proc_11_04_siftgrid_newcontrast_noblur_newparams_' + file
                        print new_file_name
                        save_image(image, new_file_name)
                    except ValueError:
                        print file_name + '_ERROR'

def detect_deffects(file_name):
    """
    Detect deffects in photo, return new_file_name and skin score

    Input: file_name
    """

    new_file_name = 'uploads/' + file_name
    time = cv2.getTickCount()

    result_image, score = process_photo(new_file_name)

    print 'total score - {0}, total time - {1}'.format(score, print_time(time))

    return_file_name = 'proc_' + file_name
    new_file_name = 'uploads/' + return_file_name
    save_image(result_image, new_file_name)

    return return_file_name, score

#process_files('photo')
#detect_deffects('1.jpg')

#TODO binary thresholding?
#TODO cheecks, relief?

#TODO time optimization
#TODO points alongside contour in the case of bad face recognition (clasterization?) color detection?
#TODO real deffects near limbs?
#TODO genetic algorythm






