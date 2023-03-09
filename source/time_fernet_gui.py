import logging

import dearpygui.dearpygui as dpg

import os

from chat_client import ChatClient
from generic_callback import GenericCallback

from fernet_gui import FernetGUI


#nombre de bit d'un bloc
TAILLE_BLOCK = 128
#nombre d'octet
TAILLE_OCTET = 16


# Import AES
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding
# Import Fernet
from cryptography.fernet import Fernet
# Import sha256
import hashlib

import base64

class TimeFernetGUI(FernetGUI):
    def encrypt(self, message):
        # Encrypts plaintext with the given key.
        # The key must be 32 url-safe base64-encoded bytes.
        # The plaintext must be a bytes object.
        # The return value is a url-safe base64-encoded bytes object.
        f = Fernet(self.key)
        return f.encrypt(bytes(message,'utf-8'))
    
    def decrypt(self, message):
        # Decrypts ciphertext with the given key.
        # The key must be 32 url-safe base64-encoded bytes.
        # The ciphertext must be a url-safe base64-encoded bytes object.
        # The return value is a bytes object.
        message = base64.b64decode(message['data'])
        f = Fernet(self.key)
        return f.decrypt(str(message, 'utf-8'))

    def run_chat(self, sender, app_data) -> None:
        # callback used by the connection windows to start a chat session
        host = dpg.get_value("connection_host")
        port = int(dpg.get_value("connection_port"))
        name = dpg.get_value("connection_name")
        password = dpg.get_value("connection_password")
        self._log.info(f"Connecting {name}@{host}:{port}")

        self._callback = GenericCallback()

        self._client = ChatClient(host, port)
        self._client.start(self._callback)
        self._client.register(name)

        dpg.hide_item("connection_windows")
        dpg.show_item("chat_windows")
        dpg.set_value("screen", "Connecting")

        #sha256().digest() + base64.b64encode() the  password
        self.key = hashlib.sha256(password.encode()).digest()
        self.key = base64.b64encode(self.key)



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # instanciate the class, create context and related stuff, run the main loop
    client = FernetGUI()
    client.create()
    client.loop()
