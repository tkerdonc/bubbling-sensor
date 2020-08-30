#!/usr/bin/env python3
import RPi.GPIO as GPIO
import json
import os
import signal
import time
from datetime import datetime
from influxdb import InfluxDBClient


dataPin = 18

conf_path = os.environ.get("SENSOR_CONF") or "./conf.json"
conf = json.load(open(conf_path))
client = InfluxDBClient(host=conf['server_host'],
                        database="brewing",
                        use_udp=True,
                        udp_port=conf['server_port'])


GPIO.setmode(GPIO.BCM)
GPIO.setup(dataPin, GPIO.IN)

lastData = None

try:
    while 1:
        data = GPIO.input(dataPin)
        if data is not lastData:
            if data is 1:
                json_body = {
                    "tags": {
                        "beer": conf["current_beer"],
                        "phase": conf["current_phase"],
                    },
                    "points": [{
                        "measurement": "bubble",
                        "fields": {
                            "value": 1,
                        },
                        "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
                    }]
                }
                client.send_packet(json_body)
            lastData = data
        
except KeyboardInterrupt:
    GPIO.cleanup()

