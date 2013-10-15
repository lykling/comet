#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
get_ip_address
"""

import socket
import fcntl
import struct


def get_ip_address(ifname):
    """
    Test
    """
    _sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(_sk.fileno(),
                                        0x8915,  # SIOCGIFADDR
                                        struct.pack('256s', ifname[:15])
                                        )[20: 24])


print get_ip_address('eth0')
