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
                print('client stream closed {}'.format(address))
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
    proc = Subprocess(cmd, stdout=stdout_stream)# io_loop=io_loop)
    call_back = partial(on_exit, address)
    proc.set_exit_callback(call_back)

    pipe_stream = PipeIOStream(proc.stdout.fileno())



    print("start address: {}".format(address))
    count = 0
    stdout_chunk_callback = stream.write

    #def on_stdout_chunk(data):
    #    stdout_chunk_callback(data)
    #    if not pipe_stream.closed():
    #        pipe_stream.read_bytes(102400, on_stdout_chunk, None, True)

    #pipe_stream.read_bytes(102400, on_stdout_chunk, None, True)




    while True:
        try:
            count += 1
            str_ = yield pipe_stream.read_bytes(102400, partial=True)
            yield stream.write(str_)
            #yield maybe_future(stdout_callback (str_))
        except StreamClosedError:
            break
        if count > 99999:

            print (count)
    print("end address: {}".format(address))
    

@coroutine
def on_exit(a, address):
    print ("exit {} {}".format(a, address))

@coroutine
def main(ioloop=None):
    """TODO: Docstring for main.
    :returns: TODO

    """
     
    
    cmd = argv[1:]
    process_list = []
    yield call_process(cmd, 1, print, io_loop=ioloop)
    #proc2 = call_process(cmd, 2, print, io_loop=ioloop)
    #process_list.append(proc1)
    #process_list.append(proc2)
    #yield process_list


if __name__ == "__main__":
    server = MyProcessServer()
    server.listen(8888)
    io_loop = IOLoop.instance()
    io_loop.start()
    #main_partial = partial(main, ioloop = io_loop)
    #io_loop.run_sync(main_partial)
