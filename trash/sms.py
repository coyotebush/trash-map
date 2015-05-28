from twilio.rest import TwilioRestClient
import config

def send(body, to=config.TWILIO_RECIPIENT):
    client = TwilioRestClient(config.TWILIO_ACCOUNT, config.TWILIO_TOKEN)
    client.messages.create(to=to, from_=config.TWILIO_FROM, body=body)
