from pyicloud import PyiCloudService
from shutil import copyfileobj
import os


with open("password.txt","r") as f:
    password = str(f.readline)
api = PyiCloudService("gavin.d.weiner@icloud.com",password)`


def push(folder_name):

    folder = api.drive[folder_name]

    for entry in os.listdir(folder_name):
        
        if folder is not None:
            if not folder[entry]:
                with open(entry, "rb") as file:
                    folder.upload(file)
        else:
            print(f"Folder '{folder_name}' not found in iCloud Drive.")
        