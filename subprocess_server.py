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

import logging
import json as json

from sys import argv
from functools import partial


from tornado import options 

from tornado.tcpserver import TCPServer
from tornado.process import Subprocess
from tornado.iostream import PipeIOStream, StreamClosedError
from tornado.gen import coroutine, maybe_future, moment
from tornado.ioloop import IOLoop




logger = logging.getLogger()
logging.basicConfig()




class ReadServerStreamHandler(object):

    def __init__(self, stream, address, script,  logger):
        """TODO: Docstring for __init__.

        :stream: TODO
        :returns: TODO

        """
        self._logger = logger
        self.stream = stream
        self.address = address
        self.script = script

    @coroutine
    def on_connect(self):
        """TODO: Docstring for on_connect.
        :returns: TODO

        """
        yield self.dispatch()

    @coroutine
    def dispatch(self):
        """TODO: Docstring for dispatch.
        :returns: TODO

        """
        while not self.stream.closed():
            try:
                client_str = yield self.stream.read_until('\n')
            except StreamClosedError:
                break
            if client_str:
                yield self.process_request(client_str)
            else:
                pass
            yield self.stream.write("{'end':''}\n")
        pass


    @coroutine
    def process_request(self, line):
        """TODO: Docstring for process_request.
        :returns: TODO

        """
        req = json.loads(line)
        req = req['params']
        starttime = req['seconds'][0]
        endtime = req['seconds'][1]
        sensors = "{},{}".format( req['sensors'][req['sensors'].keys()[0]][0] , req['sensors'].keys()[0])
        format
        sitename = req['sitename']
        storage_base = '/var/kat/katstore'
        script_cmd = ["python" , self.script,
                      "--start-time={}".format(starttime),
                      "--end-time={}".format(endtime),
                      "--S={}".format(sensors),
                      "--site-name={}".format(sitename),
                      "--path={}".format(storage_base),
                      "--query={}".format(self.address)]

        yield self.call_process(script_cmd, self.stream, self.address)
  
    @coroutine
    def call_process(self, cmd, stream, address, io_loop=None): 
        """ Calls process 

        cmd: command in a list e.g ['ls', '-la']
        stdout_callback: callback to run on stdout


        TODO: add some way of calling proc.kill() if the stream is closed
        """

        stdout_stream = Subprocess.STREAM 
        stderr_stream = Subprocess.STREAM 
        proc = Subprocess(cmd, stdout=stdout_stream, stderr=stderr_stream)
        call_back = partial(self.on_exit, address)
        proc.set_exit_callback(call_back)

        pipe_stream = PipeIOStream(proc.stdout.fileno())

        try:
            while True:
                str_ = yield pipe_stream.read_bytes(102400, partial=True)
                yield stream.write(str_)
        except StreamClosedError:
            pass
        print("end address: {}".format(address))



    @coroutine
    def on_exit(self, a, address):
        print ("exit {} {}".format(a, address))





class MyProcessServer(TCPServer):

    """Docstring for MyProcessServer. """

    def __init__(self, script, io_loop=None, internal_metrics=None):
        super(MyProcessServer, self).__init__(io_loop)
        self.script = script
     
    @coroutine
    def handle_stream(self, stream, address):
        client_stream = ReadServerStreamHandler(stream, address, self.script, logger)
        yield client_stream.on_connect()

if __name__ == "__main__":
    options.define("script", help="script to read")
    options.define("logger", help="logger")


    options.parse_command_line()
    server = MyProcessServer(options.options.script)
    server.listen(8888)
    io_loop = IOLoop.current()
    io_loop.start()
