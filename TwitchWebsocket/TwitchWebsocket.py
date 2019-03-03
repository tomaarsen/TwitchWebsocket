
import socket, types, threading, time

from Message import Message

class TwitchWebsocket(threading.Thread):
    def __init__(self, host, port, callback, live = False):
        assert type(host) == str and type(port) == int and (type(callback) == types.FunctionType or type(callback) == types.MethodType)
        threading.Thread.__init__(self)
        self.name = "TwitchWebsocket"

        # Variables
        self.host = host
        self.port = port
        self.chan = str()
        self.nick = str()
        self.auth = str()
        self.capability = None
        self.callback = callback
        self.live = live

        self.data = str()

        # Lambda Functions.
        self.send_join = lambda message, command="JOIN ": self._send(command, message)
        self.send_pong = lambda message="", command="PONG ": self._send(command, message)
        self.send_ping = lambda message="", command="PING ": self._send(command, message)
        self.send_message = lambda message, command="PRIVMSG ": self._send("{}{} :".format(command, self.chan.lower()), message) if self.live else print(message)
        self.send_nick = lambda message, command="NICK ": self._send(command, message)
        self.send_pass = lambda message, command="PASS ": self._send(command, message)
        self.send_part = lambda message, command="PART ": self._send(command, message)
        self.send_req = lambda message, command="CAP REQ :twitch.tv/": self._send(command, message)

        # Seting up the initial socket connection.
        self._initialize_websocket()
        self.start()

    def run(self):
        while True:
            try:
                # Receive data from Twitch Websocket.
                packet = self.conn.recv(4096).decode('UTF-8')
                #if len(packet) == 0:
                #    print("It's 0")
                self.data += packet
                data_split = self.data.split("\r\n")
                self.data = data_split.pop()

                # Iterate over seperately sent data.
                for line in data_split:
                    m = Message(line)

                    # We will do some handling depending on the message ourself,
                    # so the developer doesn't have to.
                    if m.type == "PING":
                        self.send_pong()

                    self.callback(m)

            except OSError as e:
                print(f"[OSError: at {time.strftime('%X')}]: {e} -> {line}")
                self._initialize_websocket()
                if len(self.nick) > 0:
                    self.login(self.nick, self.auth)
                if len(self.chan) > 1:
                    self.join_channel(self.chan)
                if self.capability is not None:
                    self.add_capability(self.capability)

    def _send(self, command, message):
        # Send data back to Twitch.
        sent = self.conn.send(bytes("{}{}\r\n".format(command, message), 'UTF-8'))
        if sent == 0:
            raise RuntimeError("Socket connection broken, sent is 0")

    def _initialize_websocket(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # We set the timeout to 330 seconds, as the PING from the Twitch server indicating
        # That the connection is still live is sent roughly every 5 minutes it seems.
        # the extra 30 seconds prevents us from checking the connection when it's not 
        # needed.
        
        #TODO Error handle socket.gaierror: [Errno 11001] getaddrinfo failed and other errors
        self.conn.settimeout(330)
        
        self.conn.connect( (self.host, self.port) )

    def join_channel(self, chan):
        assert type(chan) == str and len(chan) > 0

        self.chan = chan if chan[0] == "#" else "#" + chan
        self.send_join(self.chan.lower())

    def leave(self):
        self.send_part(self.chan.lower())

    def login(self, nick, auth):
        assert type(nick) == type(auth) == str

        self.nick = nick
        self.auth = auth
        self.send_pass(self.auth)
        self.send_nick(self.nick.lower())

    def add_capability(self, capability):
        assert type(capability) in [list, str]

        self.capability = capability
        if type(capability) == list:
            for cap in capability:
                self.send_req(cap.lower())
        else:
            self.send_req(capability.lower())