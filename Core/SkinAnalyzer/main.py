import sys
import cv2
import cv2.cv
import numpy as np
from matplotlib import pyplot as plt
JPG = '.jpg'

def readImage(fileName, type):
    image = cv2.imread(fileName, type)
    return image

def saveImage(image, fileName):
    cv2.imwrite(fileName, image)

def saveAndShowImage(image, fileName):
    cv2.imwrite(fileName, image)
    cv2.imshow(fileName,image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def printTime(time1):
    time2 = cv2.getTickCount()
    time = (time2 - time1)/ cv2.getTickFrequency()
    print time

def createBGRHist(image):
    color = ('B','G','R')
    for i, col in enumerate(color):
        histr = cv2.calcHist([image1],[i], None, [256], [0,256])
        plt.plot(histr, color = col)
        plt.xlim([0,256])
    plt.show()

def findCircles(image, type1, type2, min, max):
    cimg = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    circles = cv2.HoughCircles(image, cv2.cv.CV_HOUGH_GRADIENT ,1, 40, type1, type2, min, max)
    circles = np.uint16(np.around(circles))
    for i in circles[0,:]:
        cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
        cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)
    return cimg

def SIFT(image, param3, param5):
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT(0, 3, param3, 10, param5)
    keyPoints = sift.detect(gray, None)
    image = cv2.drawKeypoints(gray, keyPoints, flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    square = 0
    imageOriginal = readImage('3' + JPG, cv2.IMREAD_COLOR)
    max = 0
    min = 255
    maxPoint = (0, 0)
    minPoint = (0, 0)

    for kp in keyPoints:
        x = round(kp.pt[0])
        y = round(kp.pt[1])

        if imageOriginal[x, y, 2] > max:
            max = imageOriginal[x, y, 2]
            maxPoint = (x, y)
        else:
            if imageOriginal[x, y, 2] < min:
                min = imageOriginal[x, y, 2]
                minPoint = (x, y)
        print str(kp.size) + ' ' + str(kp.pt) + ' ' + str(imageOriginal[x, y, 2])

        radius = kp.size / 2;
        square += radius * radius * np.pi

    print 'max:'
    print maxPoint
    print 'min:'
    print minPoint
    return image, square

def fullSIFT(fileName, param3, param5, blur):
    image = readImage(fileName + JPG, cv2.IMREAD_COLOR)
    shape = image.shape
    square = shape[0] * shape[0]
    print square

    blurStr = 'noBlur'
    if blur:
        blurStr = 'Blur'
        image = cv2.medianBlur(image, 5)

    result = SIFT(image, param3, param5)

    name = fileName + ' pic ' + blurStr + ' ' + ' param3 - ' + str(param3) + ' ' + 'param 5 - ' + str(param5) + JPG
    saveImage(result[0], name)
    return result[1] / square

fileName  = '3'
param3 = 0.03
param5 = 2.3
startTime = cv2.getTickCount()

square = fullSIFT(fileName, param3, param5, False)
print 'coeff - ' + str(square * 100) + '%'

printTime(startTime)