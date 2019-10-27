import argparse
import imutils
import cv2
import json
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
temp = np.empty((4, 2), dtype="float32")
for point in approx:
    countx1 = 0
    countx2 = 0
    county1 = 0
    county2 = 0
    for check in approx:
        if check[0] != point[0] or check[1] != point[1]:
            if point[0] <= check[0]:
                countx1 = countx1 + 1
            else:
                countx2 = countx2 + 1
            if point[1] <= check[1]:
                if point[0] == 2864 and point[1] == 3771:
                    print(point, check)
                county1 = county1 + 1
            else:
                county2 = county2 + 1
    if countx1 > 1 and county1 > 1:
        temp[0] = point
    if countx2 > 1 and county1 > 1:
        temp[1] = point
    if countx1 > 1 and county2 > 1:
        temp[3] = point
    if countx2 > 1 and county2 > 1:
        temp[2] = point

(tl, tr, br, bl) = temp

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
transform = cv2.getPerspectiveTransform(temp, transformCoords)
perspective = cv2.warpPerspective(image.copy(), transform, (maxWidth, maxHeight))
h, w, _ = perspective.shape

outterCropProportion = 0
widthCut = int(maxWidth*outterCropProportion/2)
heightCut = int(maxHeight*outterCropProportion/2)
perspectiveImage = perspective[heightCut:h-1-heightCut, widthCut:w-1-widthCut]

cv2.imwrite('perspective.png', perspectiveImage)

def detect(c):
    # initialize the shape name and approximate the contour
    shape = "unidentified"
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    # if the shape is a triangle, it will have 3 vertices
    if len(approx) == 3:
        shape = "triangle"

    # if the shape has 4 vertices, it is either a square or
    # a rectangle
    elif len(approx) == 4:
        # compute the bounding box of the contour and use the
        # bounding box to compute the aspect ratio
        (x, y, w, h) = cv2.boundingRect(approx)
        ar = w / float(h)

        # a square will have an aspect ratio that is approximately
        # equal to one, otherwise, the shape is a rectangle
        shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"

    # if the shape is a pentagon, it will have 5 vertices
    elif len(approx) == 5:
        shape = "pentagon"

    # otherwise, we assume the shape is a circle
    else:
        shape = "circle"

    # return the name of the shape
    return shape

imagePGray = cv2.cvtColor(perspectiveImage.copy(), cv2.COLOR_BGR2GRAY)

# Filtering
imagePGray = cv2.GaussianBlur(imagePGray.copy(), (5, 5), 0)
imagePGray = cv2.GaussianBlur(imagePGray.copy(), (5, 5), 0)
edgesP = cv2.Canny(imagePGray.copy(), 80, 160)
threshP = cv2.threshold(edgesP.copy(), 80, 160, cv2.THRESH_BINARY)[1]

kernelP = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
dilatedP = cv2.dilate(threshP.copy(), kernelP)
cv2.imwrite('cannyPerspective.png', dilatedP)

# Obtain contours, looking for scantron outline
contoursP, hierarchyP = cv2.findContours(dilatedP.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

ChildContour = hierarchyP[0, :, -1]
WithoutChildContour = (ChildContour==-1).nonzero()[0]

cntsA = contoursP
# get contours from indices
cntsA=[cntsA[i] for i in WithoutChildContour]

ratio = perspectiveImage.shape[0] / float(perspectiveImage.shape[0])
shapeContoursImage = perspectiveImage.copy()

intermediateJSON = []
i = 0
# loop over the contours
for c in cntsA:
    # compute the center of the contour, then detect the name of the
    # shape using only the contour
    M = cv2.moments(c)

    cX = int((M["m10"] / (M["m00"]+1)) * ratio)
    cY = int((M["m01"] / (M["m00"]+1)) * ratio)
    shape = detect(c)
    intermediateJSON.append({"shape": shape, "value": ''})
    i = i+1

    # multiply the contour (x, y)-coordinates by the resize ratio,
    # then draw the contours and the name of the shape on the image
    c = c.astype("float")
    c *= ratio
    c = c.astype("int")
    cv2.drawContours(shapeContoursImage, [c], -1, (57, 255, 20), 2)
    cv2.putText(shapeContoursImage, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255), 2)

#shapeContoursImage = cv2.drawContours(perspectiveImage.copy(), cntsA, -1, (57, 255, 20), 2)

cv2.imwrite('shapecontours.png', shapeContoursImage)

def detect_document(path):
    """Detects document features in an image."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()


    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.document_text_detection(image=image)

    if len(response.text_annotations) > 0:
        return response.text_annotations[0].description
    else:
        return ''
    """
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            print('\nBlock confidence: {}\n'.format(block.confidence))

            for paragraph in block.paragraphs:
                print('Paragraph confidence: {}'.format(
                    paragraph.confidence))

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                    print('Word text: {} (confidence: {})'.format(
                        word_text, word.confidence))

                    for symbol in word.symbols:
                        print('\tSymbol: {} (confidence: {})'.format(
                            symbol.text, symbol.confidence))

    """


i = 0
for c in cntsA:
    x,y,width,height = cv2.boundingRect(c)
    out = imagePGray[y:y+height, x:x+width]
    cv2.imwrite('temp.png', out, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
    intermediateJSON[i]['value'] = detect_document('temp.png')
    i = i+1

intermediateJSONFin = []
for i in range(len(intermediateJSON)):
    if intermediateJSON[i]['value'] != '':
        intermediateJSONFin.append(intermediateJSON[i])

# Reversing a list using reversed()
def Reverse(lst):
    return [ele for ele in reversed(lst)]

print(Reverse(intermediateJSONFin))
