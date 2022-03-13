# pylint: disable=unused-argument
import sys
from os import getenv
import logging
from time import time
from flask_discord_interactions.models.message import Message
import requests

from dotenv import load_dotenv
from flask_discord_interactions import DiscordInteractions


from flask import Flask
from flask_discord_interactions.models.option import CommandOptionType

import config

load_dotenv("./.env")

app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = getenv("DISCORD_CLIENT_ID", default="")
app.config["DISCORD_PUBLIC_KEY"] = getenv("DISCORD_PUBLIC_KEY", default="")
app.config["DISCORD_CLIENT_SECRET"] = getenv("DISCORD_CLIENT_SECRET", default="")
BOT_TOKEN = getenv("BOT_TOKEN", default="")

if "--debug" in sys.argv:
    app.config["DONT_VALIDATE_SIGNATURE"] = True

logger = logging.getLogger()
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(config.LOG_FORMAT))
logger.addHandler(console_handler)

base_url = "https://discord.com/api/v10/channels/"
headers = {"Authorization": f"Bot {BOT_TOKEN}", "user-agent": "Purgebot v2"}


@discord.command(
    options=[
        {
            "name": "amount",
            "description": "The amount of messages you want to delete (2-100).",
            "min_value": 2,
            "max_value": 100,
            "type": CommandOptionType.INTEGER,
            "required": True,
        }
    ]
)
def purge(ctx, amount: int):
    "Deletes up to 100 messages."
    if not ((ctx.author.permissions & (1 << 16)) and (ctx.author.permissions & (1 << 13))):
        return Message("You do not have the right permissions to perform this action.", ephemeral=True)
    minimum_time = int((time() - 14 * 24 * 60 * 60) * 1000.0 - 1420070400000) << 22
    messages_request = requests.get(
        url=base_url + str(ctx.channel_id) + "/messages?limit=" + str(amount), headers=headers
    )
    if messages_request.status_code == 403:
        return Message(
            content=(
                "Hey there, the bot is missing permissions to perform this action. Please make sure "
                "<@941041925216157746> has the permission to:\n - View this channel\n - Read message history."
            ),
            ephemeral=True,
        )
    messages_request.raise_for_status()
    messages_to_delete = []
    for record in messages_request.json():
        if int(record["id"]) > minimum_time:
            messages_to_delete.append(record["id"])
    if len(messages_to_delete) > 1:
        delete_request = requests.post(
            url=base_url + str(ctx.channel_id) + "/messages/bulk-delete",
            json={"messages": messages_to_delete},
            headers=headers,
        )
        if delete_request.status_code == 403:
            return Message(
                content=(
                    "Hey there, the bot is missing permissions to perform this action. Please make sure "
                    "<@941041925216157746> has the permission to manage messages."
                ),
                ephemeral=True,
            )
        delete_request.raise_for_status()

    return Message(f"Deleted {len(messages_to_delete)} messages.", ephemeral=True)


if "--update" in sys.argv:
    discord.update_commands(guild_id=830928381100556338)
    sys.exit()

if "--deploy" in sys.argv:
    discord.update_commands()
    sys.exit()


discord.set_route("/interactions")

if __name__ == "__main__":
    app.run(port=9100, debug=True)
