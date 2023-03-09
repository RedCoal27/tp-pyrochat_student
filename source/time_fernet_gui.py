import logging

import dearpygui.dearpygui as dpg

from chat_client import ChatClient
from generic_callback import GenericCallback

from fernet_gui import FernetGUI

import time

#nombre de bit d'un bloc
TAILLE_BLOCK = 128
#nombre d'octet
TAILLE_OCTET = 16


# Import Fernet
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

#



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
        temps = int(time.time())
        return f.encrypt_at_time(bytes(message,'utf-8'),current_time=temps)
    
    def decrypt(self, message):
        # Decrypts the given ciphertext, which must be a url-safe
        # base64-encoded bytes object. The key must be 32 url-safe
        # base64-encoded bytes.
        # The return value is a bytes object.
        try :
            message = base64.b64decode(message['data'])
            f = Fernet(self.key)
            temps = int(time.time())
            return f.decrypt_at_time(message,current_time=temps,ttl=30)
        except InvalidToken as e:
            logging.error(e)
            print("Invalid Token")
            return message
        

        



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # instanciate the class, create context and related stuff, run the main loop
    client = TimeFernetGUI()
    client.create()
    client.loop()
