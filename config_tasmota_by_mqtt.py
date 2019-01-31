#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import yaml
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

prefix = "garden61"

def mqtt_query(dev, cmnd, param):
    mqtt_template = "{prefix}/cmnd/{device}/{cmnd}"
    qry = mqtt_template.format(device=dev, cmnd=cmnd)

    prefix = cfg["consumer"]["prefix"]
    publish.single( topic="{}{}".format(prefix, msg.topic)
                    , payload=msg.payload
                    , qos=msg.qos
                    , retain=msg.retain
                    , hostname=cfg["consumer"]["mqtt"]["hostname"]
                    , port=cfg["consumer"]["mqtt"]["port"]
                    , client_id=cfg["consumer"]["mqtt"]["client_id"]
                    , keepalive=7
                    )
    res = ""
    return res


def setup_device(device, cmnds):
    try:
        commands = cmnds
        for cmnd in commands:
            print("- {}".format(mqtt_query(device, cmnd)))

    except:
        print("*************\nUnexpected Error:", sys.exc_info()[1])


def main():
    import argparse
    parser = argparse.ArgumentParser(description="initial play to config tasmota system")
    parser.add_argument('-c', '--cfg', dest='cfg', help='playbook yaml file', default="playbook.yml")
    parser.add_argument('-b', '--broker', dest='broker', help='mqtt broker config file', default="broker.conf")
    args = parser.parse_args()

    with open(args.cfg, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

    with open(args.broker, 'r') as ymlfile:
        broker = yaml.load(ymlfile)

    commands = cfg["commands"]
    if not commands:
        print("Config Error: No commands.")
        return

    for dev in cfg["sonoffs"]:
        print("{}".format(dev))
        setup_device(dev, commands)
        print("Ok\n".format(dev))


if __name__ == '__main__':
    try:
        print('-----------------------------------------------')
        main()
    except (SystemExit, KeyboardInterrupt):
        print('-----------------------------------------------')
    except:
        type, value, traceback = sys.exc_info()
        print("Exception: {}".format(value))
