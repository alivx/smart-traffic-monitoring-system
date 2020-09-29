import json
import threading
import psutil
import requests


def tell_system_status():
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory()[2]
    disk_percent = psutil.disk_usage('/')[3]
    response = "Disk: {0}%, Memory: {1}, CPU: {2}%  ".format(
        disk_percent, memory_percent, cpu_percent)
    return response


def pushMetricInt(typex, body, host):
    if typex == "stat1":
        url = '{0}/widgets/stat1'.format(host)
    elif typex == "stat2":
        body = tell_system_status()
        url = '{0}/widgets/stat2'.format(host)
    elif typex == "stat3":
        url = '{0}/widgets/stat3'.format(host)
    else:
        pass
    headers = {'content-type': 'application/json'}
    data = {"auth_token": "YOUR_AUTH_TOKEN", "text": body}
    params = {}
    try:
        requests.post(url, params=params, data=json.dumps(data),
                      headers=headers, verify=False, timeout=1)
    except requests.ConnectionError:
        pass


def pushMetric(typex, body, host):
    download_thread = threading.Thread(
        target=pushMetricInt, args=[typex, body, host])
    download_thread.start()


def pushTriggerInt(typex, host):
    print('Getting a trigger type {0} to host: {1}'.format(typex, host))
    if typex == "trigger1":
        print("Run Trigger Type: {0}".format(typex))
        url = '{0}/trigger1'.format(host)
        print("Final URL for trigger is {0}".format(url))
    elif typex == "trigger2":
        print("Run Trigger Type: {0}".format(typex))
        url = '{0}/trigger2'.format(host)
        print("Final URL for trigger is {0}".format(url))
    elif typex == "trigger3":
        print("Run Trigger Type: {0}".format(typex))
        url = '{0}/trigger3'.format(host)
        print("Final URL for trigger is {0}".format(url))
    else:
        pass
    try:
        requests.get(url)
    except requests.ConnectionError:
        print("Error On URL")
        pass


def pushTrigger(xtype, host):
    download_thread = threading.Thread(
        target=pushTriggerInt, args=[xtype, host])
    download_thread.start()


pushTrigger("trigger1", "http://192.168.1.8:80")
pushTrigger("trigger2", "http://192.168.1.8:80")
pushTrigger("trigger3", "http://192.168.1.8:80")
