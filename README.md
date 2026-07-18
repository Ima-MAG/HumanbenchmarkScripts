<div align="center">

# Human Benchmark Scripts

Desktop automation scripts for multiple **Human Benchmark** tests using **Selenium**, **OpenCV**, **MSS**, and **PyAutoGUI**.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)
![Status](https://img.shields.io/badge/Status-In%20Development-orange?style=for-the-badge)

</div>

---

## 📖 Overview

Human Benchmark Scripts is a desktop automation project designed to run and manage automation scripts for different Human Benchmark tests.

The first implemented module is **Aim Trainer**, which:

- Opens the user's default browser automatically.
- Detects the game region using Selenium.
- Captures only the game area with MSS.
- Detects targets using OpenCV color detection.
- Clicks the target using PyAutoGUI.

The project is built with a modular architecture, making it easy to add support for additional Human Benchmark tests in the future.

---

# ⚠ Disclaimer

> This repository is intended **only for educational purposes**, computer vision experimentation, and desktop automation learning.
>
> It is **not** intended to misrepresent human performance or compete unfairly on Human Benchmark.
>
> Please respect the website's Terms of Service.

---

# 📸 Project Preview

### Aim Trainer

<p align="center">
<img src="assets/gifs/aimtrainer_gif.gif" width="900">
</p>

---

# 📋 Requirements

- Windows 10 / Windows 11
- Python 3.10+
- Google Chrome, Microsoft Edge, or Firefox
- Internet connection

Install all dependencies:

```bash
pip install selenium mss opencv-python numpy pyautogui
```

Tkinter is included with most Windows Python installations.

Verify Tkinter:

```bash
python -m tkinter
```

---

# 🌐 Browser Support

| Browser | Status |
|----------|:------:|
| Google Chrome | ✅ |
| Microsoft Edge | ✅ |
| Mozilla Firefox | ✅ |
| Brave | ⚠ Not configured |
| Opera | ⚠ Not configured |
| Safari | ❌ Unsupported |

---

# 🚀 Features

<details>

<summary><strong>Click to expand</strong></summary>

- Desktop GUI built with Tkinter
- Modular script system
- Background multithreading
- Start / Stop controls
- Live activity log
- Automatic browser detection
- Chrome / Edge / Firefox support
- Selenium game-region detection
- High-speed screen capture (MSS)
- OpenCV target detection
- NumPy image processing
- PyAutoGUI mouse control
- DPI awareness
- Automatic region updates
- Graceful browser shutdown

</details>

---

# ⚙ Installation

Clone the repository:

```bash
git clone https://github.com/Ima-MAG/HumanbenchmarkScripts.git
```

Enter the project:

```bash
cd HumanBenchmarkScripts
```

---

# ▶ Running

Start the application:

```bash
python main.py
```

Then:

1. Select **Aim Trainer**
2. Click **Start**
3. Wait for the browser to open
4. Begin the Human Benchmark Aim Trainer test
5. The script will automatically detect and click the targets
6. Click **Stop** to terminate the automation

---

# ➕ Adding New Scripts

Every automation script should expose a `run()` function:

```python
def run(stop_event, log_callback=None):

    def log(message):
        if log_callback:
            log_callback(message)

    log("Script started.")

    while not stop_event.is_set():
        # automation logic
        pass

    log("Script stopped.")
```

Register the new script inside `main.py`.

### Planned scripts

- Reaction Time
- Sequence Memory
- Number Memory
- Verbal Memory
- Visual Memory
- Chimp Test
- Typing Test
