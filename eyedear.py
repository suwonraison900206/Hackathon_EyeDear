"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

import cv2
try:
    from EyeDear import gaze_tracking
except:
    print("EyeDear folder not found")
from gaze_tracking import GazeTracking
from datetime import datetime
from datetime import timedelta
from tkinter import *
from PIL import ImageTk, Image

# eye = Eye()
gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

before_blink = False
blink_count = 0
count_blink_one_minute = datetime.now()
#first_now = datetime.now()  # 캠키자마자 찍히는 시간
#first_now = first_now.second

# count study time
start_study_time = datetime.now()  # check before study
no_monitor_time = 0  # if no monitor time is zero, the pupil is located.
study_time = timedelta(seconds=0)  # real study time
are_you_study = False  # check person study or not

# face coords
face_x = 0
face_y = 0
face_std_x = 0
face_std_y = 0

# stay pose
pose_time = datetime.now()
minute_pose_time = 1 # default
change_minute = False

# User Name
user_name = "사용자"

root = Tk()
root.title('Eye Dear')
root.geometry("+500+10")
label1 = Label(root, text="안구건조증 증상 측정 중입니다.", font= ('Helvetica 15 bold'), height=2, width=50, borderwidth=2, relief="ridge")
label1.grid(row=0, column=0, columnspan=3, pady=2)

label2 = Label(root, text="자세교정", font= ('Helvetica 15 bold'), height=2, width=28, borderwidth=2, relief="ridge")
label2.grid(row=1, column=0, columnspan=2, pady=2)

label2_1 = Label(root, text=f"자세주기 {minute_pose_time}분" , font= ('Helvetica 15 bold'), height=2, width=18, borderwidth=2, relief="ridge")
label2_1.grid(row=1, column=2, pady=2)

label3 = Label(root, text="공부시간", font= ('Helvetica 15 bold'), height=2, width=50, borderwidth=2, relief="ridge")
label3.grid(row=2, column=0, columnspan=3, pady=2)
label_cam = Label(root)
label_cam.grid(row=3, column=0, columnspan=3, pady=2)

button = Button(root,text="quit", command=root.destroy, width=10, height=2, font= ('Helvetica 15 bold'))
button.grid(row=4, column=2)

#setup_btn = Button(root, text="setup", command=setup, width=10, height=2, font= ('Helvetica 15 bold'))
#setup_btn.grid(row=4, column=1, pady=2)

def video_stream():
    global study_time, are_you_study, start_study_time, no_monitor_time
    global count_blink_one_minute, before_blink, blink_count
    global face_x, face_y, face_std_x, face_std_y, pose_time, gaze
    global change_minute, minute_pose_time
    global user_name

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
                before_blink = True
        elif gaze.is_right():
            before_blink = False
            text = "Looking right"
        elif gaze.is_left():
            before_blink = False
            text = "Looking left"
        elif gaze.is_center():
            before_blink = False
            if gaze.is_up():
                text = "Looking upward"
            elif gaze.is_down():
                text = "Looking under"
            else:
                text = "Looking center"
        else:
            before_blink = False
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
            elif (datetime.now() - no_monitor_time) > timedelta(seconds=10) and are_you_study:
                print("Your not Study!!!!")
                are_you_study = False
                study_time -= (datetime.now() - no_monitor_time)
        else:
            are_you_study = True
            no_monitor_time = 0

        #label3 show study time
        study_time_second = study_time.total_seconds()
        study_hour = int(study_time_second / 3600)
        study_minute = int((study_time_second % 3600) / 60)
        study_second = int(study_time_second % 60)
        label3.configure(text = f"작업시간 : {study_hour}시간 {study_minute}분 {study_second}초")

        cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

        # now = now_study_time.second # 현재 시간

        # 눈깜박임 횟수 세서 팝업창띄우기(15회미만이고 1분이 지났으면)
        if (now_study_time - count_blink_one_minute) > timedelta(seconds=10):
            count_blink_one_minute = datetime.now()
            if blink_count <= 15:
                label1.configure(text=f"{user_name}님은 1분에 {blink_count}번 눈을 깜빡이셨습니다. \n안구건조증 예방을 위해 눈을 더 깜빡여주세요.",
                                 font=('Helvetica 15 bold'), fg='red')
                blink_count = 0
            else:
                label1.configure(text=f"{user_name}님은 1분에 {blink_count}번 눈을 깜빡이셨습니다. \n지금처럼 눈을 자주 깜빡여주세요.",
                                 font=('Helvetica 15 bold'), fg='black')
                blink_count = 0

        if change_minute:
            label2_1.configure(text=f"자세주기 {minute_pose_time}분")
            change_minute = False

        face_loc = gaze.face_coords()
        if face_loc != None:
            face_x, face_y = face_loc.center().x, face_loc.center().y
            if face_std_x == 0 and face_std_y == 0:
                label2.configure(text="자세를 고치지 않아도 됩니다.", fg="black")
                pose_time = datetime.now()
                face_std_x = face_x
                face_std_y = face_y
            elif abs(face_std_x - face_x) > 100 or abs(face_std_y - face_y) > 50:
                label2.configure(text="자세를 고치지 않아도 됩니다.", fg="black")
                pose_time = datetime.now()
                face_std_x = face_x
                face_std_y = face_y
            elif (now_study_time - pose_time) > timedelta(minutes=minute_pose_time):
                label2.configure(text="슬슬 자세를 고치세요.", fg="red")
            #print((now_study_time - pose_time))
            cv2.putText(frame, "C", (face_loc.center().x, face_loc.center().y), cv2.FONT_HERSHEY_DUPLEX, 0.3, (147, 58, 31), 1)

            # cv2.imshow("Eye Dear", frame)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        label_cam.imgtk = imgtk
        label_cam.configure(image=imgtk)
        label_cam.after(1, video_stream)

