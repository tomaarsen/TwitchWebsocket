
import socket
import threading
import time
import logging
from typing import Callable, List, Optional, Union

from TwitchWebsocket.Message import Message

logger = logging.getLogger(__name__)


class TwitchWebsocket(threading.Thread):
    """
    TwitchWebsocket class used for connecting a Twitch account to a Twitch channel's chat,
    where it can read messages of many kinds, and post messages of its own.
    """

    def __init__(self,
                 host: str,
                 port: str,
                 chan: str,
                 nick: str,
                 auth: str,
                 callback: Callable[[Message], None],
                 capability: Optional[Union[List[str], str]] = None,
                 live: bool = True):
        """
        `host`: IRC Host, generally "irc.chat.twitch.tv".
        `port`: Socket port, generally `6667`.
        `chan`: Twitch channel of the chat to join, e.g. "#Tom" for www.twitch.tv/tom.
        `nick`: Twitch account name to use, e.g. "CubieB0T".
        `auth`: Twitch OAuth Token, e.g. "oauth:pivogip8ybletucqdz4pkhag6itbax".
        `callback`: The function or method that takes a `Message` object as parameter.
        `capability`: List of strings with extra information to be requested from Twitch. See docs.
        `live`: send_message() messages are posted in chat if True, otherwise only in the console.
        """
        assert isinstance(host, str)
        assert isinstance(port, int)
        assert callable(callback)
        threading.Thread.__init__(self)
        # Thread parameters
        self.name = "TwitchWebsocket"
        self._stop_event = threading.Event()
        self.daemon = True

        # Store passed variables
        self.host = host
        self.port = port
        self.chan = chan if chan[0] == "#" else "#" + chan
        self.nick = nick
        self.auth = auth
        self.capability = capability
        self.callback = callback
        self.live = live
        self.conn = None

    def start_nonblocking(self):
        """
        Start the bot in the background,
        I.e. more code can be run immediately in the main thread. (hence, non-blocking)
        """
        self.start()

    def start_blocking(self):
        """
        Start the bot in the foreground,
        I.e. the bot needs to terminate before the main thread can continue. (hence, blocking)
        """
        self.start_nonblocking()
        self.wait()

    def start_bot(self):
        """
        Deprecated version of `self.start_blocking()`.
        """
        self.start_blocking()

    def wait(self):
        """
        Wait for the bot to terminate, while allowing `KeyboardInterrupt' to terminate the program.
        """
        try:
            # Joining without a timeout will prevent the KeyboardInterrupt from triggering.
            while self.is_alive():
                self.join(1)
        except (KeyboardInterrupt, SystemExit) as e:
            # Stop the while loop in run()
            self.stop()
            # Cancel the self.conn.recv() in run()
            if self.conn is not None:
                self.conn.shutdown(socket.SHUT_WR)
            # Join this thread
            self.join()
            logger.info(f"{e.__class__.__name__} detected - shutting down.")

    def stop(self):
        """
        Set the event that indicates that the bot should stop.
        The bot will stop receiving messages after the next message.
        """
        self._stop_event.set()

    def stopped(self) -> bool:
        """
        Returns the status of the event that indicates if the bot should stop.
        True if `stop()` has been called. False otherwise.
        """
        return self._stop_event.is_set()

    def run(self):
        """
        First connect to Twitch using `connect()`, and then collect messages from Twitch
        indefinitely. `self.callback` is called with every message received.
        Automatically reconnects on timeout.
        """
        self.connect()
        # `data` will be continuously appended with received data
        data = ""
        while not self.stopped():
            try:
                # Receive data from Twitch Websocket.
                data += self.conn.recv(8192).decode('UTF-8')

            except UnicodeDecodeError:
                # In case of unexpected end of data.
                logger.warning(
                    "Received data could not be decoded. Skipping this data.")
                continue

            except OSError as error:
                logger.error(f"[OSError: {error}] - Attempting to reconnect.")
                self.connect()
                continue

            data_split = data.split("\r\n")
            data = data_split.pop()

            # Iterate over seperately sent data.
            for line in data_split:
                message = Message(line)

                # We will do some handling depending on the message ourself,
                # so the developer doesn't have to.
                if message.type == "PING":
                    self.send_pong()

                self.callback(message)

    def _send(self, command: str, message: str):
        """
        Send data to Twitch, with the `command` message command, and `message` as the content.
        In most cases, the public `send_...` methods should be used instead of this method,
        e.g. `self.send_message(message)` or `self.send_whisper(message, user)`
        """
        sent = self.conn.send(
            bytes("{}{}\r\n".format(command, message), 'UTF-8'))
        if sent == 0:
            raise RuntimeError("Socket connection broken, sent is 0")

    def send_join(self, channel: str) -> None:
        """
        Send JOIN request over IRC to connect to `channel` their Twitch chat.

        `channel` must be a string and nonempty. May be prepended with "#",
        and can have any casing , e.g. "#Tom" is equivalent to "tom".
        """
        self._send("JOIN ", channel)

    def send_part(self, channel: str) -> None:
        """
        Send PART request over IRC to disconnect from `channel` their Twitch chat.

        `channel` must be a string and nonempty. May be prepended with "#",
        and can have any casing , e.g. "#Tom" is equivalent to "tom".
        """
        self._send("PART ", channel)

    def send_pong(self) -> None:
        """
        Send PONG over IRC to Twitch.
        """
        self._send("PONG ", "")

    def send_ping(self) -> None:
        """
        Send PING over IRC to Twitch.
        """
        self._send("PING ", "")

    def send_message(self, message: str) -> None:
        """
        Send `message` in the connected Twitch Chat using the connected Twitch account,
        but only if `self.live` is True.
        If this boolean is False, simply print out `message`.
        """
        if self.live:
            self._send("PRIVMSG {} :".format(self.chan.lower()), message)
        else:
            print(message)

    def send_whisper(self, user: str, message: str):
        """
        Whisper `message` to `user` on Twitch using the connected Twitch account,
        but only if `self.live` is True.
        If this boolean is False, simply print out `/w user message`.
        """
        self.send_message(f"/w {user} {message}")

    def send_nick(self, nickname: str) -> None:
        """
        Send a NICK message to Twitch to identify the
        bot with the username/nickname `nickname`.
        """
        self._send("NICK ", nickname)

    def send_pass(self, authentication):
        """
        Send a PASS message to Twitch to authenticate the
        bot with the authentication `authentication`.
        """
        self._send("PASS ", authentication)

    def send_req(self, capability: str) -> None:
        """
        Send a CAP REQ request to add specific capability to access Twitch-specific
        commands, data, etc. See https://dev.twitch.tv/docs/irc/guide#twitch-irc-capabilities
        for more information.
        """
        self._send("CAP REQ ", ":twitch.tv/" + capability)

    def connect(self):
        """
        Connect to Twitch, Log in using the nickname and authentication, join
        the desired Twitch channel's chat, and optionally add capabilities for more
        data from Twitch.
        """
        self._initialize_websocket()
        self.login(self.nick, self.auth)
        self.join_channel(self.chan)
        if self.capability is not None:
            self.add_capability(self.capability)

    def _initialize_websocket(self):
        """
        Set up socket connection with Twitch, with a timeout of 330 seconds.
        After 330 seconds, the bot will timeout and automatically reconnect.
        """
        def get_reconnection_delay():
            """
            Yield exponential increase, starting with 0, 1, 2, 4, 8, 16, ...
            and ending at 512, which is repeated infinitely.
            """
            yield 0
            for val in (2**i for i in range(10)):  # Yields 1, 2, ..., 256, 512
                yield val
            while True:  # Yields 512, 512, 512, ...
                yield val

        reconnection_delay_gen = get_reconnection_delay()

        while True:
            try:
                logger.info("Attempting to initialize websocket connection.")
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # We set the timeout to 330 seconds, as the PING from the Twitch server indicating
                # That the connection is still live is sent roughly every 5 minutes it seems.
                # the extra 30 seconds prevents us from checking the connection when it's not
                # needed.
                self.conn.settimeout(330)

                self.conn.connect((self.host, self.port))
                logger.info("Websocket connection initialized.")
                # Only return if successful
                return

            except OSError:
                # Sleep and retry if not successful
                # reconnect_delay is 0, 1, 2, 4, 8, 16, ..., 512, 512, 512, ...
                reconnect_delay = next(reconnection_delay_gen)
                logger.error(
                    f"Failed to connect. Sleeping for {reconnect_delay} seconds and retrying...")
                time.sleep(reconnect_delay)

    def join_channel(self, channel: str) -> None:
        """
        Connect to the Twitch chat on the `channel` Twitch channel.
        Requires login using `self.login()`.

        `channel` must be a string and nonempty. May be prepended with "#",
        and can have any casing , e.g. "#Tom" is equivalent to "tom".
        """
        assert isinstance(channel, str) and channel

        self.send_join(channel.lower())

    def leave_channel(self, channel: str) -> None:
        """
        Disconnect from the Twitch chat on the `channel` Twitch channel.

        `channel` must be a string and nonempty. May be prepended with "#",
        and can have any casing , e.g. "#Tom" is equivalent to "tom".
        """
        self.send_part(channel.lower())

    def leave(self) -> None:
        """
        Deprecated version of `self.leave_channel(channel)`.
        """
        self.leave_channel(self.chan)

    def login(self, nickname: str, authentication: str) -> None:
        """
        Login using a nickname and corresponding authentication.
        `nickname` and `authentication` must be a non-empty string.
        """
        assert isinstance(nickname, str)
        assert isinstance(authentication, str)
        assert nickname and authentication

        self.send_pass(authentication)
        self.send_nick(nickname.lower())

    def add_capability(self, capability: Union[str, List[str]]) -> None:
        """
        Add a capability on Twitch, i.e. request more information from Twitch.
        `capability` must be a string or a list of strings. Currently, valid
        capabilities are "membership", "tags" and "commands".
        See https://dev.twitch.tv/docs/irc/guide#twitch-irc-capabilities for
        more information.
        """
        assert isinstance(capability, (list, str))

        if isinstance(capability, list):
            for cap in capability:
                self.add_capability(cap.lower())
        else:
            self.send_req(capability.lower())
