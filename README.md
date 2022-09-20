[![Deployment](https://github.com/therealr5/Purge/actions/workflows/deploy.yml/badge.svg)](https://github.com/therealr5/Purge/actions/workflows/deploy.yml)
[![Image size](https://img.shields.io/docker/image-size/therealr5/purge/latest)](https://hub.docker.com/r/therealr5/purge)
[![Black](https://img.shields.io/badge/codestyle-black-000000)](https://github.com/psf/black)
![Lines of code](https://img.shields.io/tokei/lines/github/therealr5/Purge)
[![Crowdin](https://badges.crowdin.net/purge/localized.svg)](https://crowdin.com/project/purge)

[![Discord](https://discord.com/api/v10/guilds/952508187905511484/widget.png)](https://discord.gg/4JT9JyjkAF)

# Purge
Minimalistic purge bot for Discord

## Project description

### Motivation
The bulk delete functionality is one of the very few things that are only available for bots. This project aims to bring that functionality to the Discord end user.

### Usage
This bot has only one command: `/purge` -  which lets you delete up to 100 messages at once.
Please keep in mind that due to discord limits, the messages may not be older than 2 weeks.


## Self-host this bot
### Running the server
Simply self host this bot using docker. The internal server will be running on port 9100. The following environment variables are required for the bot to work:
```env
DISCORD_CLIENT_ID
DISCORD_PUBLIC_KEY
BOT_TOKEN
```` 

### Registering commands
To register commands, simply run `python3 app/bot.py --deploy` after cloning the repo and installing all [requirements](https://github.com/therealr5/Purge/blob/main/requirements.txt).
The following environment variables are required to be set before executing the command:
```env
DISCORD_CLIENT_ID
DISCORD_CLIENT_SECRET
```
