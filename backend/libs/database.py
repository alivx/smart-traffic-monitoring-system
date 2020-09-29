#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import MySQLdb as mdb
from .config import camera_id

try:
    con = mdb.connect(host="127.0.0.1", user="admin",
                      passwd="pass", db="aou_stat")
    cur = con.cursor()
    cur.execute("select connection_path from camera;")
    connectionPath = cur.fetchone()[0]
    cur.execute("select olc from camera;")
    olc = cur.fetchone()[0]
    cur.execute("select trigger_object from camera;")
    triggerObject = cur.fetchone()[0]
    cur.execute("select wild_range from camera;")
    wildRange = cur.fetchone()[0]
    cur.execute("select debugMode from camera;")
    debug_Mode = cur.fetchone()[0]
    cur.execute(
        "select person_email from person where person_id in (select personid from camera where id = %s);" % camera_id)
    email = cur.fetchone()[0]
    cur.execute(
        "select person_push_alert from person where person_id in (select personid from camera where id = %s);" % camera_id)
    person_push_alert = cur.fetchone()[0]
    cur.execute(
        "select person_email_alert from person where person_id in (select personid from camera where id = %s);" % camera_id)
    person_email_alert = cur.fetchone()[0]
except mdb.Error:
    print("Error %d: %s" % (e.args[0], e.args[1]))
    sys.exit(1)
finally:
    if con:
        con.close()
