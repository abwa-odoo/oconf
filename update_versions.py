import os
import json
import re

def update_manifest_version(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == '__manifest__.py':
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        manifest_data = json.load(f)
                        # Only update if the version starts with '15.'
                        if 'version' in manifest_data and manifest_data['version'].startswith('15.'):
                            # Replace '15.' with '16.' at the start of the version string
                            manifest_data['version'] = re.sub(r'^15\.', '16.', manifest_data['version'])
                            
                            with open(file_path, 'w', encoding='utf-8') as fw:
                                json.dump(manifest_data, fw, indent=4)
                                print(f"Updated version in {file_path}")
                    except json.JSONDecodeError as e:
                        print(f"Error reading {file_path}: {e}")

# Replace 'your_directory_path' with the path to the directory you want to start from
update_manifest_version('/home/abwa/ODOO/src/odoo-psae/psae-al-khunaizan')
