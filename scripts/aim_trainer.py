import ctypes
import sys
import threading
import time
import cv2
import mss
import numpy as np
import pyautogui

from selenium import webdriver
from selenium.common.exceptions import (JavascriptException, NoSuchElementException, SessionNotCreatedException, StaleElementReferenceException, WebDriverException,)
from selenium.webdriver.common.by import By


URL = "https://humanbenchmark.com/tests/aim"
TARGET_SELECTOR = '[data-aim-target="true"]'
REGION_REFRESH_INTERVAL = 1.0
MIN_CLICK_INTERVAL = 0.012
MIN_TARGET_MOVEMENT = 5

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0


# =========================================================
# Windows DPI configuration
# =========================================================

def enable_dpi_awareness():

    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# =========================================================
# Default browser detection
# =========================================================

def get_windows_default_browser():

    if sys.platform != "win32":
        return None
    try:
        import winreg
    except ImportError:
        return None
    registry_paths = [(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Shell" r"\Associations\UrlAssociations\https\UserChoice", ), (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Shell" r"\Associations\UrlAssociations\http\UserChoice", ), ]

    prog_id = None

    for hive, registry_path in registry_paths:
        try:
            with winreg.OpenKey(hive, registry_path) as key:
                prog_id, _ = winreg.QueryValueEx(key, "ProgId")

            if prog_id:
                break

        except OSError:
            continue

    if not prog_id:
        return None

    value = prog_id.lower()

    if "brave" in value:
        return "brave"

    if "firefox" in value:
        return "firefox"

    if "msedge" in value or "edge" in value:
        return "edge"

    if "chrome" in value:
        return "chrome"

    if "opera" in value:
        return "opera"

    return None


# =========================================================
# Selenium browser creation
# =========================================================

def create_chrome_driver():
    options = webdriver.ChromeOptions()

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-logging"],
    )

    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")

    return webdriver.Chrome(options=options)


def create_edge_driver():
    options = webdriver.EdgeOptions()

    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")

    return webdriver.Edge(options=options)


def create_firefox_driver():
    options = webdriver.FirefoxOptions()

    options.add_argument("--width=1400")
    options.add_argument("--height=900")

    driver = webdriver.Firefox(options=options)
    driver.maximize_window()

    return driver


def create_driver(log_callback=None):

    def log(message):
        if log_callback:
            log_callback(message)

    default_browser = get_windows_default_browser()

    log("Default browser detected: " f"{default_browser or 'unknown'}")

    try:
        if default_browser == "firefox":
            log("Starting Firefox...")
            return create_firefox_driver()

        if default_browser == "edge":
            log("Starting Microsoft Edge...")
            return create_edge_driver()

        if default_browser == "chrome":
            log("Starting Google Chrome...")
            return create_chrome_driver()

        if default_browser in {"brave", "opera"}:
            log(
                f"{default_browser.title()} is the default browser, "
                "but this version supports Chrome, Edge and Firefox."
            )

        log("Trying Microsoft Edge as fallback...")

        try:
            return create_edge_driver()

        except WebDriverException:
            log("Edge failed. Trying Chrome...")
            return create_chrome_driver()

    except SessionNotCreatedException as error:
        raise RuntimeError(
            "Selenium could not create the browser session. "
            "Update Selenium and your browser."
        ) from error

    except WebDriverException as error:
        raise RuntimeError(
            "No compatible Selenium browser could be started."
        ) from error

# =========================================================
# Selenium game-region detection
# =========================================================

