import sys
import threading
import time
import ctypes
import random

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QCheckBox, QLabel, 
    QHBoxLayout, QPushButton, QRadioButton
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont

SendInput = ctypes.windll.user32.SendInput

KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002

VK_F1 = 0x70
VK_F2 = 0x71
VK_CONTROL = 0x11

MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

running = False

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT)]
    _anonymous_ = ("u",)
    _fields_ = [("type", ctypes.c_ulong),
                ("u", _INPUT)]

INPUT_KEYBOARD = 1
INPUT_MOUSE = 0

def press_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ki = KEYBDINPUT(wVk=hexKeyCode, wScan=0, dwFlags=KEYEVENTF_KEYDOWN, time=0, dwExtraInfo=ctypes.pointer(extra))
    x = INPUT(type=INPUT_KEYBOARD, ki=ki)
    SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
    ki.dwFlags = KEYEVENTF_KEYUP
    SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
        
def press_key_down(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ki = KEYBDINPUT(wVk=hexKeyCode, wScan=0, dwFlags=KEYEVENTF_KEYDOWN, time=0, dwExtraInfo=ctypes.pointer(extra))
    x = INPUT(type=INPUT_KEYBOARD, ki=ki)
    SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def press_key_up(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ki = KEYBDINPUT(wVk=hexKeyCode, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=ctypes.pointer(extra))
    x = INPUT(type=INPUT_KEYBOARD, ki=ki)
    SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def right_click():
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

class AutoClickerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(240, 80)

        screen_geometry = QApplication.desktop().availableGeometry()
        self.move(
            screen_geometry.width() - self.width() - 5,
            screen_geometry.height() - self.height() - 5
        )


        layout = QVBoxLayout()

        self.label = QLabel("By.Hossam Salem , Press F10 to Active")
        self.label.setFont(QFont("Arial", 8, QFont.Bold))
        layout.addWidget(self.label)

        button_layout = QHBoxLayout()

        self.checkbox_f1 = QCheckBox("F1")
        self.checkbox_ctrl = QCheckBox("Ctrl")
        self.checkbox_f2 = QCheckBox("F2")
        self.checkbox_right_click = QCheckBox("Right Click")

        button_layout.addWidget(self.checkbox_f1)
        button_layout.addWidget(self.checkbox_ctrl)
        button_layout.addWidget(self.checkbox_f2)
        button_layout.addWidget(self.checkbox_right_click)

        layout.addLayout(button_layout)

        close_button = QPushButton("X")
        close_button.setFixedSize(20, 20)
        close_button.setStyleSheet("background-color: red; color: white; border-radius: 10px;")
        close_button.clicked.connect(self.close)

        self.radio_toggle = QRadioButton("Status")
        self.radio_toggle.toggled.connect(self.toggle_manual)

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.radio_toggle)
        control_layout.addStretch()
        control_layout.addWidget(close_button)

        layout.addLayout(control_layout)

        self.setLayout(layout)

        self.check_thread = threading.Thread(target=self.toggle_listener, daemon=True)
        self.check_thread.start()

    def toggle_manual(self):
        global running
        running = self.radio_toggle.isChecked()
        if running:
            threading.Thread(target=self.auto_press, daemon=True).start()
        else:
            pass

    def toggle_listener(self):
        import keyboard
        global running
        while True:
            keyboard.wait('F10')
            running = not running
            self.radio_toggle.setChecked(running)
            time.sleep(0.3)

    def auto_press(self):
        global running
        ctrl_pressed = False

        while running:
            try:
                if self.checkbox_f1.isChecked():
                    press_key(VK_F1)
                if self.checkbox_f2.isChecked():
                    press_key(VK_F2)
                if self.checkbox_right_click.isChecked():
                    right_click()
                if self.checkbox_ctrl.isChecked():
                    if not ctrl_pressed:
                        press_key_down(VK_CONTROL)
                        ctrl_pressed = True
                else:
                    if ctrl_pressed:
                        press_key_up(VK_CONTROL)
                        ctrl_pressed = False

                if random.randint(1, 20) == 10:
                    time.sleep(random.uniform(0.15, 0.3))

            except Exception as e:
                pass

            time.sleep(random.uniform(0.04, 0.06))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AutoClickerApp()
    window.show()
    sys.exit(app.exec_())
