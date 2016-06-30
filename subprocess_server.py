#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 tockards <tockards@tockards-ska>
#
# Distributed under terms of the MIT license.

"""
Basic Implementation of subprocess in tornado
"""
from __future__ import print_function

from sys import argv
from functools import partial

from tornado.tcpserver import TCPServer
from tornado.process import Subprocess
from tornado.iostream import PipeIOStream, StreamClosedError
from tornado.gen import coroutine, maybe_future, moment

from tornado.ioloop import IOLoop

class MyProcessServer(TCPServer):

    """Docstring for MyProcessServer. """

    @coroutine
    def handle_stream(self, stream, address):
        while not stream.closed():
            try:
                client_str = yield stream.read_until('\n')
            except StreamClosedError:
                break
            if client_str:
                yield call_process(client_str.split(), stream, address) #stream.write )
            else:
                pass
            yield stream.write("{'end':''}\n")


@coroutine
def call_process(cmd, stream, address, io_loop=None): #stdout_callback, io_loop=None):
    """ Calls process 

       cmd: command in a list e.g ['ls', '-la']
       stdout_callback: callback to run on stdout


       TODO: add some way of calling proc.kill() if the stream is closed
    """
    stdout_stream = Subprocess.STREAM 
    proc = Subprocess(cmd, stdout=stdout_stream)
    call_back = partial(on_exit, address)
    proc.set_exit_callback(call_back)

    pipe_stream = PipeIOStream(proc.stdout.fileno())

    while True:
        try:
            str_ = yield pipe_stream.read_bytes(102400, partial=True)
            yield stream.write(str_)
        except StreamClosedError:
            break

    print("end address: {}".format(address))

@coroutine
def on_exit(a, address):
    print ("exit {} {}".format(a, address))


if __name__ == "__main__":
    server = MyProcessServer()
    server.listen(8888)
    io_loop = IOLoop.current()
    io_loop.start()
