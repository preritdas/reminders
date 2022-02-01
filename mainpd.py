import pandas as pd
from datetime import datetime as dt
import time
from texts import *
import os

if __name__ == "__main__":
    print("Reminders bot is ready to go.") # wake-up
    while True:
        # Update Data (Reading all files in - File/IO)
        try:
            remindersDF = pd.read_json("Data/reminders.json")
            reminders = list(remindersDF["Reminder"])
            times = list(remindersDF['Time'])
        except:
            print("An error occured while parsing the csv.")
            textMe("An error occured while parsing the program. Do fix it.")
            modified = os.path.getmtime('Data/reminders.csv')
            while os.path.getmtime('Data/reminders.csv') == modified:
                time.sleep(1)

        if len(reminders) != len(times): # our csv is mismatched, so possibility of null return is caught
            print("Reminders aren't corresponding with times.")
            textMe("Reminders aren't corresponding with times. Please correct.")
            modified = os.path.getmtime('Data/reminders.csv') # since the file won't change in loop, we call it again. if it isn't fixed, it will be stuck.
            while os.path.getmtime('Data/reminders.csv'):
                time.sleep(1)

        currentTime = dt.now().strftime("%H-%M") # [AC, questions on how often this iterates.]
        if currentTime in times:
            for i in range(len(times)):
                if times[i] == currentTime:
                    break
                else:
                    pass
            message = reminders([i]) # [AC, changes made for clarity + easier debugging]
            response = textMe(message) # [AC, saving as local variable, then sending]
            print(f"Successfully reminded {reminders[i]}" if response == '0' else f"message failure at {dt.now()}")
            time.sleep(60)
        else:
            time.sleep(0.5)