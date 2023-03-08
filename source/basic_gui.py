import logging

import dearpygui.dearpygui as dpg

#import AES
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding


import base64

import os

from chat_client import ChatClient
from generic_callback import GenericCallback



#nombre de bit
BIT = 128


# default values used to populate connection window
DEFAULT_VALUES = {
    "host": "127.0.0.1",
    "port": "6666",
    "name": "foo_"+os.urandom(16).hex()[:4]
}



class BasicGUI:
    """
    GUI for a chat client. Not so secured.
    """

    def __init__(self) -> None:
        # constructor
        self._client = None
        self._callback = None
        self._log = logging.getLogger(self.__class__.__name__)

    def _create_chat_window(self) -> None:
        # chat windows
        # known bug : the add_input_text do not display message in a user friendly way
        with dpg.window(label="Chat", pos=(0, 0), width=800, height=600, show=False, tag="chat_windows", on_close=self.on_close):
            dpg.add_input_text(default_value="Readonly\n\n\n\n\n\n\n\nfff",
                               multiline=True, readonly=True, tag="screen", width=790, height=525)
            dpg.add_input_text(default_value="some text", tag="input",
                               on_enter=True, callback=self.text_callback, width=790)

    def _create_connection_window(self) -> None:
        # windows about connexion
        with dpg.window(label="Connection", pos=(200, 150), width=400, height=300, show=False, tag="connection_windows"):

            for field in ["host", "port", "name"]:
                with dpg.group(horizontal=True):
                    dpg.add_text(field)
                    dpg.add_input_text(
                        default_value=DEFAULT_VALUES[field], tag=f"connection_{field}")

            dpg.add_button(label="Connect", callback=self.run_chat)

    def _create_menu(self) -> None:
        # menu (file->connect)
        with dpg.viewport_menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Connect", callback=self.connect)

    def create(self):
        # create the context and all windows
        dpg.create_context()

        self._create_chat_window()
        self._create_connection_window()
        self._create_menu()

        dpg.create_viewport(title='Secure chat - or not',
                            width=800, height=600)
        dpg.setup_dearpygui()
        dpg.show_viewport()

    def update_text_screen(self, new_text: str) -> None:
        # from a nex_text, add a line to the dedicated screen text widget
        text_screen = dpg.get_value("screen")
        text_screen = text_screen + "\n" + new_text
        dpg.set_value("screen", text_screen)

    def text_callback(self, sender, app_data) -> None:
        # every time a enter is pressed, the message is gattered from the input line
        text = dpg.get_value("input")
        self.update_text_screen(f"Me: {text}")
        self.send(text)
        dpg.set_value("input", "")

    def connect(self, sender, app_data) -> None:
        # callback used by the menu to display connection windows
        dpg.show_item("connection_windows")

    def run_chat(self, sender, app_data) -> None:
        # callback used by the connection windows to start a chat session
        host = dpg.get_value("connection_host")
        port = int(dpg.get_value("connection_port"))
        name = dpg.get_value("connection_name")
        self._log.info(f"Connecting {name}@{host}:{port}")

        self._callback = GenericCallback()

        self._client = ChatClient(host, port)
        self._client.start(self._callback)
        self._client.register(name)

        dpg.hide_item("connection_windows")
        dpg.show_item("chat_windows")
        dpg.set_value("screen", "Connecting")

    def on_close(self):
        # called when the chat windows is closed
        self._client.stop()
        self._client = None
        self._callback = None

    def recv(self) -> None:
        # function called to get incoming messages and display them
        if self._callback is not None:
            for user, message in self._callback.get():
                self.update_text_screen(f"{user} : {message}")
            self._callback.clear()

    def send(self, text) -> None:
        # function called to send a message to all (broadcasting)
        self._client.send_message(text)

    def loop(self):
        # main loop
        while dpg.is_dearpygui_running():
            self.recv()
            dpg.render_dearpygui_frame()

        dpg.destroy_context()



class CipheredGUI(BasicGUI):
    # secure chat client
    # Surcharger le constructeur pour y inclure le champ self._key
    def __init__(self) -> None:
        super().__init__()
        self.key = None

    # Surcharger la fonction _create_connection_window() pour y inclure un champ password  
    def _create_connection_window(self) -> None:
        # windows about connexion
        with dpg.window(label="Connection", pos=(200, 150), width=400, height=300, show=False, tag="connection_windows"):

            for field in ["host", "port", "name"]:
                with dpg.group(horizontal=True):
                    dpg.add_text(field)
                    dpg.add_input_text(
                        default_value=DEFAULT_VALUES[field], tag=f"connection_{field}")
            # Ajouter un champ password with hidden value
            with dpg.group(horizontal=True):
                dpg.add_text("password")
                dpg.add_input_text(
                    default_value="", tag=f"connection_password", password=True)
            dpg.add_button(label="Connect", callback=self.run_chat)


    # Surcharger la fonction run_chat() pour y inclure la récupération du mot de passe
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

        # Sel
        salt = "NeverGonnaGiveYouUp".encode('utf-8')

        #clé de 16 octets
        self.key = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=16,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        ).derive(password.encode('utf-8'))
        
    #fonction qui chiffre un message avec pkcs7 et retourn un tuple (iv, message)
    def encrypt(self, message):
        # Fonction qui chiffre un message avec pkcs7
        iv = os.urandom(16)
        encryptor = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        ).encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(message.encode('utf-8')) + padder.finalize()
        return (iv, encryptor.update(padded_data) + encryptor.finalize())
    

    #fonction qui déchiffre un message avec pkcs7 et retourne le message déchiffré
    def decrypt(self, iv, message):
        # Fonction qui déchiffre un message avec pkcs7
        decryptor = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        ).decryptor()
        # Déchiffrer le message
        unpadder = padding.PKCS7(BIT).unpadder()
        data = decryptor.update(message) + decryptor.finalize()
        return unpadder.update(data) + unpadder.finalize()

    def send(self, text) -> None:
        # function called to send a message to all (broadcasting)
        #Chiffrer le message
        message = self.encrypt(text)
        print("Envoyé : ", message)
        self._client.send_message(message)



    def recv(self) -> None:
        # function called to get incoming messages and display them
        if self._callback is not None:
            for user, message in self._callback.get():
                #string to tuple
                iv = base64.b64decode(message[0]['data'])
                #Récupérer le message
                message = base64.b64decode(message[1]['data'])

                print("Reçu : ", iv, message)
                #Déchiffrer le message
                message = self.decrypt(iv, message)
                #b string to string
                self.update_text_screen(f"{user} : {message.decode('utf-8')}")
            self._callback.clear()



    
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    # instanciate the class, create context and related stuff, run the main loop
    client = CipheredGUI()
    client.create()
    client.loop()
