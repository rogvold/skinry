import skinscan
import os

def calc_overlaps(key_points1, key_points2):
    num_of_overlaps = 0

    for kp2 in key_points2:
        x2 = int(kp2[0])
        y2 = int(kp2[1])
        for kp1 in key_points1:
            x1 = int(kp1.pt[0])
            y1 = int(kp1.pt[1])

            r = kp1.size / 2
            if (x1 - x2)**2 + (y1 - y2)**2 <= r:
                num_of_overlaps += 1
                break

    return num_of_overlaps

def calc_precision(key_points1, key_points2):
    num_of_overlaps = calc_overlaps(key_points1, key_points2)
    return (num_of_overlaps + 0.0) / len(key_points1)

def calc_recall(key_points1, key_points2):
    num_of_overlaps = calc_overlaps(key_points1, key_points2)
    return (num_of_overlaps + 0.0) / len(key_points2)

def process_tests(num_tests):
    name = 'face_tests'
    tests = os.listdir(name)

    for i in range(1, num_tests + 1):
        kp1 = []
        kp2 = []

        for test in tests:
            test = 'face_tests' + '/' + test
            if str(i) in test and not '.txt' in test:
                image, kp1 = skinscan.process_photo_tests(test)

        test = name + '/' + str(i) + '.txt'
        file_input = open(test, "r")
        lines = file_input.readlines()
        for line in lines:
            coords = line.split()
            kp2.append(coords)

        precision = calc_precision(kp1, kp2)
        recall = calc_recall(kp1, kp2)
        print 'for test ' + str(i) + ':'
        print 'precision - ' + str(precision)
        print 'recall - ' + str(recall)

process_tests(1)
