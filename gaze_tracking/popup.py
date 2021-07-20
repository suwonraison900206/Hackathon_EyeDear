#잘가,,,,
import tkinter as tk

class PopupWindow(tk.Tk):
    def __init__(self, master):
        tk.Tk.__init__(self, master)
        self.master=master
        self.title('alarm')
        self.geometry("300x200-500+140")
        self.resizable(False, False)

        blink_alarm_text = tk.Label(self, text='Blink_alarm : ')
        pose_alarm_text = tk.Label(self, text="Pose_alarm : ")
        working_time_text = tk.Label(self, text='working_time')

        blink_alarm_text.grid(row=0, column=0)
        pose_alarm_text.grid(row=1, column=0)
        working_time_text.grid(row=2, column=0)



'''
    # 1. 눈깜빡임 횟수가 1분에 15회 이하면 알람띄워주기
    def blink_alarm(self):
    blink_alarm_text = tk.Label(window, text='Blink_alarm : ')
    blink_alarm = tk.Label(window, text='Blinks too few times!\nBlink more often:)', fg='red')
    blink_alarm.place(x=0, y=0)
    blink_alarm.place(x=100, y=0)
    blink_alarm.after(1000, blink_alarm.destroy)

window=tk.Tk()
window.title('alarm')
window.geometry()
window.resizable(False, False)


#2. 자세 알람

#3. 작업시간측정

window.mainloop()
'''
