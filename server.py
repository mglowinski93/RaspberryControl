import asyncio
from protocol import from_binary, SetPin, Response
import RPi.GPIO as GPIO

pinsToControl = (12, 16, 18, 22, 32, 36, 40)

class EchoServerClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        message = from_binary(data)
        if isinstance(message, SetPin):#compare classes
            pin = message.pin
            state = message.state
            if pin in pinsToControl:
                GPIO.output(pin, GPIO.HIGH) if state else GPIO.output(pin, GPIO.LOW)
                response = Response(pin, state, True)
            else:
                response = Response(pin, state, False)

        print('Send to client: {!r}'.format(response.get_binary()))
        self.transport.write(response)
        self.transport.close()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
for pin in pinsToControl:
    GPIO.setup(pin, GPIO.OUT)

loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
coro = loop.create_server(EchoServerClientProtocol, '0.0.0.0', 8888)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()