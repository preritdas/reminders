import pysftp, shutil, sys

def deployReminders():
    # Optional: move file to project directory from desktop
    shutil.move(src = '~/Desktop/reminders.json', dst = 'Data/reminders.json')

    # Deploy to server
    with pysftp.Connection(host = 'ServerName', username = 'ServerUsername', password = 'AccountPassword') as sftp:
        with sftp.cd('Reminders'):
            sftp.put('Data/reminders.json')

def getReminders():
    # Get file from server
    with pysftp.Connection(host = 'ServerName', username = 'ServerUsername', password = 'AccountPassword') as sftp:
        with sftp.cd('Reminders'):
            sftp.put(remotepath = 'reminders.json', localpath = 'Data/reminders.json')

    # Optional: copy file to desktop for easy editing
    shutil.copy(src = 'Data/reminders.json', dst = '~/Desktop/reminders.json')

if __name__ == "__main__":
    if 'deploy' in sys.argv:
        deployReminders()
    elif 'get' in sys.argv:
        getReminders()