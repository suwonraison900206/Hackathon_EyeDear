"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

import cv2
from gaze_tracking import GazeTracking
#from gaze_tracking import Eye
from datetime import datetime
from datetime import timedelta
from tkinter import *
from PIL import ImageTk, Image

#eye = Eye()
gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

before_blink=False
blink_count=0
first_now=datetime.now()    #캠키자마자 찍히는 시간
first_now=first_now.second

start_study_time = datetime.now()
no_monitor_time = 0
study_time = timedelta(seconds=0)
are_you_study = False

root = Tk()
root.title('화면')
root.geometry("+500+10")
label1 = Label(root, text="1분간 깜빡임 횟수 : " + str(blink_count), font= ('Helvetica 15 bold'))
label1.grid(row=0, column=0)

label2 = Label(root, text="자세교정", font= ('Helvetica 15 bold'))
label2.grid(row=1, column=0)

label3 = Label(root, text="test", font= ('Helvetica 15 bold'))
label3.grid(row=2, column=0)
label_cam = Label(root)
label_cam.grid(row=3, column=0)

button = Button(root,text="quit", command=root.destroy, width=8, height=1)
button.grid(row=4, column=0)
def video_stream():
    global study_time, are_you_study, start_study_time, no_monitor_time, first_now, before_blink, blink_count
    _, frame = webcam.read()
    if not _:
        print("WebCam is not detected")
    
    else:
        # We get a new frame from the webcam
        

        # We send this frame to GazeTracking to analyze it
        gaze.refresh(frame)

        frame = gaze.annotated_frame()
        text = ""

        if gaze.is_blinking():
            text = "Blinking"
            if before_blink == False:
                blink_count += 1
        elif gaze.is_right():
            text = "Looking right"
        elif gaze.is_left():
            text = "Looking left"
        elif gaze.is_center():
            if gaze.is_up():
                text = "Looking upward"
            elif gaze.is_down():
                text = "Looking under"
            else:
                text = "Looking center"
        #print(gaze.out_of_monitor())
        # if out_of_monitor False, no monitor time is not initialize
        # So if out_of_monitor False, your not watch monitor
        now_study_time = datetime.now()
        if are_you_study:
            study_time += (now_study_time - start_study_time)
        start_study_time = now_study_time


        if not gaze.out_of_monitor():
            if no_monitor_time == 0:
                print("Your Study Right Now")
                no_monitor_time = datetime.now()
            elif (datetime.now() - no_monitor_time) > timedelta(seconds=10):
                print("Your not Study!!!!")
                are_you_study = False
                study_time -= (datetime.now() - no_monitor_time)
        else:
            are_you_study = True
            no_monitor_time = 0


        before_blink=gaze.is_blinking()
        cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

        now = datetime.now()    #현재 시간
        now = now.second

        #눈깜박임 횟수 세서 팝업창띄우기(15회미만이고 1분이 지났으면)
        if blink_count <= 15 and now == first_now:
            print(blink_count, '123')
            blink_count=0
        elif now == first_now:
            print(blink_count, '안 건조해!')
            blink_count=0

        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()
        cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
        cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

        blink_text = "1분간 깜빡임 횟수 : " + str(blink_count)
        label1.configure(text=blink_text)
        label3.configure(text="")
        print(blink_count)
        print(first_now)

        print(start_study_time)
        print(no_monitor_time)
        print(study_time)
        print(are_you_study)
        # cv2.imshow("Eye Dear", frame)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        label_cam.imgtk = imgtk
        label_cam.configure(image=imgtk)
        label_cam.after(1, video_stream)

video_stream()
root.mainloop()