#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 tockards <tockards@tockards-ska>
#
# Distributed under terms of the MIT license.

"""
This server uses telnetlib to access the subprocess server
"""
import telnetlib
from sys import argv
import socket


def main2():
    """
    """

    con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con.connect((argv[1], int(argv[2])))
    args = ' '.join(argv[3:])+ '\n'
    con.send(args)
    lines = ''
    while True:
       data = con.recv(102400)
       if not data:
          break
       lines = lines + data
    print(lines)

def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    client = telnetlib.Telnet(argv[1], argv[2])
    args = ' '.join(argv[3:])
    #print(args)
    client.write(args+'\n')
    line = client.read_until('\n')
    while True:
        if 'end' in line:
            break
        print(line.strip())
        try:
            line = client.read_until('\n')
        except EOFError:
            break

if __name__ == "__main__":
    main2()

