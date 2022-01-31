# Reminders Bot

Originall posted [here](https://reminders.preritdas.com). The read-me below includes information on how to setup the program from scratch, how to deploy it, and how to create shell shortcuts. The files in their full form are in the repository and are regularly updated when I make significant changes to the program. As such, the code below should only be used in context and as a guide for building the program.

----

Initially a feature of [Jeeves](https://jeeves.preritdas.com), the reminder bot is an interesting new way to push messages at scheduled times. Is it overkill? Yes. Necessary? No. Cool? Absolutely. 

I learned a ton through this project, particularly through the headaches of JSON interpretation and opening files through python. It had nothing to do with finance but was a fun coding project that will certainly play a role in a future trading bot to keep track of live-updated status files or text me intraday account updates.

## Step One: Initializing Data

In the way I attacked this project, there are two methods of accessing data. One is clearly worse than the other. The first is via CSV. I’ve learned that CSVs have their pros and cons but are generally outdated. They’re really good for accessing data quickly as comma delineation makes data-entering a breeze. But, commas represent delineation, meaning you can’t actually use commas in your messages. Also, it’s very easy to mess something up in syntax and lettering and get a `DecodeError`. 

An example of how a `reminders.csv` file would look:

```CSV
Reminder,Time
This is a test.,08-00
```

I first got the bot running with CSVs. Parsing the CSV is as simple as:

```python
import pandas as pd

def getRemindersCSV(CSVfilePath):
    remindersDF = pd.read_csv(CSVfilePath, index_col = 0)
    times = list(remindersDF["Time"])
    reminders = list(remindersDF["Reminder"])

while True:
    getRemindersCSV(CSVfilePath = 'Data/reminders.csv') # or wherever your reminders file is
```

Pros: easy to parse, and opening files in python isn’t necessary.
Cons: uses a DataFrame and renders it difficult to search for times and reminders within columns, thus requiring a standard list for `times` and `reminders`. 

Currently, my preferred option is JSON. It’s so beautifully organized, simple to create/edit, and most of all, you can have commas in the content! Long strings, punctuation, lists, variables… you name it. But, parsing the JSON is difficult because the following script doesn’t work as intended. 

```python
import json

def getRemindersJSON(JSONfilePath):
    with open(JSONfilePath, 'r') as f:
        return json.load(f)

while True:
    getRemindersJSON(JSONfilePath = 'Data/reminders.json") # or wherever your reminders file is
```

The issue arises with the fact that we need to `open()` the file to get its contents. If we’re constantly opening and closing the file to get contents, when we edit the file, for a period of time the file _wont exist_ while it’s resaving. So python will return a `FileNotFound` error. With this in mind, we can correct the issue like so:

```python
import json, time

def getRemindersJSON(JSONfilePath):
    try:
        with open(JSONfilePath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        time.sleep(1)
        with open(JSONfilePath, 'r') as f:
            return json.load(f)

while True:
    getRemindersJSON(JSONfilePath = 'Data/reminders.json") # or wherever your reminders file is
```

This will only fail if (a) the JSON is formatted incorrectly (returning a `json.JSONDecodeError` which we’ll deal with later) or (b) you’re crazy and are updating the file manually less than a second apart.

Pros: no need for Pandas. All processing is done in-house with built in libraries. Far greater possibility when writing reminders. 
Cons: Potential for many (correctible) raised exceptions. 

## Step Two: JSON Decode Error

The goal is to have the bot running forever. A mistake you make in updating your reminders shouldn’t quit the entire program. We want it to be as asynchronous as  possible, so your only input is replacing the `reminders.json` file. Thus, we need to deal with the dreaded `json.JSONDecodeError`.

Here’s how I did it…

```python
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
```

Essentially, if we get a JSON decoding error whose message is that it was expecting a value, we can pretty much assume it was an issue where we didn’t get parse the data fast enough for the JSON interpreter. So, we let `restartwait = True` which skips the rest of the interpreter script and tries again. It’ll keep doing this until the data is properly in place.

Next, if we get an error with the actual JSON body, we enter a loop that remains active until we set `errorDecoding = False`. Until then, it keeps looping and trying to see if we saved a copy of the JSON file that doesn’t have an interpretation error. To be efficient and user friendly, we’re only checking this when the modified time of the file changes. That way we can print the actual error every time you save the file with an error. It’ll print something along the lines of `Error decoding JSON. Expecting , delimiter on line xyz`… prompting you to find the area of interest and correct the file and try again. Once you save the file and no errors are raised, it stops shouting at you and sets `errorDecoding = False` which breaks the loop. 

## Step Three (Easiest!): Parsing Reminders and Delivery

Finally, the fun bit. Our JSON file is formatted like so:

```json
{
	"08-00": "This is a test! Commas, exclamations! All can fit nice and cleanly and be delivered with no issues.",
	"19-00": "Take out the trash."
}
```

In my case, a file like this is saved in a subdirectory `Data/` as `reminders.json`. 

The beauty of JSON interpretation is unlike CSVs with Pandas, we don’t have to convert the times and reminders to separate lists and use `for` loops to align the indices. Instead, `remindersJSON[currentTime]` _is equal to_ the reminder content we want. 

So… we set `currentTime = dt.now().strftime("%H-%M")`. This makes `currentTime` a string with the current time in the format 08-00 for 8am or 19-00 for 7pm. Then we say that if `currentTime` is in `remindersJSON` (the python dictionary because we used `json.load()`) grab the associated reminder and send it to us. This is beautiful(!) because when you convert a JSON file to a python dictionary you get an iterable object meaning you can sequentially search elements with the `in` statement in python. This allows us to say:

```python
from datetime import datetime as dt

while True:
    currentTime = dt.now().strftime("%H-%M")
    if currentTime in remindersJSON:
        reminder = remindersJSON[currentTime]
```
 
And that’s it! The `in` will search through each of the JSON ‘keys’, which in the way we’ve formatted the file are the times. 

The only issue is we only want to parse and deliver if our file is good to go (as in, the decoding process from above hasn’t indicated that it wants to re-loop until the JSON file actually appears. That happens when we’re saving as the file disappears for a period of milliseconds). So we just modify `if currentTime in remindersJSON` to be `if currentTime in remindersJSON and restartwait == False`. 

And that’s it, really. The only thing missing would be a function to actually text the message. Using the Vonage API it would look something like this:

```python
def textMe(content):
    status = sms.send_message(
        {
            "from": senderNo,
            "to": yourNumber,
            "text": content
        }
    )
    return status["messages"][0]["status"]
```
 
Then you can stick a `textMe(reminder)` after you print the reminder. My full code is below:

## One Last Thing

We want to make sure the program doesn’t remind us of the same thing twice. So we create a `reminded = []` array at the top and append it every time we send a reminder and then only send another reminder if it isn’t in that array. I’ve done so in my code below.

## My Code

```python
import json, os, time
from datetime import datetime as dt
from texts import textMe # this file isn't included but it's just my Vonage api keys and a function like above to text me content.

reminded = []

def getData():
    try:
        with open('Data/reminders.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        time.sleep(1)
        with open('Data/reminders.json', 'r') as f:
            return json.load(f)

def main():
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
                textMe("There has been an error decoding the JSON, sir. Likely you had a syntactical mishap. Do correct it immediately for the updated reminders to take effect.")
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
            reminder = remindersJSON[currentTime]
            if reminder in reminded:
                alreadyReminded = True
            if alreadyReminded != True:
                print(f"Reminder: {reminder}")
                textMe(reminder)
                reminded.append(reminder)

if __name__ == "__main__":
    main()
```

## Zsh Shortcuts

As I mentioned earlier, a key aspect of the bot we want to maintain is its independence. It doesn’t require stopping and starting or any sort of intervention, really. It handles exceptions and parses updated files in real-time. That gives us the freedom to make things _even easier_. 

What we can do, then, is use the `pysftp` library and a `zsh` or `bash` command line to streamline the process of updating reminders. 

### 1: Sending files via SFTP

The `pysftp` works really well in this way. 

```python
import pysftp

with pysftp.Connection(host = 'HOSTNAMEIP', username = 'USER', password = 'verysecretcode') as sftp:
    with sftp.cd('Reminders/Data'):
        sftp.put('Data/reminders.json)
```

This will SFTP into the server running this program, find the folder `Reminders/` for your project, the subdirectory `Data/`, and then put your `reminders.json` file from the `Data/` subdirectory in your local project folder. The structure looks like this:

Local directory:
```
Reminders/
    main.py
    otherfiles
    requirements.txt
    Data/
        reminders.json
```

Remote directory:
```
Reminders/
    main.py
    config.py
    __pycache__/
    venv/
    Data/
        requirements.json
```

`reminders.json` from the local directory replaces `reminders.json` from the remote directory. 

### 2: Sending files from desktop

I guess you could alter the SFTP script above to automatically move files from your desktop, but I found it more practical to leave it as is and write a separate script that moves a reminders.json file from the desktop to the `Data/` subdirectory on your computer. 

Using `shutil` to do this.

```python
import shutil

shutil.move(src = 'pathToDesktop/reminders.json', dst = 'pathToReminders/Data/reminders.json')
```

Easy. Combining these would look like so:

```python
import pysftp, shutil

def deployReminders():
    with pysftp.Connection(host = 'HOSTNAMEIP', username = 'USER', password = 'verysecretcode') as sftp:
        with sftp.cd('Reminders/Data'):
            sftp.put('Data/reminders.json)

def replaceFile():
    shutil.move(src = 'pathToDesktop/reminders.json', dst = 'pathToReminders/Data/reminders.json')
```

### 3: Doing all this with one zsh/bash command

Now the fun part. We need to modify this program slightly so it’s runnable, create a virtual environment, and then write a command-line alias to run it silently when it’s triggered. 

```python
import pysftp, shutil, sys

def deployReminders():
    with pysftp.Connection(host = 'HOSTNAMEIP', username = 'USER', password = 'verysecretcode') as sftp:
        with sftp.cd('Reminders/Data'):
            sftp.put('Data/reminders.json)

def replaceFile():
    shutil.move(src = 'pathToDesktop/reminders.json', dst = 'pathToReminders/Data/reminders.json')

if __name__ == "__main__":
    if 'move' in sys.argv and 'sftp' in sys.argv:
        replaceFile()
        deployReminders()
    if 'move' in sys.argv:
        replaceFile()
    if 'sftp' in sys.argv:
        deployReminders()
```

This allows us to run `python(3.8) main.py move sftp` to get a temporary `reminders.json` file from our desktop, move it to the proper place in our program files, and then deploy it via SFTP to the server which will then parse the file and remind us at the correct time.

The only thing we have to do before creating an alias is make a virtual environment and install necessary packages. From within the directory, make sure `python3.8-venv` is installed, then if `python3 -V = 3.8` we can use `python3 -m venv venv`, `source venv/bin/activate`, and `pip install -r requirements.txt` which should really just be `pysftp`.

Now, for the alias:

`alias deployreminders="cd pathToFolder && source venv/bin/activate && python main.py move sftp && deactivate && cd"`

Copy this into the ~/.bash_profile file, execute `source ~/.bash_profile` to bring it into effect, and then with a `reminders.json` file on the desktop give it a whirl. 

With one command, `deployreminders`, a `reminders.json` file from the Desktop will automatically move itself to the directory of your project and deploy itself to the reminders server in the correct place. The bot will recognize that there has been a change to its source of reminders, interpret the file, and get ready to execute at the correct time. If it detects an error, it will text you to let you know you should correct the file’s syntax and redeploy. During this whole process, no errors should be triggered by the bot because it’s handling JSON Decode exceptions as we want it to.

### Updating Reminders

The only downside to this setup is it requires us to create a new `reminders.json` file every time we use the `deployreminers` command. So we need a similar script to get the currently active file, so we can then update it and redeploy. 

We’re going to add to the SFTP script above so we can create a new alias, `getreminders`, for this feature.

```python
import pysftp, shutil, sys

def deployReminders():
    with pysftp.Connection(host = 'HOSTNAMEIP', username = 'USER', password = 'verysecretcode') as sftp:
        with sftp.cd('Reminders/Data'):
            sftp.put('Data/reminders.json)

def getReminders(): # the new one
    with pysftp.Connection(host = 'HOSTNAMEIP', username = 'USERNAME', password = 'donttellanyone') as sftp:
        with sftp.cd('Reminders/Data'):
            sftp.get(remotepath = 'reminders.json', localpath = 'PathToReminders/Data')

    # Copy file to Desktop
    shutil.copy('Data/reminders.json', 'pathToDesktop')

def replaceFile():
    shutil.move(src = 'pathToDesktop/reminders.json', dst = 'pathToReminders/Data/reminders.json')

if __name__ == "__main__":
    if 'move' in sys.argv and 'sftp' in sys.argv:
        replaceFile()
        deployReminders()
    if 'move' in sys.argv:
        replaceFile()
    if 'sftp' in sys.argv:
        deployReminders()
    if 'get' in sys.argv: # Add this too
        getReminders()
```

We’re using `shutil.copy()` this time instead of `shutil.move()` because we want the file to still remain in the Reminders/ local project directory. At least, I do. If you are okay with it being moved then use `shutil.move()` as when we’re deploying. When deploying, I want that `reminders.json` file cleared off my desktop as it’s temporary. 

The new alias for ~/.bash_profile:
alias getreminders="cd pathToReminders && source venv/bin/activate && python main.py get && deactivate && cd"

And now, we’re _really_ in business. Here’s the workflow.

## Workflow

Open a command line with ~/.bash_profile sourced. Type and execute the command getreminders. Give it a second to run and a file magically appears on your desktop, reminders.json. This file was flown all the way in from your remote server.

Open the file in a text editor and add some reminders. For example, add these to the file:

```json
{
    "08-00": "Wake up!",
    "10-00": "Jeeves never forgets."
}
```

Save the file (still on your desktop) and close it.

Pop open the command line again and execute the command deployreminders. It runs for a second, the file vanishes from your desktop, and assuming you don’t get a text saying there was a syntax error (your fault in writing the reminders, as in you forgot a comma or colon or something), you’re in business. The new reminders are now activated and you’ll be texted at the appropriate time.

The error text I’m referring to is this line in the full code from above:
```python
textMe("There has been an error decoding the JSON, sir. Likely you had a syntactical mishap. Do correct it immediately for the updated reminders to take effect.")
```

## Requirements

### Actual Reminders Bot 

```python
certifi==2021.10.8
cffi==1.15.0
charset-normalizer==2.0.10
cryptography==36.0.1
DateTime==4.3
Deprecated==1.2.13
idna==3.3
nexmo==2.5.2
numpy==1.22.1
pandas==1.4.0
pycparser==2.21
PyJWT==2.3.0
python-dateutil==2.8.2
pytz==2021.3
requests==2.27.1
six==1.16.0
urllib3==1.26.8
wrapt==1.13.3
zope.interface==5.4.0
```

### Local SFTP Python Environment

```python
bcrypt==3.2.0
cffi==1.15.0
cryptography==36.0.1
paramiko==2.9.2
pycparser==2.21
PyNaCl==1.5.0
pysftp==0.2.9 ## this is the main one. others are automatically installed dependencies. Still, install all from this file.
six==1.16.0
```

These can be installed at once, in their correct version, using the command `python3 -m pip install -r requirements.txt`. 