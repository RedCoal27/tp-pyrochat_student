import logging

from fernet_gui import FernetGUI

import time



# Import Fernet
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

# Import sha256
import hashlib

# Import base64
import base64

TTL = 30

class TimeFernetGUI(FernetGUI):
    def encrypt(self, message):
        '''
        message : message à chiffrer

        Chiffre le message avec Fernet et le timestamp
        '''
        f = Fernet(self.key)
        temps = int(time.time())
        return f.encrypt_at_time(bytes(message,'utf-8'),current_time=temps)
    
    def decrypt(self, message):
        '''
        message : message à déchiffrer
        
        Déchiffre le message avec Fernet et le timestamp
        '''
        try :
            message = base64.b64decode(message['data'])
            f = Fernet(self.key)
            temps = int(time.time())
            return f.decrypt_at_time(
                message,
                current_time=temps,
                ttl=TTL
                )
        except InvalidToken as e:
            logging.error(e)
            print("Invalid Token")
            raise InvalidToken


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # instanciate the class, create context and related stuff, run the main loop
    client = TimeFernetGUI()
    client.create()
    client.loop()
