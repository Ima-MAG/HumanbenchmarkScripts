import time
import pyautogui
import keyboard as k
from pathlib import Path

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

PROJECT_DIR = Path(__file__).resolve().parent.parent
IMG_PATH = PROJECT_DIR / "src" / "aimTrainer" / "target.png"
SEARCH_REGION = (465,149,1441,655)

def find_center():
    try:
        box = pyautogui.locateOnScreen(
            str(IMG_PATH),
            confidence=0.70,
            region=SEARCH_REGION,
            grayscale=True,
        )
        if box != None:
           return pyautogui.center(box)
        
    except pyautogui.ImageNotFoundException:
        pass
    return None

def run(stop_event, log_callback=None):
    if log_callback:
        log_callback("Aim Trainer Started")
    
    try:
        while not stop_event.is_set():
            point = find_center()

            if point != None:
                pyautogui.click(point[0], point[1])
                if log_callback:
                    log_callback(f"Target clicked at x={point[0]}, y={point[1]}")
                else:
                    time.sleep(0.005)
    except pyautogui.FailSafeException:
        if log_callback:
            log_callback("Stopped by PyAutoGUI failsafe")
    
    except Exception as error:
        if log_callback:
            log_callback(f"Error: {error}")
            
    finally:
        if log_callback:
            log_callback("Aim Trainer stopped")

if __name__ == "__main__":
    import threading

    test_stop_event = threading.Event()

    def print_log(message):
        print(message)

    try:
        run(test_stop_event, print_log)

    except KeyboardInterrupt:
        test_stop_event.set()
        print("Stopped manually")