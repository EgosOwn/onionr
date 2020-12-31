"""Wrap RinseOff, a c# CLI tool for secure data erasure via a keyfile.

Intended for encrypting database entries.

It is quite slow since it spawns an external process,
but an ext process is necessary to keep the key out
of memory as much as possible
"""

import os
from typing import Union

import subprocess

from filepaths import secure_erase_key_file, app_root
import logger

_rinseoff = f"{app_root}/src/rinseoff/rinseoffcli"


def generate_key_file():
    if os.path.exists(secure_erase_key_file):
        raise FileExistsError(
            "Key file for rinseoff secure erase already exists")

    with open(secure_erase_key_file, 'wb') as f:
        f.write(os.urandom(32))


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
        raise subprocess.CalledProcessError(
            "Error protecting string")


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
        raise subprocess.CalledProcessError(
            "Error unprotecting string")
