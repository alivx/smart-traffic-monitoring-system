import os
import smtplib
from .config import *
from .database import *


def sendPush(subject, body, ACCESS_TOKEN_pushbullet):
    """Send pushbullet notification
    Arguments:
            subject {[type]} -- [Subject of message]
            body {[type]} -- [Body of the message]
    """
    if person_push_alert == "on":
        os.system("curl -u {0}: https://api.pushbullet.com/v2/pushes -d type=note -d title='{1}' -d body='{2}' >/dev/null 2>&1".format(
            ACCESS_TOKEN_pushbullet, subject, body))


def sendEmail(object, camera):
    """Send an alert email

    Arguments:
        object {[type]} -- [Object type such as person, car ..etc]
        camera {[type]} -- [Source camera of detected object]
    """
    TO = email
    SUBJECT = SUBJECT_EMAIL
    gmail_sender = Gmail_sender
    gmail_passwd = Gmail_passwd
    server = smtplib.SMTP(SMTP, 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_sender, gmail_passwd)
    mainBody = "Hello,\n System has detect an:\n\tObject:[{0}]\n\tCamera {1}\n\nplease check site stat.monit.site for the feedback.".format(
        object, camera)
    BODY = '\r\n'.join(['To: %s' % TO,
                        'From: %s' % gmail_sender,
                        'Subject: %s' % SUBJECT,
                        '', mainBody])

    try:
        if person_email_alert == "on":
            server.sendmail(gmail_sender, [TO], BODY)
            print('email sent')
    except:
        print('error sending mail')

    server.quit()
    print("Sumlite Email sent...")
