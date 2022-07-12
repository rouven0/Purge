# pylint: disable=unused-argument
import logging
import re
import sys
from os import getenv
from time import time

import requests
from flask import Flask
from flask_discord_interactions import DiscordInteractions
from flask_discord_interactions.models.message import Message
from flask_discord_interactions.models.option import CommandOptionType, Option

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
            min_length=18,
            max_length=95,
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

    def has_permission_indicator(num: int) -> str:
        """
        Returns an indicator for the given permission
        """
        return "✅" if int(ctx.app_permissions) & (1 << num) else "🚫"

    if not all(
        [
            int(ctx.app_permissions) & (1 << 16),
            int(ctx.app_permissions) & (1 << 13),
            int(ctx.app_permissions) & (1 << 10),
        ]
    ):
        return Message(
            content=(
                "Hey there, <@941041925216157746> needs the following permissions in this channel in order to work. "
                "The indicators show whether you have already granted that permission or not.\n"
                f"{has_permission_indicator(10)} View this channel\n{has_permission_indicator(16)} "
                f"Read message history\n{has_permission_indicator(13)} Manage Messages"
            ),
            ephemeral=True,
        )
    m = re.match(r"https://discord.com/channels/\d*/\d*/(\d*)", until)
    if m:
        until = m.groups()[0]
    minimum_time = int((time() - 14 * 24 * 60 * 60) * 1000.0 - 1420070400000) << 22
    messages_request = requests.get(
        url=base_url + str(ctx.channel_id) + "/messages?limit=" + str(amount), headers=headers
    )
    messages_to_delete = []
    for record in messages_request.json():
        if int(record["id"]) > minimum_time:
            messages_to_delete.append(record["id"])
        if record["id"] == until:
            break
    if len(messages_to_delete) > 1:
        requests.post(
            url=base_url + str(ctx.channel_id) + "/messages/bulk-delete",
            json={"messages": messages_to_delete},
            headers=headers,
        ).raise_for_status()
    elif len(messages_to_delete) == 1:
        requests.delete(
            url=base_url + str(ctx.channel_id) + "/messages/" + messages_to_delete[0],
            headers=headers,
        ).raise_for_status()

    return Message(f"Deleted {len(messages_to_delete)} messages.", ephemeral=True)


if "--deploy" in sys.argv:
    discord.update_commands()
    sys.exit()


discord.set_route("/interactions")

if __name__ == "__main__":
    app.run(port=9100, debug=True)
