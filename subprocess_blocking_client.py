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


def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    client = telnetlib.Telnet(argv[1], argv[2])
    args = ' '.join(argv[3:])
    print(args)
    client.write(args+'\n')
    line = client.read_until('\n')
    while True:
        print(line.strip())
        try:
            line = client.read_until('\n')
        except EOFError:
            break

if __name__ == "__main__":
    main()

