"""
This Python Program Set Up Your Pupil direction Threshold.
Pupil Threshold save in text file.
"""

import cv2
from gaze_tracking import GazeTracking

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
def setup():
    setCount = 0
    setThreshold = 0

    direction = ["left", "right", "upward", "under"]
    direction_key = ["A", "S", "D", "F"]
    direction_index = 0

    thresholdFile = open("gaze_tracking/threshold.txt", 'w')

    while webcam.isOpened():
        _, frame2 = webcam.read()
        gaze.refresh(frame2)
        frame2 = gaze.annotated_frame()

        text = "Please turn your eyes to the " + direction[direction_index]
        text_push = "Push Button " + direction_key[direction_index] + " To SetUp Your Threshold!!"

        cv2.putText(frame2, text, (20, 60), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)
        cv2.putText(frame2, text_push, (20, 130), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        cv2.imshow("SetUp", frame2)

        #left
        if cv2.waitKey(1) == ord('a') and direction_index == 0:
            print(setThreshold, direction_index)
            if setCount > 10:
                direction_index += 1
                thresholdFile.write(str(setThreshold / setCount) + "\n")
                setCount = 0
                setThreshold = 0
            if gaze.pupils_located:
                setThreshold += gaze.horizontal_ratio()
                setCount += 1
        #right
        elif cv2.waitKey(1) == ord('s') and direction_index == 1:
            print(setThreshold, direction_index)
            if setCount > 10:
                direction_index += 1
                thresholdFile.write(str(setThreshold / setCount) + "\n")
                setCount = 0
                setThreshold = 0
            if gaze.pupils_located:
                setThreshold += gaze.horizontal_ratio()
                setCount += 1
        #upward
        elif cv2.waitKey(1) == ord('d') and direction_index == 2:
            print(setThreshold, direction_index)
            if setCount > 10:
                direction_index += 1
                thresholdFile.write(str(setThreshold / setCount) + "\n")
                setCount = 0
                setThreshold = 0
            if gaze.pupils_located:
                setThreshold += gaze.vertical_ratio()
                setCount += 1
        #under
        elif cv2.waitKey(1) == ord('f') and direction_index == 3:
            print(setThreshold, direction_index)
            if setCount > 10:
                direction_index += 1
                thresholdFile.write(str(setThreshold / setCount) + "\n")
                setCount = 0
                setThreshold = 0
            if gaze.pupils_located:
                setThreshold += gaze.vertical_ratio()
                setCount += 1


        if direction_index > 3 :
            break

        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyWindow("SetUp")
    thresholdFile.close()

