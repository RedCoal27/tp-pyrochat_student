import logging

import dearpygui.dearpygui as dpg

from chat_client import ChatClient
from generic_callback import GenericCallback

from ciphered_gui import CipheredGUI


# Import Fernet
from cryptography.fernet import Fernet
# Import sha256
import hashlib

import base64

class FernetGUI(CipheredGUI):
    def encrypt(self, message):
        '''
        message : message à chiffrer
        
        Chiffre le message avec Fernet
        '''
        f = Fernet(self.key)
        return f.encrypt(bytes(message,'utf-8'))
    
    def decrypt(self, message):
        '''
        message : message à déchiffrer
        
        Déchiffre le message avec Fernet
        '''
        message = base64.b64decode(message['data'])
        f = Fernet(self.key)
        return f.decrypt(str(message, 'utf-8')).decode()

    def run_chat(self, sender, app_data) -> None:
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
