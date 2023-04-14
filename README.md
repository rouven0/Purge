[![Black](https://img.shields.io/badge/codestyle-black-000000)](https://github.com/psf/black)
![Lines of code](https://img.shields.io/tokei/lines/github/therealr5/Purge)
[![Crowdin](https://badges.crowdin.net/purge/localized.svg)](https://crowdin.com/project/purge)
[![Discord Server](https://discord.com/api/v10/guilds/952508187905511484/widget.png)](https://discord.gg/4JT9JyjkAF)

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
You can self-host this bot using Nix. After importing the nixosModule from the flake you can simply enable the service using
```nix
{ config, ...}:
{
    services.purge.enable = true;
    services.purge.environmentFile = /path/to/your/file;
}
```

The environmentFile should contain the following variables:
```env
DISCORD_CLIENT_ID
DISCORD_PUBLIC_KEY
BOT_TOKEN
```

To expose the app to the internet, simply put an nginx reverse proxy in place.

```nix
{ config, ... }
{
    ...
    services.nginx.virtualHosts."purge.example.com" = {
        enableACME = true;
        forceSSL = true;
        locations."/" = {
            proxyPass = "http://127.0.0.1:${toString config.services.purge.listenPort}";
        };
    };
}
```

### Registering commands
To register commands, simply run `python3 app/bot.py --deploy` after cloning the repo and installing all [requirements](https://github.com/therealr5/Purge/blob/main/requirements.txt).
The following environment variables are required to be set before executing the command:
```env
DISCORD_CLIENT_ID
DISCORD_CLIENT_SECRET
```
