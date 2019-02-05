#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import yaml
import paho.mqtt.client as mqtt
# import paho.mqtt.publish as publish
import time

mqtt_cli = None


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True  # set flag
        broker = userdata
        print("{} connected. OK.".format(broker["address"]))
        # client.subscribe(topic)
        topic = "{}#".format(broker["prefix"])
        mid = client.subscribe(topic)
        print(f"subscribtion: {topic} -> {mid}")
    else:
        client.bad_connection_flag = True
        print(f"Bad connection. Returned code= {rc}")
        print("Result: {}".format(mqtt.connack_string(rc)))


def on_disconnect(client, userdata, rc):
    client.connected_flag = False
    print(f"broker DISCONNECTED. Result={rc}")


def on_publish(client, userdata, mid):
    print(f"-> {mid}")


def on_message(client, userdata, msg):
    print("<- {}: {}".format(msg.topic, msg.payload.decode("utf-8")))


def setup_device(device, cmnds, broker):
    commands = cmnds
    for cmd in commands:
        # print("- {}".format(mqtt_query(device, cmnd)))
        name, val = cmd.split()
        topic = "{prefix}cmnd/{device}/{cmnd}".format(prefix=broker["prefix"], device=device, cmnd=name)

        print("> {}: {}".format(topic, val))
        global mqtt_cli
        r = mqtt_cli.publish(topic, val)
        print(f"Published result:  {r}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="initial play to config tasmota system")
    parser.add_argument('-c', '--cfg', dest='cfg', help='playbook yaml file', default="playbook.yml")
    parser.add_argument('-b', '--broker', dest='broker', help='mqtt broker config file', default="broker.conf")
    args = parser.parse_args()

    with open(args.cfg, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

    commands = cfg["commands"]
    if not commands:
        print("No commands.")
        return

    with open(args.broker, 'r') as ymlfile:
        broker = yaml.load(ymlfile)

    global mqtt_cli
    mqtt_cli = mqtt.Client(client_id=broker["clientid"], clean_session=broker["cleansession"], userdata=broker)
    mqtt_cli.on_publish = on_publish
    mqtt_cli.on_message = on_message
    mqtt_cli.on_connect = on_connect
    mqtt_cli.on_disconnect = on_disconnect
    mqtt_cli.loop_start()

    try:
        mqtt_cli.connected_flag = False
        mqtt_cli.bad_connection_flag = False
        mqtt_cli.tls_set()
        if "username" in broker:
            mqtt_cli.username_pw_set(username=broker["username"], password =broker["password"])
        mqtt_cli.connect(host=broker["address"], port=broker["port"], keepalive=10)
    except:
        print("Bad connection.")
        return

    while not mqtt_cli.connected_flag and not mqtt_cli.bad_connection_flag:  # wait in loop
        print("In wait ...")
        time.sleep(3)
    if mqtt_cli.bad_connection_flag:
        mqtt_cli.loop_stop()
        return
        # sys.exit()

    for dev in cfg["sonoffs"]:
        print(f"\n{dev} ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        setup_device(dev, commands, broker)
        time.sleep(1)
        print("Ok")

    time.sleep(10)
    mqtt_cli.disconnect()
    mqtt_cli.loop_stop()


if __name__ == '__main__':
    try:
        print('-----------------------------------------------')
        main()
        print('-----------------------------------------------')
    except (SystemExit, KeyboardInterrupt):
        pass
    except:
        type, value, traceback = sys.exc_info()
        print("Exception: {}".format(value))
