import RPi.GPIO as GPIO
import MFRC522
import signal

import fire
import json
import logging
from tqdm import tqdm

def init():
    # Config logger
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    # Create an object of the class MFRC522
    card_reader = MFRC522.MFRC522()
    logging.info(f"Card Reader Initialized")

    return card_reader

def read_tag(card_reader):
    return card_reader.MFRC522_Anticoll()

def validate_tag(card_reader):
    # Get UID of Card
    status, uid = read_tag(card_reader)

    # If we have the UID, continue
    if status == card_reader.MI_OK:
        with open('./users.json') as f:
            users = json.load(f)
        logging.info(f"User file loaded")

        # Select the scanned tag
        card_reader.MFRC522_SelectTag(uid)

        for user, user_data in tqdm(users.items()):
            # Load Keys
            keys = user_data.keys()

            # Authenticate
            for key in keys:
                status = card_reader.MFRC522_Auth(card_reader.PICC_AUTHENT1A, 8, key, uid)

                # Check if authenticated
                if status == card_reader.MI_OK:
                    card_reader.MFRC522_Read(8)
                    card_reader.MFRC522_StopCrypto1()

                    logging.info(f"Tag validated with UID: {uid}")
                    logging.info(f"Tag belongs to User: {user}")

                    if user_data['uses_left'] > 1:
                        user_data['times_used'] = user_data['times_used']+1 if isinstance(user_data['times_used'], int) else user_data['times_used']
                        user_data['uses_left'] = user_data['uses_left']-1 if isinstance(user_data['uses_left'], int) else user_data['uses_left']

                        logging.info(f"Tag has {user_data['uses_left']} uses left")
                        return True
                    else:
                        logging.info(f"Tag has no uses left")
                        return False
                        

    return False


def main():
    card_reader = init()
    mode = "Running"
    logging.info(f"Lock is initialized in state: {mode}")

    while True:
        if mode == "Running":
            # Scan for cards    
            status, TagType = card_reader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

            # If a card is found
            if status == card_reader.MI_OK:
                logging.info(f"Reader Detected a Card : {uid}")            
                valid = validate_tag(card_reader)

                if valid:
                    toggled = toggle_lock(card_reader)

if __name__ == '__main__':
  fire.Fire(main)