import pyautogui
import keyboard as k

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

IMG_PATH = "src/recourses/aimTrainer/target.png"
OFFSET = 25
SEARCH_REGION = (465,149,1441,655)

def find_center():
    try:
        box = pyautogui.locateOnScreen(
            IMG_PATH,
            confidence=0.70,
            region=SEARCH_REGION,
            grayscale=True,
        )
        if box != None:
           return pyautogui.center(box)
        
    except pyautogui.ImageNotFoundException:
        pass
    return None

while not k.is_pressed("q"):
    pt = find_center()

    if pt != None:
        pyautogui.click(pt[0], pt[1])
    else:
        pass

#old pos : left = 415  top = 134  width = 1142 height = 532
#new pos : left = 159  top = 149  width = 974 height = 506