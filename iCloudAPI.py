from pyicloud import PyiCloudService
import os
import sys

with open(r"C:\Users\gavin\OneDrive\Desktop\Python_Projects\password.txt","r") as f:

    password = f.readline().strip()
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


def push(local_folder_path, icloud_folder_node=None):
    print(f"push() called with local_folder_path = {local_folder_path}")

    if not os.path.exists(local_folder_path):
        print(f"Local folder not found: {local_folder_path}")
        return

    if icloud_folder_node is None:
        icloud_folder_name = os.path.basename(local_folder_path)
        try:
            icloud_folder_node = api.drive[icloud_folder_name]
        except KeyError:
            print(f"iCloud folder '{icloud_folder_name}' does not exist. Please create it first.")
            return

    for entry in os.listdir(local_folder_path):
        file_path = os.path.join(local_folder_path, entry)

        if os.path.isfile(file_path):
            try:
                icloud_file = icloud_folder_node[entry]
                if os.stat(file_path).st_size == icloud_file.size:
                    print(f"Skipping {entry}, already exists with same size.")
                    continue
                else:
                    icloud_file.delete()
            except KeyError:
                pass

            cleaned_name = clean_filename(entry)
            with open(file_path, "rb") as f:
                print(f"Uploading file: {cleaned_name}")
                icloud_folder_node.upload(f, filename=cleaned_name)

        elif os.path.isdir(file_path):
            print(f"Recursing into subfolder: {entry}")
            try:
                subfolder_node = icloud_folder_node[entry]
                print(f"Subfolder found: {entry}")
            except KeyError:
                print(f"iCloud subfolder '{entry}' does not exist. Please create it first.")
                continue

            push(file_path, subfolder_node)





            
                
                


def pull(local_folder_path,icloud_folder_name):

    icloud_folder = api.drive[icloud_folder_name]

push(r"C:\Users\gavin\Downloads\ASMR")