from libs.database import *
from objectGet import *

input_video = "./VideoSource/{0}".format(connectionPath)
olc = int(olc)
trigger_object = triggerObject
debugMode = debug_Mode

objectGet(input_video, olc)
