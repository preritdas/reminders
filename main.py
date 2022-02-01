import json, os, time
from datetime import datetime as dt
from texts import textMe
import time

def getData():
    try:
        with open('Data/reminders.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        time.sleep(1)
        with open('Data/reminders.json', 'r') as f:
            return json.load(f)

def main():
    print("Reminders bot is ready to go.", "\n")
    while True:
        restartwait = False
        alreadyReminded = False
        # Get the data
        try:
            remindersJSON = getData()
        except json.JSONDecodeError as jde:
            if "Expecting value" in str(jde):
                restartwait = True
                time.sleep(1)
            if restartwait != True:
                print("Error decoding JSON.", jde)
                textMe("Sir, there has been an error in decoding the JSON for our reminders framework. Do correct it immediately.")
                errorDecoding = True
                while errorDecoding == True:
                    fileModified = os.path.getmtime("Data/reminders.json")
                    while fileModified == os.path.getmtime('Data/reminders.json'):
                        time.sleep(0.1)
                    try:
                        file = open("Data/reminders.json", "r")
                        contents = file.read()
                        file.close()
                        remindersJSON = json.loads(contents)
                        errorDecoding = False
                    except json.JSONDecodeError as jde:
                        print("Error decoding JSON.", jde)
                        errorDecoding = True
                    except Exception as e:
                        print(f"Unxpected exception: {e}. Quitting.")
                        quit()

        # Check for reminders
        currentTime = dt.now().strftime('%H-%M')
        if currentTime in remindersJSON and restartwait != True:
            localtime = currentTime
            reminder = remindersJSON[localtime]
            print(f"Reminder: {reminder}")
            textMe(reminder)
            time.sleep(60)

if __name__ == "__main__":
    main()