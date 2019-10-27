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