def get_game_region_data(driver):

    target = driver.find_element(
        By.CSS_SELECTOR,
        TARGET_SELECTOR,
    )

    data = driver.execute_script(
        """
        const target = arguments[0];

        /*
         * Prefer the site's desktop-only game wrapper when available.
         */
        let selected = target.closest(".desktop-only");

        /*
         * Fallback: walk upward and select the nearest parent that is
         * large enough to represent the game area.
         */
        if (!selected) {
            let current = target.parentElement;

            while (current && current !== document.body) {
                const rect = current.getBoundingClientRect();

                const visible =
                    rect.width > 0 &&
                    rect.height > 0;

                const largeEnough =
                    rect.width >= 450 &&
                    rect.height >= 250;

                const insideViewport =
                    rect.left < window.innerWidth &&
                    rect.top < window.innerHeight &&
                    rect.right > 0 &&
                    rect.bottom > 0;

                if (visible && largeEnough && insideViewport) {
                    selected = current;
                    break;
                }

                current = current.parentElement;
            }
        }

        if (!selected) {
            throw new Error("Game container was not found.");
        }

        const rect = selected.getBoundingClientRect();

        return {
            elementLeft: rect.left,
            elementTop: rect.top,
            elementRight: rect.right,
            elementBottom: rect.bottom,
            width: rect.width,
            height: rect.height,

            screenX: window.screenX,
            screenY: window.screenY,

            outerWidth: window.outerWidth,
            outerHeight: window.outerHeight,
            innerWidth: window.innerWidth,
            innerHeight: window.innerHeight,

            devicePixelRatio: window.devicePixelRatio
        };
        """,
        target,)

    if not data:
        raise RuntimeError("Browser returned no game-region information.")

    return data


def convert_browser_region_to_screen(data):
    screen_x = float(data["screenX"])
    screen_y = float(data["screenY"])

    outer_width = float(data["outerWidth"])
    outer_height = float(data["outerHeight"])

    inner_width = float(data["innerWidth"])
    inner_height = float(data["innerHeight"])

    element_left = float(data["elementLeft"])
    element_top = float(data["elementTop"])
    element_width = float(data["width"])
    element_height = float(data["height"])

    horizontal_difference = max(
        0.0,
        outer_width - inner_width,
    )

    left_border = horizontal_difference / 2.0

    top_browser_area = max(
        0.0,
        outer_height - inner_height - left_border,
    )

    left = int(round(
        screen_x
        + left_border
        + element_left
    ))

    top = int(round(
        screen_y
        + top_browser_area
        + element_top
    ))

    width = int(round(element_width))
    height = int(round(element_height))

    return left, top, width, height


def get_game_region(driver):
    data = get_game_region_data(driver)
    region = convert_browser_region_to_screen(data)

    left, top, width, height = region

    if width <= 0 or height <= 0:
        raise RuntimeError(f"Invalid game region detected: {region}")

    return region


def wait_for_game_region(driver, stop_event, log_callback=None,):

    def log(message):
        if log_callback:
            log_callback(message)

    log("Waiting for the Aim Trainer target...")
    log("Click Start inside the browser.")

    while not stop_event.is_set():
        try:
            region = get_game_region(driver)

            left, top, width, height = region

            log("Game region detected: " f"left={left}, top={top}, " f"width={width}, height={height}")

            return region

        except (NoSuchElementException, StaleElementReferenceException, JavascriptException,):
            pass

        except WebDriverException:
            raise

        except Exception:
            pass

        time.sleep(0.05)

    return None

# =========================================================
# OpenCV color detection
# =========================================================

