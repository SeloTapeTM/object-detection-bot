class ObjectDetectionBot(Bot):
    def __init__(self, token, telegram_chat_url):
        super().__init__(token, telegram_chat_url)
        self.s3_client = boto3.client('s3')

    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if self.is_current_msg_photo(msg):
            photo_path = self.download_user_photo(msg)
            bucket = "omers3bucketpublic"
            img_name = f'tg-photos/{photo_path}'
            upload_response = upload_file(photo_path, bucket, img_name)  # upload the photo to S3
            if not upload_response:
                raise ClientError
            else:
                logger.info(f'Successfully uploaded {photo_path} to {bucket}/{img_name}')
            logger.info(f'before request')
            response_code, json_response = yolo5_request(img_name)  # send a request to the `yolo5` service for prediction
            logger.info(f'after request')
            if response_code is None:
                self.send_text(msg['chat']['id'], 'No detections found with your img.')
            else:
                counted_response_msg = count_prediction_msg(json_response)
                self.send_text(msg['chat']['id'], f'Detected objects: \n{counted_response_msg}')

        elif "text" in msg:
            message = msg['text'].lower()
            if '/start' in message:
                logger.info("Received text with command /start.")
                response_code = (f'Oh, Hi there!\nWelcome to Omer\'s Image Processing Bot!\n\nFor information on how to'
                                 f' use the bot type \"/help\".\nFor the list of actions type \"/actions\".')
                self.send_text(msg['chat']['id'], response_code)
            elif '/help' in message:
                logger.info("Received text with command /help.")
                response_code = (f'In order to use the bot properly you should send any photo, and in the \"caption'
                                 f'\" type in the name of the filter you want to apply.\n\nFor the list of filters available'
                                 f' right now you can type \"/filters\".')
                self.send_text(msg['chat']['id'], response_code)
            elif '/filters' in message:
                logger.info("Received text with command /filters.")
                response_code = (f'The list of filters is:\n\nBlur - Blurs the image.\nContour - Shows only outlines.\n'
                                 f'Salt n Pepper - Randomly place white and black pixels over the picture.\nSegment -'
                                 f' Makes all the bright parts white and all the dark parts black.\n\nFor information on how'
                                 f' to use the filters you can type \"/help\".')
                self.send_text(msg['chat']['id'], response_code)
            elif 'i hate you' in message:
                logger.info("Received text that says \"i hate you\".")
                response_code = f'You\'ve insulted me! And that is not nice at all.. You should be ashamed of yourself.'
                self.send_text(msg['chat']['id'], response_code)
            elif 'i love you' in message:
                logger.info("Received text that says \"i love you\".")
                response_code = f'Awwww, I love you too! <3 XOXO'
                self.send_text(msg['chat']['id'], response_code)
            elif 'supercalifragilisticexpialidocious' in message:
                logger.info("Received easteregg.")
                response_code = f'https://boulderbugle.com/super-secret-easter-egg-39tz7pni'
                self.send_text(msg['chat']['id'], response_code)
            elif 'supercalifragilisticexpialodocious' in message:
                logger.info("Received easteregg.")
                response_code = f'https://boulderbugle.com/super-secret-easter-egg-39tz7pni'
                self.send_text(msg['chat']['id'], response_code)
            else:
                response_code = (f'What you\'ve typed (\"{msg["text"]}\") is not a recognisable command.\n\nTry typing '
                                 f'\"/help\"')
                self.send_text(msg['chat']['id'], response_code)




class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])