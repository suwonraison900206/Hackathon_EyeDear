from __future__ import division
import os
import cv2
import dlib
from .eye import Eye
from .calibration import Calibration
from keras.models import load_model


class GazeTracking(object):
    """
    This class tracks the user's gaze.
    It provides useful information like the position of the eyes
    and pupils and allows to know if the eyes are open or closed
    """

    def __init__(self):
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.calibration = Calibration()
        self.face_location = None
        # _face_detector is used to detect faces
        self._face_detector = dlib.get_frontal_face_detector()

        # _predictor is used to get facial landmarks of a given face
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat"))
        self._predictor = dlib.shape_predictor(model_path)

        #blinking model
        model_path = os.path.abspath(os.path.join(cwd, "trained_models/2021_07_12_15_20_04.h5"))
        self.blinking_model = load_model(model_path)
        self.blinking_model.summary()

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

        #check gaze out of monitor
        self.gaze_in = False # if False, out of monitor

    @property
    def pupils_located(self):
        """Check that the pupils have been located"""
        try:
            int(self.eye_left.pupil.x)
            int(self.eye_left.pupil.y)
            int(self.eye_right.pupil.x)
            int(self.eye_right.pupil.y)
            return True
        except Exception:
            return False

    def _analyze(self):
        """Detects the face and initialize Eye objects"""
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_detector(frame)
        try:
            landmarks = self._predictor(frame, faces[0])
            self.eye_left = Eye(frame, landmarks, 0, self.calibration, self.blinking_model)
            self.eye_right = Eye(frame, landmarks, 1, self.calibration, self.blinking_model)
            self.face_location = faces[0]
            self.gaze_in = True

        except IndexError:
            # print("Error Occur!!")
            self.eye_left = None
            self.eye_right = None
            self.face_location = None
            self.gaze_in = False

    def out_of_monitor(self):
        if self.gaze_in:
            if not self.pupils_located:
                self.gaze_in = False
            else:
                if not self.is_center():
                    self.gaze_in = False
        return self.gaze_in

    def refresh(self, frame):
        """Refreshes the frame and analyzes it.

        Arguments:
            frame (numpy.ndarray): The frame to analyze
        """
        self.frame = frame
        self._analyze()

    def pupil_left_coords(self):
        """Returns the coordinates of the left pupil"""
        if self.pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.eye_left.origin[1] + self.eye_left.pupil.y
            return (x, y)

    def pupil_right_coords(self):
        """Returns the coordinates of the right pupil"""
        if self.pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.eye_right.origin[1] + self.eye_right.pupil.y
            return (x, y)

    def horizontal_ratio(self):
        """Returns a number between 0.0 and 1.0 that indicates the
        horizontal direction of the gaze. The extreme right is 0.0,
        the center is 0.5 and the extreme left is 1.0
        """
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.x / (self.eye_left.center[0] * 2 - 10)
            pupil_right = self.eye_right.pupil.x / (self.eye_right.center[0] * 2 - 10)
            return (pupil_left + pupil_right) / 2

    def vertical_ratio(self):
        """Returns a number between 0.0 and 1.0 that indicates the
        vertical direction of the gaze. The extreme top is 0.0,
        the center is 0.5 and the extreme bottom is 1.0
        """
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.y / (self.eye_left.center[1] * 2 - 10)
            pupil_right = self.eye_right.pupil.y / (self.eye_right.center[1] * 2 - 10)
            return (pupil_left + pupil_right) / 2


    #tracking 을 각자 눈에 맞게 훈련시키는 방안을 만들자. (평균값을 내기)
    def is_right(self):
        """Returns true if the user is looking to the right"""
        if self.pupils_located:
            return self.horizontal_ratio() <= self.right_threshold

    def is_left(self):
        """Returns true if the user is looking to the left"""
        if self.pupils_located:
            return self.horizontal_ratio() >= self.left_threshold

    def is_up(self):
        """Returns true if the user is looking to the left"""
        if self.pupils_located:
            return self.vertical_ratio() <= self.upward_threshold

    def is_down(self):
        """Returns true if the user is looking to the left"""
        if self.pupils_located:
            return self.vertical_ratio() >= self.under_threshold

    def is_center(self):
        """Returns true if the user is looking to the center"""
        if self.pupils_located:
            return self.is_right() is not True and self.is_left() is not True

    def is_blinking(self):
        """Returns true if the user closes his eyes"""
        #blink 하는 순간 원래 pupil 없어지는 거임
        if self.eye_left is not None and self.eye_right is not None:
            return self.eye_left.blinking & self.eye_right.blinking
        """
        if self.pupils_located:
            blinking_ratio = (self.eye_left.blinking + self.eye_right.blinking) / 2
            return blinking_ratio > 3.8
        """

    def face_coords(self):
        return self.face_location

    def annotated_frame(self):
        """Returns the main frame with pupils highlighted"""
        frame = self.frame.copy()

        if self.pupils_located:
            color = (0, 255, 0)
            x_left, y_left = self.pupil_left_coords()
            x_right, y_right = self.pupil_right_coords()
            cv2.line(frame, (x_left - 5, y_left), (x_left + 5, y_left), color)
            cv2.line(frame, (x_left, y_left - 5), (x_left, y_left + 5), color)
            cv2.line(frame, (x_right - 5, y_right), (x_right + 5, y_right), color)
            cv2.line(frame, (x_right, y_right - 5), (x_right, y_right + 5), color)

        return frame

    def file_check(self):
        """Checking file changed after SetUp"""
        return self.left_threshold, self.right_threshold, self.upward_threshold, self.under_threshold