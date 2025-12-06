import os

from dotenv import load_dotenv
from twilio.rest import Client
from twilio.rest.api.v2010.account.message import MessageInstance

from utils.exceptions import TwilioError

load_dotenv()


class TwilioService:
    def __init__(self):
        self.account_sid: str = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token: str = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_wp: str = os.getenv("TWILIO_PHONE_WP")
        self.phone_sms: str = os.getenv("TWILIO_PHONE_SMS")
        self.client: Client = Client(self.account_sid, self.auth_token)

    def send_sms_message(self, to_number: str, body: str):
        message: MessageInstance = self.client.messages.create(
            from_=self.phone_sms,
            body=body,
            to=to_number,
        )
        if message.error_message:
            raise TwilioError(error=message.error_message)

    def send_whatsapp_template_message(
        self,
        to_number: str,
        content_sid: str,
        content_variables: dict[str, str],
    ):
        message: MessageInstance = self.client.messages.create(
            from_=f"whatsapp:{self.phone_wp}",
            content_sid=content_sid,
            content_variables=content_variables,
            to=f"whatsapp:{to_number}",
        )
        if message.error_message:
            raise TwilioError(error=message.error_message)

    def send_whatsapp_text_message(self, to_number: str, body: str):
        message: MessageInstance = self.client.messages.create(
            from_=f"whatsapp:{self.phone_wp}",
            body=body,
            to=f"whatsapp:{to_number}",
        )
        if message.error_message:
            raise TwilioError(error=message.error_message)


if __name__ == "__main__":
    phone = os.getenv("TWILIO_PHONE_TEST_TO")
    twilio_service = TwilioService()
    option = input("Test: 1 - SMS, 2 - WhatsApp: ")
    if option == "1":
        twilio_service.send_sms_message(
            to_number=phone,
            body="SMS working!",
        )
    elif option == "2":
        twilio_service.send_whatsapp_text_message(
            to_number=phone,
            body="Hi, how I can help you?",
        )
    else:
        print("Invalid option")
