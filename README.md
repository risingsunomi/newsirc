# NEWSIRC

IRC bot for news via RSS. Watch out for ugly console output due to testing.

## Windows
To run this in the windows command prompt with foreign news sources, make sure to set utf-8 encoding via chcp 65001
see: https://ss64.com/nt/chcp.html

## Settings
Create a local.py file with the following attributes
```
NICKNAME = 'name'
CHANNELS = ['#channel1']
SERVER = 'irc.server.net'
PASSWORD = 'botidentpass'
RSSFEEDS = ['feedurl']
```

## Dev Log
### 02/13/2018
Currently, the bot connects to irc but doesn't fully work with responses for command and for sending RSS
news entries. Work is still needed but almost complete. RSS is able to be pulled with news stories and having a
constant connection to IRC works.

### 03/14/2018
Bot works with IRC and does printing of articles via timer that counts PING coming from the server (every third PING).
Doing tests of what to do when RSS list runs out. Logic should work in RSS.py/printArticle() but testing

### 03/19/2018
Logic for refreshing feed works in RSS.py/printArticle(), attribute was added to IRCClient.py to enable/disable bot
dialogue called 'talkBack' - you set it when the IRCClient is initialized. Identification when connected to server
not tested yet.
