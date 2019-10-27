import argparse
import imutils
import cv2
import numpy as np

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
    help="path to the input image")
args = vars(ap.parse_args())

# load the image and resize it to a smaller factor so that
# the shapes can be approximated better
image = cv2.imread(args["image"])
imageGray = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)

# Filtering
imageGray = cv2.GaussianBlur(imageGray.copy(), (5, 5), 0)
edges = cv2.Canny(imageGray.copy(), 80, 160)
thresh = cv2.threshold(edges.copy(), 80, 160, cv2.THRESH_BINARY)[1]

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
dilated = cv2.dilate(thresh.copy(), kernel)

# Obtain contours, looking for scantron outline
contours, _ = cv2.findContours(dilated.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.imwrite('canny.png', dilated)

mx = (0,0,0,0)      # biggest bounding box so far
mx_area = 0
maxContour = []
for cont in contours:
    x,y,w,h = cv2.boundingRect(cont)
    area = w*h
    if area > mx_area:
        mx = x,y,w,h
        mx_area = area
        maxContour = cont
x,y,w,h = mx

# Draw contour only if one actually exists
if len(contours) > 0:
    contourImage = cv2.drawContours(image.copy(), [maxContour], -1, (57, 255, 20), 2)

cv2.imwrite('contours.png', contourImage)

approx = []
d = 1
approx = cv2.approxPolyDP(maxContour, d, True)
while len(approx) > 4:
    d = d + 1
    approx = cv2.approxPolyDP(maxContour, d, True)

cornerImage = image.copy()
cv2.circle(cornerImage, tuple(approx[0][0]), 50, (57, 255, 20), -1)
cv2.circle(cornerImage, tuple(approx[1][0]), 50, (57, 255, 20), -1)
cv2.circle(cornerImage, tuple(approx[2][0]), 50, (57, 255, 20), -1)
cv2.circle(cornerImage, tuple(approx[3][0]), 50, (57, 255, 20), -1)

cv2.imwrite('corners.png', cornerImage)

cv2.getPerspectiveTransform(approx, )
