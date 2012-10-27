# -*- coding: utf-8 -*-
# Open Source Initiative OSI - The MIT License (MIT):Licensing
#
# The MIT License (MIT)
# Copyright (c) 2012 DotCloud Inc (opensource@dotcloud.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import zerorpc

REGISTRAR_ENDPOINT = "ipc:///tmp/stackio-service-registrar"

def require_session(fn):
    fn._require_session = True
    return fn

class ServiceConfig(object):
    def __init__(self, endpoint, options=None):
        self.endpoint = endpoint
        self.client = None
        self.introspected = None
        self.options = options

class StackIO(object):
    def __init__(self, **options):
        self.options = options

        registrar_client = zerorpc.Client(self.options)
        registrar_client.connect(self.options.get('registrar') or REGISTRAR_ENDPOINT)

        service_endpoints = registrar_client.services(True)

        self._services = dict([(name, ServiceConfig(config['endpoint'], config['options'])) for name, config in service_endpoints.iteritems()])

        registrar_client.close()

    def expose(self, service_name, context, endpoint=None):
        endpoint = endpoint or "ipc:///tmp/stackio-service-%s" % service_name
        require_session = []
        for element in dir(context):
            if element[0] == '_':
                continue
            if getattr(getattr(context, element), '_require_session', False):
                require_session.append(element)

        server = zerorpc.Server(context)
        server.bind(endpoint)

        registrar = self.use("registrar")
        registrar.register(service_name, endpoint, { 'requireSession': require_session })

        server.run()

    def services(self):
        return self._services.keys()

    def introspect(self, service_name):
        cached = self._services.get(service_name)

        if cached == None:
            raise Exception("Unknown service")
        elif cached.introspected != None:
            return cached.introspected
        else:
            client = self.use(service_name)
            cached.introspected = client._zerorpc_inspect()
            return cached.introspected

    def use(self, service_name):
        cached = self._services.get(service_name)

        if cached == None:
            raise Exception("Unknown service")
        elif cached.client != None:
            return cached.client
        else:
            cached.client = zerorpc.Client()
            cached.client.connect(cached.endpoint)
            return cached.client

