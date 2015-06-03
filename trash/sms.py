from twilio.rest import TwilioRestClient
import config

def send(body, recipients=config.TWILIO_RECIPIENTS):
    client = TwilioRestClient(config.TWILIO_ACCOUNT, config.TWILIO_TOKEN)
    for to in recipients:
        client.messages.create(to=to, from_=config.TWILIO_FROM, body=body)
