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
