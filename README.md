# NEWSIRC

IRC bot for news via RSS.

Currently working on finding the right scraping library as the current one seems to fail. Will work on custom scraping.

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
```

## Log
### 02/13/2018
Currently, the bot connects to irc but doesn't fully work with responses for command and for sending RSS
news entries. Work is still needed but almost complete. RSS is able to be pulled with news stories and having a
constant connection to IRC works. 
