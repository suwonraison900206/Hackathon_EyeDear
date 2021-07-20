# Eye Dear Project

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)  

![Demo_Final](https://user-images.githubusercontent.com/51294226/125287022-67ea4b80-e357-11eb-8472-ce20efef9b51.gif)  



**Developer : 황동준, 나종석, 장치근, 조영진, 한예지**  
**해당 프로젝트에는 다음과 같은 3가지 기능이 있습니다**
1. 웹캠을 이용한 안구건조증 예방 알림 기능  
2. 주기적인 자세 교체 권고  
3. Gaze tracking을 이용한 작업시간 측정

`exe branch`에서 `eyedear.py`를 바로 `exe file`로 만들 수 있습니다.  
실행파일로 만들고 싶으시면 `pyinstaller`에 `gaze tracking`폴더와 `eyedear.py`를 넣어서 만들어 주세요.  

## 실행 방법
```git
git clone https://github.com/Druwa-git/EyeDear.git
```
Window라면 Command 창을 켜고 해당 폴더에서 가상환경을 만들어 줍니다.  
```
virtualenv venv
venv\Scripts\activate
pip install -r requirements.txt
```
모두 설치가 완료되었다면 `eyedear.py`를 실행합니다.
```python
python eyedear.py
```

## 예측 모델 정확도 상승 방안
### 1. EYE BLINKING
```python
python setup_blink.py
```
![image](https://user-images.githubusercontent.com/51294226/125280930-97498a00-e350-11eb-8323-57b52ba998ef.png)  
여기서 자신의 왼쪽 눈 사진 40장을 촬영하여, `dataset` 폴더에 저장하게 됩니다.  
이후, `train_custom.ipynb` 파일을 실행하여 해당 코드를 실행하면,  
`gaze_tracking/trained_model/`에 해당 날짜의 훈련 모델이 다음과 같이 나오게 됩니다.  
![image](https://user-images.githubusercontent.com/51294226/125278946-4c2e7780-e34e-11eb-9ca2-c903c544d12f.png)  

이를 `gaze_tracking/gaze_tracking.py`에서 아래의 코드 파일 명을 바꾸면 custom해서 학습시킨 모델을 적용할 수 있습니다.  
해당 모델 요약은 다음과 같음.  
![image](https://user-images.githubusercontent.com/51294226/125280781-6ff2bd00-e350-11eb-933f-fde4540075e3.png)  
```python
#blinking model
model_path = os.path.abspath(os.path.join(cwd, "trained_models/2021_07_12_15_20_04.h5"))
self.blinking_model = load_model(model_path)
self.blinking_model.summary()
```
![image](https://user-images.githubusercontent.com/51294226/125279330-c959ec80-e34e-11eb-88a1-c2d7f0cb7751.png)  

Custom Model을 훈련시켜 5%정도의 정확도를 높일 수 있었다.

### 2. Gaze Tracking
```python
python eyedear.py
# 이후 Setup Button을 누른다.
```
이를 실행하면 다음과 같은 화면을 볼 수 있음.  
![image](https://user-images.githubusercontent.com/51294226/125279689-32d9fb00-e34f-11eb-9228-7c518b6c593b.png)  
A,S,D,F 순서대로 왼쪽, 오른쪽, 위, 아래의 pupil threshold 값을 찾아주게 됨.  

해당 값을 각각 10개씩 받아서 평균을 내면, `gaze_tracking/threshold.txt`에 4개의 값이 저장된다.  

이후 `Setup` 창이 종료되면 `ThresHold setting`이 된 상태에서 `Gaze Tracking`을 수행하게 된다.  

프로그램이 종료된 후에도 영구적으로 저장된다.  

**def setup()**  
```python
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
```

저장된 `threshold`값은 gaze_tracking.py에서 불러오게 된다.
```python
#set Threshold
        try:
            file_path = os.path.abspath(os.path.join(cwd, "threshold.txt"))
            threshold_file = open(file_path, 'r')
            self.left_threshold = float(threshold_file.readline())
            self.right_threshold = float(threshold_file.readline())
            self.upward_threshold = float(threshold_file.readline())
            self.under_threshold = float(threshold_file.readline())
            threshold_file.close()
            print("Open File")
        except:
            #default setting
            self.left_threshold = 0.5
            self.right_threshold = 0.75
            self.upward_threshold = 0.7
            self.under_threshold = 1.1
```

## 기능 구현
### 1. 웹캠을 이용한 안구건조증 예방 알림 기능  
`def video_stream main code`  
```python
if (now_study_time - count_blink_one_minute) > timedelta(seconds=60):
    count_blink_one_minute = datetime.now()
    if blink_count <= 15:
      label1.configure(text = f"건조해!", fg='red')
      blink_count = 0
    else:
      label1.configure(text = f"안 건조해!", fg='black')
      blink_count = 0
 ```
 다음과 같이 시간특정을 하게 됨. `count_blink_one_minute`는 1분마다 초기화 되며, `now_study_time`은 현재 시간을 의미함.  
 `blinking`측정 main code는 다음과 같음.  
 ```python
 landmarks = face_utils.shape_to_np(landmarks)
if side == 0:
     eye_img, eye_rect = self.crop_eye(origin_frame, eye_points=landmarks[36:42])
     eye_img = cv2.resize(eye_img, dsize=self.IMG_SIZE)
elif side == 1:
    eye_img, eye_rect = self.crop_eye(origin_frame, eye_points=landmarks[42:48])
    eye_img = cv2.resize(eye_img, dsize=self.IMG_SIZE)
    eye_img = cv2.flip(eye_img, flipCode=1)

eye_input = eye_img.copy().reshape((1, self.IMG_SIZE[1], self.IMG_SIZE[0], 1)).astype(np.float32) / 255.
pred = blinking_model.predict(eye_input)
#if blink, state == 1
state = False if pred > 0.1 else True
```

### 2. 주기적인 자세 교체 권고  
`face landmark detection`으로 얼굴의 가장 가운데 좌표를 가져오게 됨.  

위의 데모버전 처럼, 창에 `C`라고 표시되어 있는 부분이 얼굴의 중심을 의미함.  
```python
        face_loc = gaze.face_coords()
        if face_loc != None:
            face_x, face_y = face_loc.center().x, face_loc.center().y
            if face_std_x == 0 and face_std_y == 0:
                label2.configure(text="자세를 고치지 않아도 됩니다. 1분 뒤에 봬요~", fg="black")
                pose_time = datetime.now()
                face_std_x = face_x
                face_std_y = face_y
            elif abs(face_std_x - face_x) > 100 or abs(face_std_y - face_y) > 50:
                label2.configure(text="자세를 고치지 않아도 됩니다. 1분 뒤에 봬요~", fg="black")
                pose_time = datetime.now()
                face_std_x = face_x
                face_std_y = face_y
            elif (now_study_time - pose_time) > timedelta(minutes=1):
                label2.configure(text="슬슬 자세를 고치세요.", fg="red")
 ```
 현재 범위는 x좌표가 100이상, y좌표가 50이상 벗어나면 새로운 자세라고 판단하여, 자세의 기준이 옮겨짐.  
 또한 해당 자세가 50분 이상 지속될 경우, 경고를 띄우게 된다.  

### 3. Gaze tracking을 이용한 작업시간 측정
```python
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
```
`now_study_time`은 현재 시간을, `are_you_study`는 공부를 하고 있는지 아닌지를 측정한다.  
따라서, `are_you_study`가 `True`일 경우 작업시간을 흐르게 하도록 만든다.  

`gaze.out_of_monitor`는 다음과 같은 코드로 `monitor`를 주시하는 지 아닌지 판단할 수 있도록 만든다.  
```python
        def out_of_monitor(self):
        if self.gaze_in:
            if not self.pupils_located:
                self.gaze_in = False
            else:
                if not self.is_center():
                    self.gaze_in = False
        return self.gaze_in
```
`pupil_located`는 동공이 인식되는 경우 즉, 눈을 뜨고있는 경우이기 때문에, 만약 인식이 안될 경우 모니터 밖으로 시선이 분산되었다고 측정한다.


그리고 모니터를 응시하지 않는 경우 즉, `is_center()` 함수가 `False`를 `return` 하는 경우 모니터를 응시하지 않는 것으로 판단한다.  

## 실행파일 및 팝업창
팝업창은 `tkinter`를 이용하여 만들 수 있었다.  

다음과 같이 함수를 선언하여 `popup` 창을 띄웠다.
```python
root = Tk()
root.title('Eye Dear')
root.geometry("+500+10")

...

video_stream()
root.mainloop()
```
여기서 `video_stream()`은 반복적으로 팝업창에서 실행될 함수이다.  

또한 `Setup Button`을 만들어 프로그램 내에서 `Threshold Setting`을 바꿀 수 있도록 하였다.  
```python
def onClick():
    setup()

setup_btn = Button(root, text="setup", command=onClick, width=10, height=2, font= ('Helvetica 15 bold'))
setup_btn.grid(row=4, column=0)
```

## Reference

gazetrack https://github.com/antoinelame/GazeTracking  
cnn eyeblink https://github.com/kairess/eye_blink_detector  

## Licensing

This project is released by Antoine Lamé under the terms of the MIT Open Source License. View LICENSE for more information.