def setup():
    global gaze
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
            print(setThreshold, direction_index, setCount)
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
            print(setThreshold, direction_index, setCount)
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
            print(setThreshold, direction_index, setCount)
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
            print(setThreshold, direction_index, setCount)
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
    gaze = GazeTracking() #for update threshold
    

def onClick():
    setup()

def param_setup():
    #global minute_pose_time, change_minute
    # 자세교정 Entry Box
    tk_param = Tk()
    tk_param.title('Settings')
    tk_param.geometry("+500+10")

    def set_pose_time(event):
        global minute_pose_time, change_minute
        minute_pose_time = int(label2_entry.get())
        print(minute_pose_time)
        change_minute = True

    def set_user_name(event):
        global user_name
        user_name = str(label3_entry.get())
        print(user_name)

    param_label1 = Label(tk_param, text="입력 후 Enter을 눌러주세요.", font= ('Helvetica 15 bold'), height=2, width=40, borderwidth=2, relief="ridge")
    param_label1.grid(row=0, column=0, columnspan=2, pady=2)

    param_label2 = Label(tk_param, text="자세권고 주기 : ", font= ('Helvetica 15 bold'), height=2, width=23, borderwidth=2, relief="flat")
    param_label2.grid(row=1, column=0)

    label2_entry = Entry(tk_param, width=13, borderwidth=2, relief="ridge")
    label2_entry.bind("<Return>", set_pose_time)
    label2_entry.grid(row=1, column=1, pady=2)

    param_label3 = Label(tk_param, text="사용자 이름 : ", font=('Helvetica 15 bold'), height=2, width=23, borderwidth=2,
                         relief="flat")
    param_label3.grid(row=2, column=0)

    label3_entry = Entry(tk_param, width=13, borderwidth=2, relief="ridge")
    label3_entry.bind("<Return>", set_user_name)
    label3_entry.grid(row=2, column=1, pady=2)

    quit_button = Button(tk_param, text="quit", command=tk_param.destroy, width=10, height=2, font=('Helvetica 15 bold'))
    quit_button.grid(row=3, column=0, columnspan=2, pady=2)

    tk_param.mainloop()


#Param Setup Button
param_setup_btn = Button(root, text="Settings", command=param_setup, width=10, height=2, font= ('Helvetica 15 bold'))
param_setup_btn.grid(row=4, column=1)
#Set up Button
setup_btn = Button(root, text="setup", command=onClick, width=10, height=2, font= ('Helvetica 15 bold'))
setup_btn.grid(row=4, column=0)


video_stream()
root.mainloop()