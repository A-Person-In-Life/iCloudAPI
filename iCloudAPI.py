from pyicloud import PyiCloudService
import os
import sys
import datetime


with open(r"C:\Users\gavin\OneDrive\Desktop\Python_Projects\password.txt","r") as f:

    password = f.readline().strip()
    print(password)
    api = PyiCloudService("gavin.d.weiner@icloud.com",password)

    if api.requires_2fa:
        print("Two-factor authentication required.")
        code = input("Enter the code you received of one of your approved devices: ")
        result = api.validate_2fa_code(code)
        print(f"Code validation result: {result}")

        if not result:
            print("Failed to verify security code")
            sys.exit(1)

        if not api.is_trusted_session:
            print("Session is not trusted. Requesting trust...")
            result = api.trust_session()
            print(f"Session trust result {result}")



def push(local_folder_path,icloud_folder_name=None):
    print(f"push() called with local_folder_path = {local_folder_path}")

    if not os.path.exists(local_folder_path):
        print(f"Local folder not found: {local_folder_path}")
        return

    if icloud_folder_name is None:
        icloud_folder_name = os.path.basename(local_folder_path)

    icloud_folder = api.drive[icloud_folder_name]

    for entry in os.listdir(local_folder_path):
        file_path = os.path.join(local_folder_path, entry)
        print(file_path)

        if os.path.isfile(file_path):
            try:
                icloud_file = icloud_folder[entry]
                if os.stat(file_path).st_size == icloud_file.size:
                    continue
                else:
                    icloud_file.delete()
            except KeyError:
                pass

            with open(file_path, "rb") as f:
                print(f"Uploading file: {entry}")
                icloud_folder.upload(f)

        elif os.path.isdir(file_path):
            print("recursion")
            try:
                subfolder = icloud_folder[entry]
            except KeyError:
                subfolder = icloud_folder.create(entry)
                print(f"Created iCloud subfolder: {entry}")
            push(file_path, icloud_folder_name=entry)

            
                
                


def pull(local_folder_path,icloud_folder_name):

    icloud_folder = api.drive[icloud_folder_name]

push(r"C:\Users\gavin\OneDrive\Desktop\Test_iCloudAPI")