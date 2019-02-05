# -*- coding: utf-8 -*-


def gen_addr(device):
    xx, id = str.split(device, "_")
    if id:
        dd = int(id, 16) & 0x1fff
        return f"{device}-{dd}.local"
    else:
        return device


def get_dname(address):
    dev, xx = str.split(address, "-")
    return dev


