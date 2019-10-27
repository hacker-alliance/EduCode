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
cv2.imwrite('canny.png', dilated)

# Obtain contours, looking for scantron outline
contours, _ = cv2.findContours(dilated.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

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

h, w, _ = image.shape
approx = np.array([approx[0][0], approx[3][0], approx[2][0], approx[1][0]], dtype="float32")

(tl, tr, br, bl) = approx

# compute the width of the new image, which will be the
# maximum distance between bottom-right and bottom-left
# x-coordiates or the top-right and top-left x-coordinates
widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
maxWidth = max(int(widthA), int(widthB))

# compute the height of the new image, which will be the
# maximum distance between the top-right and bottom-right
# y-coordinates or the top-left and bottom-left y-coordinates
heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
maxHeight = max(int(heightA), int(heightB))

transformCoords = np.array([[0, 0], [maxWidth-1, 0], [maxWidth-1, maxHeight-1], [0, maxHeight-1]], dtype="float32")
transform = cv2.getPerspectiveTransform(approx, transformCoords)
perspective = cv2.warpPerspective(image.copy(), transform, (maxWidth, maxHeight))
h, w, _ = perspective.shape

outterCropProportion = 0.1
widthCut = int(maxWidth*outterCropProportion/2)
heightCut = int(maxHeight*outterCropProportion/2)
perspectiveImage = perspective[heightCut:h-1-heightCut, widthCut:w-1-widthCut]

cv2.imwrite('perspective.png', perspectiveImage)
