import logging

import dearpygui.dearpygui as dpg

import os

from chat_client import ChatClient
from generic_callback import GenericCallback

from basic_gui import BasicGUI,DEFAULT_VALUES


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


import base64


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

    def create(self):
        super().create()
        #change the name of the windows 
        dpg.set_viewport_title("Secure Chat")


    # Surcharger la fonction run_chat() pour y inclure la récupération du mot de passe
    def run_chat(self, sender, app_data) -> None:
        '''
        
        '''
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
        salt = "NeverGonnaGiveYouUp".encode()

        #clé de 16 octets
        self.key = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=TAILLE_OCTET,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        ).derive(password.encode())
        
    #fonction qui chiffre un message avec pkcs7 et retourn un tuple (iv, message)
    def encrypt(self, message):
        '''
        message: message à chiffrer 
        Chiffrer le message avec pkcs7 et retourner un tuple (iv, message_chiffré)
        '''
        # Fonction qui chiffre un message avec pkcs7
        iv = os.urandom(TAILLE_OCTET)
        encryptor = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        ).encryptor()
        padder = padding.PKCS7(TAILLE_BLOCK).padder()
        padded_data = padder.update(message.encode()) + padder.finalize()
        return (iv, encryptor.update(padded_data) + encryptor.finalize())
    

    #fonction qui déchiffre un message avec pkcs7 et retourne le message déchiffré
    def decrypt(self, message):
        '''
        iv: iv du message
        message: message à déchiffrer
        Déchiffrer le message avec pkcs7 et retourner le message déchiffré
        '''
        #Récupérer l'iv depuis le tuple en base64
        iv = base64.b64decode(message[0]['data'])
        #Récupérer le message depuis le tuple en base64
        message = base64.b64decode(message[1]['data'])
        # Fonction qui déchiffre un message avec pkcs7
        decryptor = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        ).decryptor()
        # Déchiffrer le message
        unpadder = padding.PKCS7(TAILLE_BLOCK).unpadder()
        data = decryptor.update(message) + decryptor.finalize()
        return unpadder.update(data) + unpadder.finalize()

    def send(self, text) -> None:
        # function called to send a message to all (broadcasting)
        #Chiffrer le message
        message = self.encrypt(text)
        #Envoyer le message
        self._client.send_message(message)


    #fonction de réception des messages
    def recv(self) -> None:
        if self._callback is not None:
            for user, message in self._callback.get():
                #essai de déchiffrer le message
                try:
                    #Déchiffrer le message
                    message = self.decrypt(message)
                    #Afficher le message déchiffré
                    self.update_text_screen(f"{user} : {message.decode()}")
                except:
                    #Afficher le message chiffré dans les logs
                    self._log.error(f"Error while decrypting message: {message}")
            self._callback.clear()



    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # instanciate the class, create context and related stuff, run the main loop
    client = CipheredGUI()
    client.create()
    client.loop()
