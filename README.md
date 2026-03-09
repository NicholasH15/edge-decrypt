# edge-decrypt

This tool will extract credentials from Edge.

Edge encrypts stored credentials with a key stored in the browser profile. This key is then encrypted by both User DPAPI and SYSTEM DPAPI. Since Edge is run at the User level, this requires the use of a COM server that can encrypt and decrypt at the SYSTEM level, preventing User level infostealers from decrypting stored passwords. However, this can be bypassed via COM hijacking. Unfortunately, all previously stored passwords will be unreadable, thus making this intended to live on a target machine long term.

## stager.py
Modifies the HKCU registry to point COM requests to elevation_service.exe to a nonexistant binary. This downgrades Edge to User level DPAPI that can be decrypted by our User level extractor.

## extract.py
Extracts passwords from Edge and sends them over HTTPS to the server specified in URL

## Dependencies
pip install requests
pip install pywin32
pip install pycryptodome

## Credits
This project implements the technique described in:
https://www.cyberark.com/resources/threat-research-blog/c4-bomb-blowing-up-chromes-appbound-cookie-encryption
