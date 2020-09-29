from .alerting import *
from .config import *


def runTrigger(object, time):
    sendPush("Ali", "Object Found: {0} Capture Time: {1}".format(
        object, time), ACCESS_TOKEN_pushbullet)
