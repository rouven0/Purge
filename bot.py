# pylint: disable=unused-argument
import sys
from os import getenv
import logging
from time import time
import re
import requests

from flask_discord_interactions import DiscordInteractions


from flask import Flask
from flask_discord_interactions.models.option import Option, CommandOptionType
from flask_discord_interactions.models.message import Message


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
console_handler.setFormatter(logging.Formatter("%(levelname)s [%(module)s.%(funcName)s]: %(message)s"))
logger.addHandler(console_handler)

base_url = "https://discord.com/api/v10/channels/"
headers = {"Authorization": f"Bot {BOT_TOKEN}", "user-agent": "Purgebot/1.0"}


@discord.command(
    default_member_permissions="73728",
    dm_permission=False,
    options=[
        Option(
            name="amount",
            description="The amount of messages you want to delete (1-100).",
            type=CommandOptionType.INTEGER,
            required=True,
            min_value=1,
            max_value=100,
        ),
        Option(
            name="until",
            description="[Message link or id] The last message to be deleted (if reached).",
            type=CommandOptionType.STRING,
        ),
    ],
)
def purge(ctx, amount: int, until: str = "0"):
    "Deletes up to 100 messages that are not older than 2 weeks."
    logging.info(
        "%s#%s used /purge in guild %s. amount: %s until: %s",
        ctx.author.username,
        ctx.author.discriminator,
        ctx.guild_id,
        amount,
        until,
    )
    m = re.match(r"https://discord.com/channels/\d*/\d*/(\d*)", until)
    if m:
        until = m.groups()[0]
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
        if record["id"] == until:
            break
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
    elif len(messages_to_delete) == 1:
        delete_request = requests.delete(
            url=base_url + str(ctx.channel_id) + "/messages/" + messages_to_delete[0],
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
