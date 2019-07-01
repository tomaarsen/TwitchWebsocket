

class Message:
    # How messages are parsed, and what the Message class attributes represent:
    # @badges=subscriber/0;color=#00FF7F;display-name=CubieDev;emotes=;flags=;id=d315b88f-7813-467a-a1fc-418b00d4d5ee;mod=0;room-id=70624819;subscriber=1;tmi-sent-ts=1550060037421;turbo=0;user-id=94714716;user-type= :cubiedev!cubiedev@cubiedev.tmi.twitch.tv PRIVMSG #flackblag :Hello World!
    # |                                                                                                                                                                                                               |  |      |                                 |     | |        |  |          |
    # +---------------------------------------------------------------------------------------------------[ TAGS ]----------------------------------------------------------------------------------------------------+  [ USER ]                                 [TYPE ] [ PARAMS ]  [ MESSAGE  ]

    # |                                                                                                                                                                                                                 |                                                          |             |
    # |                                                                                                                                                                                                                 +-----------------------[ COMMAND ]------------------------+             |
    # |                                                                                                                                                                                                                                                                                          |
    # +-------------------------------------------------------------------------------------------------------------------------------------[ FULL_MESSAGE ]-------------------------------------------------------------------------------------------------------------------------------------+

    def __init__(self, raw_data):
        split = [d for d in raw_data.split(" :") if len(d) > 0]

        # These parameters will be filled based onthe raw_data given
        self.full_message = raw_data
        self.tags = {}
        self.command = None
        self.user = None
        self.type = None
        self.params = None
        self.channel = None
        self.message = None

        if split[0][0] == "@":
            self.parse_tags(split)

        # Get full command as it is sent to us
        # We remove the : that may be left over if the
        # split on " :" didn't remove it.
        self.command = split.pop(0).replace(":", "")

        # For some reason PING messages have a different format than the rest
        # of the messages Twitch sends us.
        # We will handle this message differently for this reason
        if self.command.startswith(("PING", "PONG")):
            self.type = self.command[:4]
            return

        # Parse command into smaller bits
        # :<user>!<user>@<user>.tmi.twitch.tv <type> <params>, or
        # :<user>.tmi.twitch.tv <type> <params>, or
        # :tmi.twitch.tv <type> <params>, or
        # :jtv MODE #<channel> <params>

        # Note, we chose to send these values as parameters to indicate dependencies
        self.parse_user(self.command)
        self.parse_type(self.command)
        self.parse_params(self.command, self.type)
        self.parse_channel(self.params)

        self.parse_message(split)

    def parse_tags(self, split):
        # Get data in format @key=data; ... key=data;
        # and transform to usable dictionary type under self.tags:
        for fact in split.pop(0)[1:].split(";"):
            key, data = fact.split("=")
            self.tags[key] = data if len(data) > 0 else ""
            #TODO Consider "" vs None

    def parse_user(self, command):
        # Get data before tmi.twitch.tv, then get data before !
        # Note that not all commands have a user specified
        if not command.startswith(("jtv ", "tmi.twitch.tv ")):
            self.user = command.split("tmi.twitch.tv")[0].split("!")[0]

    def parse_type(self, command):
        # Commands types are the first word after tmi.twitch.tv,
        # with only one exception: CAP * ACK, which consists of multiple words.
        self.type = command.split(" ")[1] if "CAP * ACK" not in command else "CAP * ACK"

    def parse_params(self, command, type):
        # Get all the remaining parameters used in the command.
        # For example the channel you are attempting to join, or the user that is being modded.
        # We use the index of self.type to get everything listed after the type.
        params = command[command.index(type) + len(type) + 1:]
        self.params = params if len(params) > 0 else ""
        #TODO Consider None vs ""

    def parse_channel(self, params):
        # We will look through self.params to find if one of the parameters is a channel.
        if self.params != None:
            chan_index = self.get_index(params, "#")
            if chan_index != None:
                self.channel = params[chan_index + 1: self.get_index(params, " ", chan_index)]

    def get_index(self, string, substring, start=0):
        try:
            return string.index(substring, start)
        except ValueError:
            return None

    def parse_message(self, split):
        #TODO Consider None vs ""

        # Not everything we get sent has a message attached to it. If there is no message, we use ""
        if len(split) > 0:
            # If the message itself contains " :", then "split" will have be a list of multiple items. We will join them again.
            message = " :".join(split)
            # If someone used /me, it reaches us as ╔ACTION: /me This is a test -> ╔ACTION This is a test╔ 
            # In most cases we just want /me however, so I'll replace it.
            # Note that the first and last character have id 1
            if ord(message[0]) == 1 and message[1:7] == "ACTION":
                # Replace ╔ACTION with /me, and remove the last ╔
                message = "/me" + message[7:-1]
            self.message = message
        else:
            self.message = ""

    def __str__(self):
        return (f"full_message: {self.full_message}\n\t" +
            f"tags: {self.tags}\n\t" +
            f"command: {self.command}\n\t\t" +
                f"user: {self.user}\n\t\t" +
                f"type: {self.type}\n\t\t" +
                f"params: {self.params}\n\t\t" +
                f"channel: {self.channel}\n\t" +
            f"message: {self.message}\n")
