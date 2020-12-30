import os
from typing import Union

import subprocess

from filepaths import secure_erase_key_file, app_root
import logger

_rinseoff = f"{app_root}/src/rinseoff/rinseoffcli"




def generate_key_file():
    if os.path.exists(secure_erase_key_file):
        raise FileExistsError

    process = subprocess.Popen(
                           ["dotnet", "run",
                            "--project", _rinseoff,
                            "keygen", f"{secure_erase_key_file}"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    res = process.communicate()

    if res[0]:
        for line in res[0].decode('utf-8').split('\n'):
            logger.info(line, terminal=True)
    if res[1]:
        logger.warn("Error when generating database encryption keyfile")
        for line in res[1].decode('utf-8').split('\n'):
            logger.error(line, terminal=True)
        raise subprocess.CalledProcessError



def protect_string(plaintext: Union[bytes, bytearray, str]) -> bytes:
    """Create a "secure" string. Dont really rely on this, and dont use for comms

    This is just to make forensics a little harder"""
    try:
        plaintext = plaintext.encode('utf-8')
    except AttributeError:
        pass

    process = subprocess.Popen(
                           ["dotnet", "run",
                            "--project", _rinseoff,
                            "store", "stdout", f"{secure_erase_key_file}"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           stdin=subprocess.PIPE)
    res = process.communicate(plaintext)

    if res[0] and not res[1]:
        return res[0]
    else:
        logger.warn("Error when protecting string for database", terminal=True)
        for line in res[1].decode('utf-8').split('\n'):
            logger.error(line, terminal=True)
        raise subprocess.CalledProcessError


def unprotect_string(ciphertext: Union[bytes, bytearray]) -> bytes:
    process = subprocess.Popen(
                           ["dotnet", "run",
                            "--project", _rinseoff,
                            "load", "stdin", f"{secure_erase_key_file}"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           stdin=subprocess.PIPE)
    res = process.communicate(ciphertext)

    if res[0] and not res[1]:
        return res[0]
    else:
        logger.warn(
            "Error when decrypting ciphertext from database", terminal=True)
        for line in res[1].decode('utf-8').split('\n'):
            logger.error(line, terminal=True)
        raise subprocess.CalledProcessError
