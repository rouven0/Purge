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
You can self-host this bot using any container-runtime of your liking. The provided `Dockerfile` can be used to build the image.
The following environment variables are required to be set before starting the app:
```env
DISCORD_CLIENT_ID
DISCORD_PUBLIC_KEY
DISCORD_BOT_TOKEN
```

### Registering commands
To register commands, simply run `python3 purge/__init__.py --deploy` after cloning the repo and installing all requirements (If you are on nix, this can be achieved via `nix develop`).
The following environment variables are required to be set before executing the command:
```env
DISCORD_CLIENT_ID
DISCORD_CLIENT_SECRET
```
