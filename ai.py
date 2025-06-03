import subprocess
import platform
import psutil
import socket
import requests
from datetime import datetime
import os

def get_system_info(user_input):
    user_input_clean = user_input.lower().strip()

    if user_input_clean == "ram":
        mem = psutil.virtual_memory()
        return f"Total RAM: {round(mem.total / (1024 ** 3), 2)} GB, Used: {round(mem.used / (1024 ** 3), 2)} GB, Free: {round(mem.available / (1024 ** 3), 2)} GB"

    if user_input_clean == "uptime":
        uptime_seconds = int(datetime.now().timestamp() - psutil.boot_time())
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"System uptime: {hours} hours and {minutes} minutes"

    if user_input_clean == "time":
        return datetime.now().strftime("The current time is %I:%M %p")

    if user_input_clean == "date":
        return datetime.now().strftime("Today's date is %A, %B %d, %Y")

    if user_input_clean == "os":
        return f"You are using {platform.system()} {platform.release()}"

    if user_input_clean == "cpu":
        return f"CPU: {platform.processor()}, Cores: {psutil.cpu_count(logical=True)}"

    if user_input_clean == "cpu usage":
        return f"CPU Usage: {psutil.cpu_percent(interval=1)}%"

    if user_input_clean == "disk":
        disk = psutil.disk_usage('/')
        return f"Disk usage: {disk.percent}% used of {round(disk.total / (1024 ** 3), 2)} GB"

    if user_input_clean == "ip":
        hostname = socket.gethostname()
        try:
            ip = socket.gethostbyname(hostname)
            return f"Local IP address: {ip}"
        except Exception:
            return "Could not determine IP address"

    if user_input_clean == "external ip":
        try:
            external_ip = requests.get("https://api.ipify.org").text
            return f"External IP address: {external_ip}"
        except Exception:
            return "Could not determine external IP address"

    if user_input_clean == "hostname":
        return f"Hostname: {socket.gethostname()}"

    if user_input_clean == "battery":
        battery = psutil.sensors_battery()
        if battery:
            return f"Battery: {battery.percent}% {'Charging' if battery.power_plugged else 'Not Charging'}"
        else:
            return "Battery information not available"

    if user_input_clean == "network":
        interfaces = psutil.net_if_addrs()
        result = []
        for interface, addrs in interfaces.items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    result.append(f"{interface}: {addr.address}")
        return "\n".join(result)

    if user_input_clean == "processes":
        return f"Running processes: {len(psutil.pids())}"

    if user_input_clean == "shutdown":
        return "Shutdown is disabled for safety in this environment."

    if user_input_clean == "restart":
        return "Restart is disabled for safety in this environment."

    if user_input_clean == "list packages":
        try:
            output = subprocess.check_output(["pip", "list"], text=True)
            return output
        except Exception as e:
            return f"Error retrieving package list: {str(e)}"

    if user_input_clean == "list files":
        files = os.listdir('.')
        return "\n".join(files)

    return None  # Let the AI model handle all other queries

def chat_with_eis_ai(user_input):
    sys_response = get_system_info(user_input)
    if sys_response:
        return sys_response

    try:
        result = subprocess.run(
            ["ai.bat"],  
            input=user_input,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="ignore"
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return "Error: Sorry! server is down but I WILL BE BACK! soon..."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def main():
    print("Chat with EIS AI (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower().strip() in ['exit', 'quit']:
            break
        response = chat_with_eis_ai(user_input)
        print("EIS AI:", response)

if __name__ == "__main__":
    main()
