# colour-following-mouse-point
import cv2
import numpy as np
import win32api
import win32con
import math
import time

'''here we are tracking out blue color and mouse cursor will follow it,there is golden color also and when we get both color nearby it clicks where the pointer is.
i used it two colour glue tapes and wear it on my fingers and now whenever i move my fingers it mouse moves with it'''

lower_blue = np.array([90,130,130])
upper_blue = np.array([100,255,255])
lower_golden = np.array([15, 150, 150])
upper_golden = np.array([30, 255, 255])

def point(x,y):
    x, y = int((650 - x) * 2.5), int(y * 2)
    win32api.SetCursorPos((x,y))

def click(x,y):
    x, y = int((650 - x) * 2.5), int(y * 2)
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def distance(x,y,z,w):
    t1 = (z - x) ** 2
    t2 = (w - y) ** 2
    return math.sqrt(t1 + t2)

lk_params = dict( winSize  = (15,15),maxLevel = 2,criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

cap = cv2.VideoCapture(0)

while(1):
    ret, old_frame = cap.read()

    temp_hsv = cv2.cvtColor(old_frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(temp_hsv, lower_blue, upper_blue)
    old_res = cv2.bitwise_and(old_frame, old_frame, mask=mask)
    old_gray = cv2.cvtColor(old_res, cv2.COLOR_BGR2GRAY)

    image, contours, hierarchy = cv2.findContours(mask, 1, 2)
    if (contours):
        cnt = contours[0]
    else:
        print 'color out of range blue!!!!!!!'
        break
    (x, y), radius = cv2.minEnclosingCircle(cnt)

    old_points = np.array([[[x, y]]],np.float32)

    while(1):
        ret, frame = cap.read()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        mask_golden = cv2.inRange(hsv, lower_golden, upper_golden)
        new_res = cv2.bitwise_and(frame,frame, mask=mask)
        image, contours, hierarchy = cv2.findContours(mask, 1, 2)
        image, contours_golden, hierarchy = cv2.findContours(mask_golden, 1, 2)
        if contours:
            cnt = contours[0]
            cnt_g = contours_golden[0]
        else:
            print 'color out of range golden!!!!!!!'
            break

        (cx, cy), radius = cv2.minEnclosingCircle(cnt)
        cx,cy = int(cx),int(cy)
        cv2.circle(frame,(cx,cy),30,(0,255,0),2)

        new_gray = cv2.cvtColor(new_res, cv2.COLOR_BGR2GRAY)
        #new_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        new_points,status,error = cv2.calcOpticalFlowPyrLK(old_gray,new_gray,old_points,None,**lk_params)
        old_gray = new_gray.copy()
        old_points=new_points
        x,y = new_points.ravel()
        dist = distance(x,y,cx,cy)
        if dist>30:
            break

        point(x,y)
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

        (gx, gy), radius = cv2.minEnclosingCircle(cnt_g)
        gx, gy = int(gx), int(gy)
        g_dist = distance(x, y, gx, gy)
        cv2.circle(frame, (gx, gy), 5, (0, 255, 0), -1)
        if g_dist<50:
            print 'going for click'
            click(x,y)
            click(x,y)
            time.sleep(1)
        #cv2.imshow('image',frame)
        cv2.waitKey(1)
cap.release()
cv2.destroyAllWindows()
