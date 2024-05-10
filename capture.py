import cv2
import numpy as np

'''
Find a ball in a live video from a webcam on a computer
Mainly used to tune for edge detection
Planned to have this work in combination with a robot arm to hopefully catch a ball
Buggy and unstable as of now
'''


# Global variables for threshold values
min_threshold_value = 50
max_threshold_value = 150
min_radius_threshold = 1
circularity_tolerance = 0.7
area_diff_tolerance = 150


#TODO
#Needs to be more stable
#Still for some reason have trouble detecting circles 
#Sometimes detects rectangles or just random things

def track_ball_by_shape(frame):

    '''
    Takes a frame and does edge detection to find circles
    If it matches the thresholds it will detect it
    '''


    global max_threshold_value
    global min_threshold_value
    global min_radius_threshold
    global circularity_tolerance
    global area_diff_tolerance
    

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    

    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    

    edges = cv2.Canny(blurred, min_threshold_value, max_threshold_value)
    

    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    

    contour_image = np.zeros_like(frame)
    cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)
    

    if contours:
        # Find the contour with the maximum area
        max_contour = max(contours, key=cv2.contourArea)

        (x, y), radius = cv2.minEnclosingCircle(max_contour)
        if radius == 0 or radius < min_radius_threshold: 
            return frame, contour_image
        center = (int(x), int(y))
        radius = int(radius)


        if radius != 0:
            circularity = cv2.contourArea(max_contour) / (np.pi * radius ** 2)
        else:
            circularity = 0.0


        if circularity > 0.2:
            cv2.putText(frame, f"Circularity: {circularity:.2f}", (center[0], center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


        contour_area = cv2.contourArea(max_contour)
        circle_area = np.pi * radius ** 2
        area_diff = abs(circle_area - contour_area)

        #Might need to change these
        # circularity_tolerance = 0.7
        # area_diff_tolerance = 150


        if (circularity > circularity_tolerance or area_diff < area_diff_tolerance):
            # print("Circle Center Coordinates:", center)


            x, y, w, h = cv2.boundingRect(max_contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    
    return frame, contour_image



#Really nice and cool live adjustments

def update_maxThreshold(value):
    global max_threshold_value
    max_threshold_value = value

def update_minThreshold(value):
    global min_threshold_value
    min_threshold_value = value

def update_minRadius(value):
    global min_radius_threshold
    min_radius_threshold = value

def update_area_diff_tolerance(value):
    global area_diff_tolerance
    area_diff_tolerance = value

def update_circularity_tolerance(value):
    global circularity_tolerance
    circularity_tolerance = float(value/100)
    print (circularity_tolerance)


# Main function
def main():
    global min_threshold, max_threshold
    

    cv2.namedWindow('Parameters')
    cv2.createTrackbar('Min Threshold', 'Parameters', min_threshold_value, 255, update_maxThreshold)
    cv2.createTrackbar('Max Threshold', 'Parameters', max_threshold_value, 255, update_minThreshold)
    cv2.createTrackbar('Min Radius Threshold', 'Parameters', min_radius_threshold, 255, update_minRadius)
    cv2.createTrackbar('Area Diff', 'Parameters', area_diff_tolerance, 255, update_area_diff_tolerance)
    cv2.createTrackbar('Circularity Tolerance', 'Parameters', int(circularity_tolerance ), 100, update_circularity_tolerance)



    capture = cv2.VideoCapture(0)
    capture.set(3, 640)
    capture.set(4, 480)

    while True:
        ret, frame = capture.read()
        if not ret:
            break
           

        tracked_frame, contour_image = track_ball_by_shape(frame)
        

        cv2.imshow('Webcam', np.hstack([tracked_frame, contour_image]))


        if cv2.waitKey(1) == ord('q'):
            break


    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
