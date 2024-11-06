from django.core.mail import EmailMessage
from django.conf import settings

def send_email(changed_entity):

    email_message = EmailMessage(
        'Entity changed', # email subject
        f'Entity "{changed_entity}" has changed, please make appropriate change.\n\n\nhttp://203.161.53.121:8000\nadmin\nmedimopsbot321',
        settings.EMAIL_HOST_USER, # email sender
        ['theprotonguy@yahoo.com'] # email  receiver 
    )

    email_message.fail_silently = True
    email_message.send()