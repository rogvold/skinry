import os
from fd import *

def test_no_face():
    all_is_ok = True
    error_list = []
    for file_name in os.listdir('No_face'):
        try:
            img = cv2.imread('No_face/' + file_name)
            if img == None:
                raise ValueError("No image" + file_name)
            detect_face_and_organs(img)
            all_is_ok = False
            error_list.append(file_name)
        except ValueError as exc:
            if str(exc) != 'Error: No face. May be your eyes are closed' and str(exc) != 'Face is too small':
                all_is_ok = False
                error_list.append(file_name)

    if all_is_ok:
        print 'Test_no_face is passed'
    else:
        print 'Test_no_face is failed'
        print 'Failed:'
        for error in error_list:
            print error

def test_existence_face():
    all_is_ok = True
    error_list = []
    for file_name in os.listdir('Face'):
        try:
            img = cv2.imread('Face/' + file_name)
            if img == None:
                raise ValueError("No image")
            detect_face_and_organs(img)
        except ValueError as exc:
            if str(exc) == 'Error: No face. May be your eyes are closed':
                all_is_ok = False
                error_list.append(file_name)

    if all_is_ok:
        print 'Test_existence_face is passed'
    else:
        print 'Test_existence_face is failed'
        print 'Failed:'
        for error in error_list:
            print error

def test_face_is_too_small():
    all_is_ok = True
    error_list = []
    for file_name in os.listdir('Face_is_small/'):
        try:
            img = cv2.imread('Face_is_small/' + file_name)
            if img == None:
                raise ValueError("No image" + file_name)
            detect_face_and_organs(img)
            all_is_ok = False
            error_list.append(file_name)
        except ValueError as exc:
            if str(exc) != 'Face is too small' and str(exc) != 'Error: No face. May be your eyes are closed':
                all_is_ok = False
                error_list.append(file_name)

    if all_is_ok:
        print 'Test_face_is_too_small is passed'
    else:
        print 'Test_face_is_too_small is failed'
        print 'Failed:'
        for error in error_list:
            print error

def test():
    test_no_face()
    test_existence_face()
    test_face_is_too_small()

test()