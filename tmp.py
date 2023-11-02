import cv2
import numpy as np

img = cv2.imread('063159/1/depth3.png', cv2.IMREAD_ANYDEPTH)
print(img.shape)
print(np.min(img), np.max(img))

cv2.imshow('img', img)
cv2.waitKey(0)