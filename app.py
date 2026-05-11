import os
import time
import threading
import subprocess
import random
import webbrowser

try:
    import psutil
except ImportError:
    psutil = None

try:
    # pyrefly: ignore [missing-import]
    from flask import Flask, jsonify, request, send_from_directory
    from flask_cors import CORS
except ImportError:
    Flask = None

try:
    # pyrefly: ignore [missing-import]
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import pyautogui
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    import screeninfo
except ImportError:
    pyautogui = None

app = Flask(__name__, static_url_path='', static_folder='.') if Flask else None
if app:
    CORS(app)

# Ensure screenshots directory exists
if not os.path.exists('screenshots'):
    os.makedirs('screenshots')

@app.route('/') if app else None
def index():
    return send_from_directory('.', 'index.html')

@app.route('/screenshots/<path:path>')
def send_screenshot(path):
    return send_from_directory('screenshots', path)

@app.route('/stats') if app else None
def get_stats():
    if psutil:
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            net = psutil.net_io_counters()
            
            # Fix: Handle cases where freq might be None or unavailable
            freq_obj = psutil.cpu_freq()
            freq = f"{round(freq_obj.current / 1000, 1)}GHz" if freq_obj else "N/A"
            
            return jsonify({
                "cpu": cpu,
                "ram": ram,
                "net_sent": net.bytes_sent,
                "net_recv": net.bytes_recv,
                "status": "SECURE",
                "latency": freq
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        # Fallback Mock Data
        return jsonify({
            "cpu": random.randint(10, 20),
            "ram": random.randint(40, 50),
            "net_sent": 0,
            "net_recv": 0,
            "status": "MOCK MODE",
            "latency": "2.4GHz"
        })

@app.route('/security') if app else None
def security_scan():
    if psutil:
        try:
            connections = len(psutil.net_connections())
            status = "OPTIMAL" if connections < 50 else "CAUTION"
            return jsonify({
                "active_connections": connections,
                "status": status,
                "firewall": "ACTIVE",
                "threats": 0
            })
        except:
            pass
    
    return jsonify({
        "active_connections": 5,
        "status": "MOCK",
        "firewall": "ACTIVE",
        "threats": 0
    })

def set_volume(level):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        # level is 0.0 to 1.0
        volume.SetMasterVolumeLevelScalar(level, None)
        return True
    except:
        return False

def get_installed_apps():
    apps = {}
    # Common locations for shortcuts
    locations = [
        os.path.join(os.environ.get('ProgramData', ''), 'Microsoft\\Windows\\Start Menu\\Programs'),
        os.path.join(os.environ.get('AppData', ''), 'Microsoft\\Windows\\Start Menu\\Programs'),
        os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')
    ]
    
    for loc in locations:
        if os.path.exists(loc):
            for root, dirs, files in os.walk(loc):
                for file in files:
                    if file.endswith(".lnk"):
                        name = file.replace(".lnk", "").lower()
                        apps[name] = os.path.join(root, file)
    return apps

@app.route('/apps')
def list_apps():
    return jsonify(list(get_installed_apps().keys()))

@app.route('/chat', methods=['POST']) if app else None
def chat():
    data = request.json
    user_message = data.get('message', '').lower()
    
    # --- System Control Commands ---
    
    if "lock" in user_message:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return jsonify({"response": "Workstation secured, Boss."})

    if "screenshot" in user_message:
        if pyautogui:
            filename = f"ss_{int(time.time())}.png"
            path = os.path.join('screenshots', filename)
            pyautogui.screenshot(path)
            return jsonify({"response": f"Screenshot captured. Saved as {filename}. I've logged it in the secure archive."})
        return jsonify({"response": "Vision module (PyAutoGUI) not initialized."})

    if "volume up" in user_message:
        if set_volume(0.8): 
            return jsonify({"response": "Volume increased."})
        return jsonify({"response": "Failed to adjust audio protocols."})

    if "mute" in user_message:
        if set_volume(0.0):
            return jsonify({"response": "System audio muted."})

    if "display info" in user_message:
        try:
            screens = screeninfo.get_monitors()
            info = ", ".join([f"{s.width}x{s.height}" for s in screens])
            return jsonify({"response": f"Detecting {len(screens)} monitors. Primary resolution: {info}."})
        except:
            return jsonify({"response": "Unable to scan display hardware."})

    # --- App Automation Commands ---

    if user_message.startswith("open "):
        target_app = user_message.replace("open ", "").strip()
        installed_apps = get_installed_apps()
        
        if target_app in installed_apps:
            try:
                os.startfile(installed_apps[target_app])
                return jsonify({"response": f"Launching {target_app.capitalize()}, Boss."})
            except Exception as e:
                return jsonify({"response": f"Failed to execute {target_app}: {str(e)}"})

    if "open notepad" in user_message:
        subprocess.Popen(['notepad.exe'])
        return jsonify({"response": "Opening Notepad, Boss."})
    
    if "open opera" in user_message:
        try:
            # Common paths for Opera
            opera_paths = [
                os.path.expanduser("~\\AppData\\Local\\Programs\\Opera\\opera.exe"),
                "C:\\Program Files\\Opera\\opera.exe"
            ]
            for path in opera_paths:
                if os.path.exists(path):
                    subprocess.Popen([path])
                    return jsonify({"response": "Launching Opera browser."})
            return jsonify({"response": "Opera browser not found in standard paths."})
        except Exception as e:
            return jsonify({"response": f"Failed to open Opera: {str(e)}"})

    if "open gitbash" in user_message or "open git bash" in user_message:
        try:
            git_path = "C:\\Program Files\\Git\\git-bash.exe"
            if os.path.exists(git_path):
                subprocess.Popen([git_path])
                return jsonify({"response": "Initializing Git Bash environment."})
            return jsonify({"response": "Git Bash not found at standard location."})
        except Exception as e:
            return jsonify({"response": f"Failed to open Git Bash: {str(e)}"})

    if "open youtube" in user_message:
        webbrowser.open("https://www.youtube.com")
        return jsonify({"response": "Opening YouTube. Anything specific you're looking for?"})
    
    if "system status" in user_message:
        if psutil:
            return jsonify({"response": f"Systems are nominal. CPU is at {psutil.cpu_percent()}%. RAM usage is {psutil.virtual_memory().percent}%."})
        return jsonify({"response": "Systems are in mock mode. CPU appears stable."})

    return jsonify({"response": f"I've received your command: '{user_message}'. How should I proceed?"})

if __name__ == '__main__':
    if not app:
        print("ERROR: Flask is not installed. Please run 'pip install flask flask-cors'")
    else:
        print("FRIDAY Core booting up...")
        app.run(host='0.0.0.0', port=5000, debug=True)
