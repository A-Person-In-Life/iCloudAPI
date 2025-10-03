from pyicloud import PyiCloudService
from shutil import copyfileobj
import os
import sys


with open(r"C:\\Python_Projects\\password.txt","r") as f:

    password = str(f.readline)
    print(password)
    api = PyiCloudService("gavin.d.weiner@icloud.com",password)

    if api.requires_2fa:
        print("Two-factor authentication required.")
        code = input("Enter the code you received of one of your approved devices: ")
        result = api.validate_2fa_code(code)
        print("Code validation result: %s" % result)

        if not result:
            print("Failed to verify security code")
            sys.exit(1)

        if not api.is_trusted_session:
            print("Session is not trusted. Requesting trust...")
            result = api.trust_session()
            print("Session trust result %s" % result)



def push(folder_name):

    folder = api.drive[folder_name]

    for entry in os.listdir(folder_name):
        
        if folder is not None:
            if not folder[entry]:
                with open(entry, "rb") as file:
                    folder.upload(file)
        else:
            print(f"Folder '{folder_name}' not found in iCloud Drive.")

def pull(folder_name):
    folder = api.drive[folder_name]
    pass

push("Test_iCloudAPI")