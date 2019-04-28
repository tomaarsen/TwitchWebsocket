# TwitchWebsocket
Python Wrapper for easily connecting to Twitch and setting up a chat bot.

---

# Input
This module will require the following information to be passed:

| **Type**       | **Explanation ** | **Example**                            | **Variable Name** | **Required?** |
| -------------- | ---------------- | ---------------------- | ----------------- | ------------- |
| Host           | The socket host | "irc.chat.twitch.tv"                   | host | Y |
| Port           | The socket port | 6667                                   | port | Y |
| Channel        | The channel to connect to | "#CubieDev"                            | chan | Y |
| Nickname       | The name of the bot | "CubieB0T"                             | nick | Y |
| Authentication | The authentication of the bot | "oauth:pivogip8ybletucqdz4pkhag6itbax" | auth | Y |
| Callback       | The function that gets called with all messages | Any function which receives one param  | callback | Y |
| Capability | List of extra information to be requested from Twitch. (See Twitch docs) | ["membership", "tags", "commands"] | capability | N |
| Live | Whether the outputs should actually be sent or only printed in the console | True | live | N |

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
        
        # Send along all required information, and the bot will start 
        # sending messages to your callback function. (self.message_handler in this case)
        self.ws = TwitchWebsocket(host=self.host, 
                                  port=self.port,
                                  chan=self.chan,
                                  nick=self.nick,
                                  auth=self.auth,
                                  callback=self.message_handler,
                                  capability=["membership", "tags", "commands"],
                                  live=True)
        # Any code after this will be executed after a KeyboardInterrupt

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
# My personal Twitch Bot Template
```python
from TwitchWebsocket import TwitchWebsocket
import json

class Settings:
    def __init__(self, bot):
        try:
            # Try to load the file using json.
            # And pass the data to the MyBot class instance if this succeeds.
            with open("settings.txt", "r") as f:
                settings = f.read()
                data = json.loads(settings)
                bot.set_settings(data['Host'],
                                data['Port'],
                                data['Channel'],
                                data['Nickname'],
                                data['Authentication'])
        except ValueError:
            raise ValueError("Error in settings file.")
        except FileNotFoundError:
            # If the file is missing, create a standardised settings.txt file
            # With all parameters required.
            with open('settings.txt', 'w') as f:
                standard_dict = {
                                    "Host": "irc.chat.twitch.tv",
                                    "Port": 6667,
                                    "Channel": "#<channel>",
                                    "Nickname": "<name>",
                                    "Authentication": "oauth:<auth>"
                                }
                f.write(json.dumps(standard_dict, indent=4, separators=(',', ': ')))
                raise ValueError("Please fix your settings.txt file that was just generated.")

class MyBot:
    def __init__(self):
        self.host = None
        self.port = None
        self.chan = None
        self.nick = None
        self.auth = None
        
        # Fill previously initialised variables with data from the settings.txt file
        Settings(self)

        self.ws = TwitchWebsocket(host=self.host, 
                                  port=self.port,
                                  chan=self.chan,
                                  nick=self.nick,
                                  auth=self.auth,
                                  callback=self.message_handler,
                                  capability=["membership", "tags", "commands"],
                                  live=False)

    def set_settings(self, host, port, chan, nick, auth):
        self.host = host
        self.port = port
        self.chan = chan
        self.nick = nick
        self.auth = auth

    def message_handler(self, m):
        if m.type == "PRIVMSG":
            pass

if __name__ == "__main__":
    MyBot()
```
---

# Example

Here's a list of some personal projects of mine implementing this library.
* [TwitchGoogleTranslate](https://github.com/CubieDev/TwitchGoogleTranslate)
* [TwitchMarkovChain](https://github.com/CubieDev/TwitchMarkovChain)
* [TwitchCubieBot](https://github.com/CubieDev/TwitchCubieBot)
* [TwitchDeathCounter](https://github.com/CubieDev/TwitchDeathCounter)
* [TwitchPickUser](https://github.com/CubieDev/TwitchPickUser)
* [TwitchSaveMessages](https://github.com/CubieDev/TwitchSaveMessages)
* [TwitchPackCounter](https://github.com/CubieDev/TwitchPackCounter) (Streamer specific bot)
* [TwitchDialCheck](https://github.com/CubieDev/TwitchDialCheck) (Streamer specific bot)

