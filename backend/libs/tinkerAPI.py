import threading


def cleanup():
    import ASUS.GPIO as GPIO
    import time
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.ASUS)
    GPIO.setup(164, GPIO.IN)
    GPIO.setup(166, GPIO.IN)
    GPIO.setup(167, GPIO.IN)
    time.sleep(0.5)
    GPIO.setup(164, GPIO.HIGH)
    GPIO.setup(166, GPIO.HIGH)
    GPIO.setup(167, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.setup(164, GPIO.LOW)
    GPIO.setup(166, GPIO.LOW)
    GPIO.setup(167, GPIO.LOW)
    # GPIO.cleanup()


def tinkerAPIServer():
    from flask import Flask
    app = Flask(__name__)

    @app.route("/")
    def status():
        return tell_system_status()

    @app.route("/status")
    def start():
        return tell_system_status()

    @app.route("/trigger1")
    def led1():
        download_thread = threading.Thread(target=triggerON, args=[164])
        download_thread.start()

        return "<p>Trigger with number {0} run successfully</p>".format("164")

    @app.route("/trigger2")
    def led2():
        download_thread = threading.Thread(target=triggerON, args=[166])
        download_thread.start()

        return "<p>Trigger with number {0} run successfully</p>".format("166")

    @app.route("/trigger3")
    def led3():
        download_thread = threading.Thread(target=triggerON, args=[167])
        download_thread.start()

        return "<p>Trigger with number {0} run successfully</p>".format("167")

    @app.route("/clean")
    def clean():
        cleanup()
        return "<p>Turn Off All leds</p>".format("167")

    @app.route("/reboot")
    def reboot():
        import os
        os.system("reboot")
        return "<p>Rebots Done</p>".format("167")
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=80, debug=True)


def tell_system_status():
    import psutil
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory()[2]
    disk_percent = psutil.disk_usage('/')[3]
    response = """<p style="text-align: center;">ٍSystem Status</p><table border="1" style="border-collapse: collapse; width: 66.6666%; height: 63px; margin-left: auto; margin-right: auto;"><tbody><tr style="height: 21px;"><td style="width: 2.26244%; height: 21px;"><span>Disk</span></td><td style="width: 2.26244%; height: 21px;">{0}%&nbsp;</td></tr><tr style="height: 21px;"><td style="width: 2.26244%; height: 21px;"><span>Memory</span></td><td style="width: 2.26244%; height: 21px;">{1}%&nbsp;</td></tr><tr style="height: 21px;"><td style="width: 2.26244%; height: 21px;"><span>CPU</span></td><td style="width: 2.26244%; height: 21px;">{2}%&nbsp;</td></tr></tbody></table>""".format(
        disk_percent, memory_percent, cpu_percent)
    return response


def triggerON(portNumber):
    import ASUS.GPIO as GPIO
    import time
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.ASUS)
    light = portNumber
    GPIO.setup(light, GPIO.OUT)
    GPIO.output(light, GPIO.LOW)
    try:
        print("open led: {0}".format(light))
        GPIO.output(light, GPIO.HIGH)
        time.sleep(3)
        GPIO.output(light, GPIO.LOW)
        print("close led: {0}".format(light))
    except KeyboardInterrupt:
        GPIO.cleanup()


tinkerAPIServer()
