from pyicloud import PyiCloudService
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


def hash_file(file_path, hashing_algorithms="MD5"):
    hash_function = hashlib.new(hashing_algorithms)

    with open(file_path, "rb"):
        with open(file_path, "rb") as file:
            while chunk := file.read(8192):
                hash_function.update(chunk)
    return hash_function.hexdigest()


def clean_filename(filename):
    new_name = filename
    replacements = {
        "ΓÇÖ": "'",
        "Γ¡Æ": "~",
        "Γÿ╜": "-",
        "…": "...",
    }
    for old, new in replacements.items():
        new_name = new_name.replace(old, new)
    unsafe_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in unsafe_chars:
        new_name = new_name.replace(char, "_")
    return new_name


def push(local_folder_path, icloud_folder_name=None):
    print(f"push called with local_folder_path = {local_folder_path}")

    if not os.path.exists(local_folder_path):
        print(f"Local folder not found {local_folder_path}")
        return

    if icloud_folder_name is None:
        icloud_folder_name = os.path.basename(local_folder_path)
    
    if isinstance(icloud_folder_name, str):
        try:
            icloud_folder_name = api.drive[icloud_folder_name]
        except KeyError:
            print(f"iCloud folder {icloud_folder_name} does not exist, please create it first.")
            return

    for entry in os.listdir(local_folder_path):
        file_path = os.path.join(local_folder_path, entry)

        if os.path.isfile(file_path):
            print(f"Entry {entry} is a file, preparing upload.")
            try:

                icloud_file = icloud_folder_name[entry]

                # Download to temp file and hash
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_path = temp_file.name
                    download = icloud_file.open(stream=True)
                    temp_file.write(download.raw.read())
                
                local_hash = hash_file(file_path)
                icloud_hash = hash_file(temp_path)
                os.remove(temp_path) 
                
                if local_hash == icloud_hash:
                    print(f"Skipping {entry} already exists with same size.")
                    continue

                else:
                    icloud_file.delete()

            except KeyError:
                pass

            cleaned_name = clean_filename(entry)
            with open(file_path, "rb") as f:
                print(f"Uploading file: {cleaned_name}")
                icloud_folder_name.upload(f, filename=cleaned_name)

        elif os.path.isdir(file_path):

            print(f"Entry {entry} is a subfolder, starting recursion into {entry}")
            try:
                subfolder_node = icloud_folder_name[entry]
                print(f"Subfolder found: {entry}")
            except KeyError:
                subfolder_node = icloud_folder_name.mkdir(entry)
                print(f"Subfolder created: {entry}")

            push(file_path, subfolder_node)


def pull(local_folder_path, icloud_folder_name):

    if isinstance(icloud_folder_name, str):
        icloud_folder = api.drive[icloud_folder_name]

    if icloud_folder is not None:
        icloud_folder_contents = icloud_folder.dir()

        if icloud_folder_contents is not None:
            for entry in icloud_folder_contents:
                item = icloud_folder[entry]
                
                local_path = os.path.join(local_folder_path, item.name)
                
                if item.type == "file":
                    download = item.open(stream=True)
                    
                    with open(local_path, "wb") as out_file:
                        out_file.write(download.raw.read())

                elif item.type == "folder":
                    if not os.path.isdir(local_path):
                        os.mkdir(local_path)
                    pull(item.name, local_path)
        else:
            print(f"No entries found in iCloud folder '{icloud_folder_name}'.")
            return
    else:
        print(f"iCloud Folder {icloud_folder_name} does not exist.")
        return


def sync(local_folder_path,icloud_folder_name):
    push(local_folder_path,icloud_folder_name)
    pull(local_folder_path,icloud_folder_name)


def interface():
    local_folder_path = input("Enter the path for the local folder to send and receive from: ").strip()
    icloud_folder_name = input("Enter the name of the iCloud folder to send and receive from: ").strip()
    
    if not local_folder_path or not icloud_folder_name:
        print("Error: Both paths must be provided.")
        return
    
    print(f"Syncing {local_folder_path} with iCloud folder {icloud_folder_name}")
    sync(local_folder_path, icloud_folder_name)
    print("Sync complete!")

if __name__ == "__main__":
    interface()
