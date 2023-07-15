import logging
from telegram.ext import Updater, MessageHandler, CommandHandler
from telegram import PhotoSize
from PIL import Image
import requests
from io import BytesIO
import cv2

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

# Define the handler function for swapping faces
def swap_faces(image_path1, image_path2):
    try:
        # Load the images
        image1 = cv2.imread(image_path1)
        image2 = cv2.imread(image_path2)

        # Detect faces in the images
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces1 = face_cascade.detectMultiScale(image1, 1.1, 5)
        faces2 = face_cascade.detectMultiScale(image2, 1.1, 5)

        if len(faces1) == 0 or len(faces2) == 0:
            return None

        # Swap the faces
        face1 = faces1[0]
        face2 = faces2[0]

        temp_image1 = image1.copy()
        temp_image1[face1[1]:face1[1] + face1[3], face1[0]:face1[0] + face1[2]] = image2[face2[1]:face2[1] + face2[3], face2[0]:face2[0] + face2[2]]

        temp_image2 = image2.copy()
        temp_image2[face2[1]:face2[1] + face2[3], face2[0]:face2[0] + face2[2]] = image1[face1[1]:face1[1] + face1[3], face1[0]:face1[0] + face1[2]]

        # Save the swapped images
        swapped_image_path1 = 'swapped_faces_1.jpg'
        swapped_image_path2 = 'swapped_faces_2.jpg'
        cv2.imwrite(swapped_image_path1, temp_image1)
        cv2.imwrite(swapped_image_path2, temp_image2)

        return swapped_image_path1, swapped_image_path2

    except Exception as e:
        logger.error(str(e))
        return None


# Define the handler function for receiving photos
def handle_photo(update, context):
    try:
        # Get the two most recent photos from the message
        photos = update.message.photo
        if len(photos) < 2:
            update.message.reply_text('Please provide two photos.')
            return

        # Get the file IDs of the photos
        file_id1 = photos[-2].file_id
        file_id2 = photos[-1].file_id

        # Get the file objects from the file IDs
        file1 = context.bot.get_file(file_id1)
        file2 = context.bot.get_file(file_id2)

        # Download the photos
        photo_bytes1 = BytesIO()
        file1.download(out=photo_bytes1)
        photo_bytes2 = BytesIO()
        file2.download(out=photo_bytes2)

        # Swap faces in the photos
        swapped_image_paths = swap_faces(photo_bytes1, photo_bytes2)

        if swapped_image_paths:
            # Send the swapped images back
            context.bot.send_photo(update.message.chat_id, photo=open(swapped_image_paths[0], 'rb'))
            context.bot.send_photo(update.message.chat_id, photo=open(swapped_image_paths[1], 'rb'))
        else:
            # Send a message if faces were not found
            update.message.reply_text('Could not detect faces in the provided photos.')

    except Exception as e:
        logger.error(str(e))


def main():
    # Set up the Telegram bot
    token = '5694266322:AAFuhovA-kFby3QNJjTlGUttDxWtYUNdYuA'
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    # Set up the message handler for photos
    photo_handler = MessageHandler(PhotoSize, handle_photo)
    dispatcher.add_handler(photo_handler)

    # Start the bot
    updater.start_polling()
    logger.info('Bot started.')
    updater.idle()


if __name__ == '__main__':
    main()
