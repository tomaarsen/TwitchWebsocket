# TwitchWebsocket
Python Wrapper for easily connecting to Twitch and setting up a chat bot.

---

# Input
This module will require the following information to be passed:

| **Type**       | **Example**                            |
| -------------- | -------------------------------------- |
| Host           | "irc.chat.twitch.tv"                   |
| Port           | 6667                                   |
| Channel        | "#CubieDev"                            |
| Nickname       | "CubieB0T"                             |
| Authentication | "oauth:pivogip8ybletucqdz4pkhag6itbax" |
| Callback       | Any function which receives one param  |

*Note that the example OAuth token is not an actual token, but merely a generated string to give an indication what it might look like.*

I got my real OAuth token from https://twitchapps.com/tmi/.

---

# Output
The callback function will be given back a Message object. This object has no methods and is merely parsed storage of the information given by Twitch. It has the following variables (assuming m is a Message object):

**Variable**    | **Type**  | **Example Data** |
--------------- | --------- | ---------------- |
 m.full_message | str       | @badges=broadcaster/1;color=#00FF7F;display-name=CubieDev;emotes=;flags=;id=3d623460-0bcb-4e65-9167-4b8d435e768d;mod=0;room-id=94714716;subscriber=0;tmi-sent-ts=1551617354820;turbo=0;user-id=94714716;user-type= :cubiedev!cubiedev@cubiedev.tmi.twitch.tv PRIVMSG #cubiedev :This is a test message for clarification purposes |
 m.tags         | dict      | {'badges': 'broadcaster/1', 'color': '#00FF7F', 'display-name': 'CubieDev', 'emotes': '', 'flags': '', 'id': '3d623460-0bcb-4e65-9167-4b8d435e768d', 'mod': '0', 'room-id': '94714716', 'subscriber': '0', 'tmi-sent-ts': '1551617354820', 'turbo': '0', 'user-id': '94714716', 'user-type': ''} |
 m.command      | str       | cubiedev!cubiedev@cubiedev.tmi.twitch.tv PRIVMSG #cubiedev |
 m.user         | str       | cubiedev |
 m.type         | str       | PRIVMSG |
 m.params       | str       | #cubiedev |
 m.channel      | str       | cubiedev |
 m.message      | str       | This is a test message for clarification purposes |

What these variables hold is shown here:

    # How messages are parsed, and what the Message class attributes represent:
    # @badges=subscriber/0;color=#00FF7F;display-name=CubieDev;emotes=;flags=;id=d315b88f-7813-467a-a1fc-418b00d4d5ee;mod=0;room-id=70624819;subscriber=1;tmi-sent-ts=1550060037421;turbo=0;user-id=94714716;user-type= :cubiedev!cubiedev@cubiedev.tmi.twitch.tv PRIVMSG #flackblag :Hello World!
    # |                                                                                                                                                                                                               |  |      |                                 |     | |        |  |          |
    # +---------------------------------------------------------------------------------------------------[ TAGS ]----------------------------------------------------------------------------------------------------+  [ USER ]                                 [TYPE ] [ PARAMS ]  [ MESSAGE  ]

    # |                                                                                                                                                                                                                 |                                                          |             |
    # |                                                                                                                                                                                                                 +-----------------------[ COMMAND ]------------------------+             |
    # |                                                                                                                                                                                                                                                                                          |
    # +-------------------------------------------------------------------------------------------------------------------------------------[ FULL_MESSAGE ]-------------------------------------------------------------------------------------------------------------------------------------+

Printing out the Message object also gives some information on what everything means:
```
full_message: @badges=broadcaster/1;color=#00FF7F;display-name=CubieDev;emotes=;flags=;id=3d623460-0bcb-4e65-9167-4b8d435e768d;mod=0;room-id=94714716;subscriber=0;tmi-sent-ts=1551617354820;turbo=0;user-id=94714716;user-type= :cubiedev!cubiedev@cubiedev.tmi.twitch.tv PRIVMSG #cubiedev :This is a test message for clarification purposes
        tags: {'badges': 'broadcaster/1', 'color': '#00FF7F', 'display-name': 'CubieDev', 'emotes': '', 'flags': '', 'id': '3d623460-0bcb-4e65-9167-4b8d435e768d', 'mod': '0', 'room-id': '94714716', 'subscriber': '0', 'tmi-sent-ts': '1551617354820', 'turbo': '0', 'user-id': '94714716', 'user-type': ''}
        command: cubiedev!cubiedev@cubiedev.tmi.twitch.tv PRIVMSG #cubiedev
                user: cubiedev
                type: PRIVMSG
                params: #cubiedev
        message: This is a test message for clarification purposes
```

---

# Usage:
```python
class MyBot:
    def __init__(self):
        self.host = "irc.chat.twitch.tv"
        self.port = 6667
        self.chan = "#<channel_name>"
        self.nick = "<user_name>"
        self.auth = "oauth:<authentication>"
        
        # Initialise using a host, port, callback and whether the bot is live (if it should send messages)
        # If live=False, then no chat messages will be sent, only printed out in the console.
        self.ws = TwitchWebsocket(self.host, self.port, self.message_handler, live=True)
        # Login using your nickname and authentication
        self.ws.login(self.nick, self.auth)
        # Join a channel
        self.ws.join_channel(self.chan)
        # Add a capability. See https://dev.twitch.tv/docs/irc/membership/ for capability documentation.
        self.ws.add_capability(["membership", "tags", "commands"])

    def message_handler(self, m):
        # Create your bot functionality here.
        pass

if __name__ == "__main__":
    MyBot()
```
| **Method with Parameters** | **Meaning** |
| -------------------------- | ----------- |
| ws = TwitchWebsocket(str host, str port, function message_handler, bool live) | message_handler is a function or method which will receive a Message object. If live is true, then any messages sent with ws.send_message() will appear in chat, otherwise they will just be printed out in the console. |
| ws.login(str nick, str auth) | Logs in to Twitch using the username and authentication |
| ws.join_channel(str channel) | Joins the channel |
| ws.add_capability(str capability) | Adds a single [capability](https://dev.twitch.tv/docs/irc/membership/). |
| ws.add_capability(list capabilities) | Adds all [capabilities](https://dev.twitch.tv/docs/irc/membership/) in the list. |
| ws.leave() | Leave a channel |
| ws.send_pong() | Send Pong. This is already done automatically upon receiving a Ping. |
| ws.send_ping() | Send a Ping. Can be useful for testing connectivity. |
| ws.send_message(str message) | Send message to Twitch Chat. | 
| ws.send_whisper(str sender, str message) | Whisper sender with message |

---

# Example

Here's a list of some personal projects of mine implementing this library.
* [TwitchGoogleTranslate](https://github.com/CubieDev/TwitchGoogleTranslate)
* [TwitchPickUser](https://github.com/CubieDev/TwitchPickUser)
* [TwitchPackCounter](https://github.com/CubieDev/TwitchPackCounter) (Streamer specific bot)
* [TwitchDialCheck](https://github.com/CubieDev/TwitchDialCheck) (Streamer specific bot)

