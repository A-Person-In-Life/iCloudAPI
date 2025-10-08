from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudAPIResponseException
import os
import sys
from shutil import copyfileobj
import hashlib
import tempfile
from tqdm import tqdm


def hash_file(file_path, algorithm="md5"):
    #copied from geeks for geeks
    hash_function = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hash_function.update(chunk)
    return hash_function.hexdigest()


def hash_check(local_path, icloud_file):    
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

    print(f"Starting upload of folder {os.path.basename(local_folder_path)}")
    for entry in os.listdir(local_folder_path):
        file_path = os.path.join(local_folder_path, entry)

        if os.path.isfile(file_path):
            print(f"Starting upload of file {entry} within folder {os.path.basename(local_folder_path)}")
            try:
                icloud_file = icloud_folder[entry]
                if not hash_check(file_path, icloud_file):
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
                print(f"Subfolder does not exist, please create {entry} in {os.path.basename(local_folder_path)}")

            print(f"Starting recursion with subfolder {entry}")
            push(file_path, subfolder_node)
        print(f"Finished upload of folder {os.path.basename(local_folder_path)}")




def pull(local_folder_path, icloud_folder):


    if isinstance(icloud_folder, str):
        try:
            icloud_folder = api.drive[icloud_folder]
        except KeyError:
            return

    if not os.path.exists(local_folder_path):
        os.mkdir(local_folder_path)

    print(f"Starting download of folder {icloud_folder.name}")
    for entry in icloud_folder.dir():
        item = icloud_folder[entry]
        local_path = os.path.join(local_folder_path, item.name)

        if item.type == "file":
            print(f"Starting download of file {entry} within folder {icloud_folder.name}")
            should_download = True
            if os.path.exists(local_path):
                should_download = hash_check(local_path, item)
            
            if should_download:
                download = item.open(stream=True)
                with open(local_path, "wb") as out_file:
                    out_file.write(download.raw.read())                

        elif item.type == "folder":
            print(f"Starting recursion with subfolder {entry}")
            pull(local_path, item)
    print(f"Finished download of folder {icloud_folder.name}")


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

    interface()