def find_target_center(frame):
    bgr = cv2.cvtColor(
        frame,
        cv2.COLOR_BGRA2BGR,
    )

    hsv = cv2.cvtColor(
        bgr,
        cv2.COLOR_BGR2HSV,
    )

    lower_white = np.array(
        [0, 0, 175],
        dtype=np.uint8,
    )

    upper_white = np.array(
        [179, 75, 255],
        dtype=np.uint8,
    )

    mask = cv2.inRange(
        hsv,
        lower_white,
        upper_white,
    )

    kernel = np.ones(
        (3, 3),
        dtype=np.uint8,
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel,
    )

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    best_center = None
    best_score = 0.0

    for contour in contours:
        area = cv2.contourArea(contour)

        if area < 120 or area > 20_000:
            continue

        x, y, width, height = cv2.boundingRect(contour)

        if width < 25 or height < 25:
            continue

        if width > 180 or height > 180:
            continue

        aspect_ratio = width / height

        if not 0.75 <= aspect_ratio <= 1.25:
            continue

        perimeter = cv2.arcLength(
            contour,
            True,
        )

        if perimeter <= 0:
            continue

        circularity = (
            4.0
            * np.pi
            * area
            / (perimeter * perimeter)
        )

        if circularity < 0.35:
            continue

        center_x = x + width // 2
        center_y = y + height // 2

        score = area * circularity

        if score > best_score:
            best_score = score
            best_center = (
                center_x,
                center_y,
            )

    return best_center

# =========================================================
# Main GUI-compatible function
# =========================================================

def run(stop_event, log_callback=None):

    driver = None

    def log(message):
        if log_callback:
            log_callback(message)

    enable_dpi_awareness()

    try:
        log("Starting Aim Trainer automation...")

        driver = create_driver(log_callback)

        driver.get(URL)
        driver.implicitly_wait(0)

        search_region = wait_for_game_region(driver, stop_event, log_callback,)

        if search_region is None:
            log("Stopped before the game region was detected.")
            return

        left, top, width, height = search_region

        monitor = {"left": left, "top": top, "width": width, "height": height,}

        last_clicked_target = None
        last_click_time = 0.0
        last_region_refresh = time.perf_counter()

        log("Color detection started.")

        with mss.mss() as screen_capture:
            while not stop_event.is_set():
                now = time.perf_counter()

                # Recalculate the browser region periodically in case
                # the browser moves or changes size.
                if (now - last_region_refresh >= REGION_REFRESH_INTERVAL):
                    try:
                        updated_region = get_game_region(driver)

                        if updated_region != search_region:
                            search_region = updated_region
                            left, top, width, height = updated_region

                            monitor = {"left": left, "top": top, "width": width, "height": height,}

                            log("Game region updated: " f"left={left}, top={top}, " f"width={width}, height={height}")

                        last_region_refresh = now

                    except (NoSuchElementException, StaleElementReferenceException, JavascriptException,):
                        last_region_refresh = now

                    except WebDriverException:
                        raise

                screenshot = screen_capture.grab(monitor)
                frame = np.asarray(screenshot)

                target = find_target_center(frame)

                if target is None:
                    continue

                relative_x, relative_y = target

                screen_x = left + relative_x
                screen_y = top + relative_y

                now = time.perf_counter()

                moved_enough = (last_clicked_target is None or abs(screen_x - last_clicked_target[0]) > MIN_TARGET_MOVEMENT or abs(screen_y - last_clicked_target[1]) > MIN_TARGET_MOVEMENT)

                enough_time_passed = (now - last_click_time >= MIN_CLICK_INTERVAL)

                if moved_enough and enough_time_passed:
                    pyautogui.click(screen_x, screen_y,)

                    last_clicked_target = (screen_x, screen_y,)

                    last_click_time = now

        log("Stop requested.")

    except RuntimeError as error:
        log(f"Configuration error: {error}")

    except WebDriverException as error:
        log(f"Browser error: {error}")

    except mss.exception.ScreenShotError as error:
        log(f"Screen capture error: {error}")

    except Exception as error:
        log(f"Unexpected error: " f"{type(error)._name_}: {error}")

    finally:
        if driver is not None:
            try:
                driver.quit()
            except WebDriverException:
                pass

        log("Aim Trainer stopped.")

# =========================================================
# Standalone test
# =========================================================

if __name__ == "__main__":
    test_stop_event = threading.Event()

    print("Press Ctrl+C to stop.")

    try:
        run(stop_event=test_stop_event, log_callback=print,)

    except KeyboardInterrupt:
        test_stop_event.set()
        print("Stopped manually.")