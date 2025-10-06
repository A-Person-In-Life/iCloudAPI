from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudAPIResponseException
import os
import sys
from shutil import copyfileobj
import hashlib
import tempfile

with open(r"C:\Users\gavin\OneDrive\Desktop\Python_Projects\password.txt", "r") as f:
    password = f.readline().strip()
    api = PyiCloudService("gavin.d.weiner@icloud.com", password)

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


def hash_file(file_path, algorithm="md5"):
    #copied from geeks for geeks
    hash_function = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hash_function.update(chunk)
    return hash_function.hexdigest()


def should_upload(local_path, icloud_file):    
    #copied chunking from geeks for geeks
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
        download = icloud_file.open(stream=True)
        while chunk := download.raw.read(8192):
            temp_file.write(chunk)

    local_hash = hash_file(local_path)
    icloud_hash = hash_file(temp_path)
    os.remove(temp_path)

    return local_hash != icloud_hash


def push(local_folder_path, icloud_folder=None):

    if not os.path.exists(local_folder_path):
        print("file doesn't exist")
        return

    if icloud_folder is None:
        folder_name = os.path.basename(local_folder_path)
        icloud_folder = api.drive[folder_name]
        
    elif isinstance(icloud_folder, str):
        icloud_folder = api.drive[icloud_folder]

    for entry in os.listdir(local_folder_path):
        file_path = os.path.join(local_folder_path, entry)

        if os.path.isfile(file_path):
            try:
                icloud_file = icloud_folder[entry]
                if not should_upload(file_path, icloud_file):
                    continue
                else:
                    icloud_file.delete()
            except KeyError:
                pass

            with open(file_path, "rb") as f:
                icloud_folder.upload(f, filename=entry)

        elif os.path.isdir(file_path):
            try:
                subfolder_node = icloud_folder[entry]
            except KeyError:
                print("subfolder doesn't exist, please make it in icloud")

            push(file_path, subfolder_node)




def pull(local_folder_path, icloud_folder):

    if isinstance(icloud_folder, str):
        try:
            icloud_folder = api.drive[icloud_folder]
        except KeyError:
            return

    if not os.path.exists(local_folder_path):
        os.mkdir(local_folder_path)

    for entry in icloud_folder.dir():
        item = icloud_folder[entry]
        local_path = os.path.join(local_folder_path, item.name)

        if item.type == "file":
            download = item.open(stream=True)
            with open(local_path, "wb") as out_file:
                out_file.write(download.raw.read())

        elif item.type == "folder":
            pull(local_path, item)


def sync(local_folder_path,icloud_folder_name):
    push(local_folder_path,icloud_folder_name)
    pull(local_folder_path,icloud_folder_name)


def interface():
    local_folder_path = input("Enter the path for the local folder to send and receive from: ").strip()
    icloud_folder_name = input("Enter the name of the iCloud folder to send and receive from: ").strip()
    
    if not local_folder_path or not icloud_folder_name:
        print("Both paths must be provided.")
        return

    sync(local_folder_path, icloud_folder_name)

if __name__ == "__main__":
    interface()
