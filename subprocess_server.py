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
from tornado.gen import coroutine, maybe_future

from tornado.ioloop import IOLoop

class MyProcessServer(TCPServer):

    """Docstring for MyProcessServer. """

    @coroutine
    def handle_stream(self, stream, address):
        while not stream.closed():
            try:
                client_str = yield stream.read_until('\n')
            except StreamClosedError:
                print('client stream closed {}'.format(address))
                break
            if client_str:
                yield call_process(client_str.split(), stream.write )
            else:
                pass
            stream.close()


@coroutine
def call_process(cmd, stdout_callback, io_loop=None):
    """ Calls process 

       cmd: command in a list e.g ['ls', '-la']
       stdout_callback: callback to run on stdout


       TODO: add some way of calling proc.kill() if the stream is closed
    """
    stdout_stream = Subprocess.STREAM 
    proc = Subprocess(cmd, stdout=stdout_stream, io_loop=io_loop)
    output_stream = PipeIOStream(proc.stdout.fileno())

    
    while not output_stream.closed():
        try:
            str_ = yield output_stream.read_until('\n')
            yield maybe_future(stdout_callback (str_))
        except StreamClosedError:
            pass

        


@coroutine
def main(ioloop=None):
    """TODO: Docstring for main.
    :returns: TODO

    """
     
    
    cmd = argv[1:]
    process_list = []
    proc1 = call_process(cmd, 1, print, io_loop=ioloop)
    #proc2 = call_process(cmd, 2, print, io_loop=ioloop)
    process_list.append(proc1)
    #process_list.append(proc2)
    yield process_list


if __name__ == "__main__":
    server = MyProcessServer()
    server.listen(8888)
    io_loop = IOLoop.instance()
    io_loop.start()
    #main_partial = partial(main, ioloop = io_loop)
    #io_loop.run_sync(main_partial)
