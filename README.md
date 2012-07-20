# Stack.io Python Client #

Stack.io is a distributed communication framework for web apps and server-side
processes. This is the python client for
[stack.io](https://github.com/ysimonson/stack.io).

To use, first install stack.io:

    pip install stack.io

Then import the module and instantiate a new client:

    client = stackio.StackIO()

From there, you can start using a service, e.g.:

    test = client.use("test-service")
    print test.say_hello("World")

The python client can also expose services, e.g.:

    class TestService(object):
        def say_hello(name):
            return "Hello, %s!" % name

    client.expose("test-service", "tcp://127.0.0.1:4242", TestService())

This will expose the service `test-service` at the endpoint
`tcp://127.0.0.1:4242`.

All client methods:
 * `expose(service_name, endpoint, context)` - Exposes a new stack.io service,
   where `service_name` is the name of the service, `endpoint` is the ZeroMQ
   endpoint to expose to, and `context` is the object to expose.
 * `use(service_name)` - Prepares a service to be used, returning back an
   object that you can make RPC calls against. `service_name` is the name of a
   service.
 * `services()` - Returns a list of services available.
 * `introspect(service_name)` - Introspects on the methods available
   for the given `service_name`.
