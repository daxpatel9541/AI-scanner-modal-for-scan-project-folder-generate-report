import requests
import os

url = "http://localhost:8000/api/upload/"
folder_path = "test_upload_folder"

files = []
paths = []

for root, _, dirs_files in os.walk(folder_path):
    for f_name in dirs_files:
        f_path = os.path.join(root, f_name)
        rel_path = os.path.relpath(f_path, os.path.dirname(folder_path))
        files.append(('files', open(f_path, 'rb')))
        paths.append(('paths', rel_path))

data = {
    'projectName': 'Test Folder Project',
    'mode': 'folder'
}
# We need to send paths as multiple values for the same key
# requests handles this if we pass a list of tuples to data or files
# Actually for data, we can pass a list of tuples to handle multiple values for the same key

payload_data = [('projectName', 'Test Folder Project'), ('mode', 'folder')]
payload_data.extend(paths)

try:
    response = requests.post(url, data=payload_data, files=files)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    for _, f in files:
        f.close()
