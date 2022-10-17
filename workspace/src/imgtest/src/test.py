import cv2
camera_width = 1280
camera_height = 960
vidfps = 30

cam = cv2.VideoCapture(0)
# cam.set(cv2.CAP_PROP_FPS, vidfps)
# cam.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
# cam.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)
cv2.namedWindow("USB Camera", cv2.WINDOW_AUTOSIZE)

while True:
    ret, color_image = cam.read()
    
    cv2.imshow('USB Camera', color_image)
    key =cv2.waitKey(10)
    if key == 27:
        break

cv2.destroyAllWindows()