#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import yaml
from urllib.request import urlopen
from urllib.parse import quote


def http_query(host, cmnd):
    http_template = "http://{host}/cm?&cmnd={cmnd}"
    qry = http_template.format(host=host, cmnd=quote(cmnd, safe=';'))
    r = urlopen(qry)
    res = ""
    if r.status == 200:
        res = r.read().decode('utf-8')
    else:
        res = "?: responce = {}".format(r.status)
    return res


def setup_device(host, cmnds, backlog, weblog):
    try:
        commands = cmnds
        if backlog and len(cmnds) != 1:
            commands = ["Backlog " + ";".join(cmnds)]

        wl = weblog and not backlog
        if wl:
            http_query(host, "weblog 2")
            print("weblog ON")
        # ------------------------------------------------------------------------------------------
        for cmnd in commands:
            print("- {}".format( http_query(host, cmnd) ))
        # ------------------------------------------------------------------------------------------
        if wl:
            http_query(host, "weblog 0")
            print("weblog OFF")


    except:
        print("*************\nUnexpected Error:", sys.exc_info()[1])


def main():
    import argparse
    parser = argparse.ArgumentParser(description="initial config tasmota system")
    parser.add_argument('-c', '--cfg', dest='cfg', help='config yaml file', default="playbook.yml")
    args = parser.parse_args()

    with open(args.cfg, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

    backlog = False
    if "backlog" in cfg.keys():
        backlog = cfg["backlog"]

    weblog = False
    if "weblog" in cfg.keys():
        weblog = cfg["weblog"]

    commands = cfg["commands"]
    if not commands:
        print("Config Error: No commands.")
        return

    if backlog and len(commands) > 30:
        print("Config Error: Maximum commands per backlog request must be <= 30.")
        return

    for host in cfg["hosts"]:
        print("{}".format(host))
        setup_device(host, commands, backlog, weblog)
        print("Ok\n".format(host))


if __name__ == '__main__':
    try:
        print('-----------------------------------------------')
        main()
    except (SystemExit, KeyboardInterrupt):
        print('-----------------------------------------------')
    except:
        type, value, traceback = sys.exc_info()
        print("Exception: {}".format(value))
