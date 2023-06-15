# pylint: disable=unused-argument
import logging
import re
import sys
from os import getenv
from time import time
import pathlib

import i18n
import requests
from flask import Flask, send_file
from flask_discord_interactions import DiscordInteractions
from flask_discord_interactions.models.message import Message
from flask_discord_interactions.models.option import CommandOptionType, Option
from i18n import set as set_i18n
from i18n import t

import purge.config as config

i18n.set("filename_format", config.I18n.FILENAME_FORMAT)
i18n.set("fallback", config.I18n.FALLBACK)
i18n.set("available_locales", config.I18n.AVAILABLE_LOCALES)
i18n.set("skip_locale_root_data", True)

i18n.load_path.append(str(pathlib.Path(__file__).parent.resolve()) + "/locales")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.handlers.clear()
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(config.LOG_FORMAT))
logger.addHandler(console_handler)

# ugly thing I have to do to support nested locales
for locale in config.I18n.AVAILABLE_LOCALES:
    logging.info("Initialized locale %s", locale)
    i18n.t("ratelimited", locale=locale)

app = Flask(__name__)


@app.route("/robots.txt")
def get_robots():
    return send_file(f"{config.BASE_PATH}/robots.txt")


discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = getenv("DISCORD_CLIENT_ID", default="")
app.config["DISCORD_PUBLIC_KEY"] = getenv("DISCORD_PUBLIC_KEY", default="")
app.config["DISCORD_CLIENT_SECRET"] = getenv("DISCORD_CLIENT_SECRET", default="")
BOT_TOKEN = getenv("BOT_TOKEN", default="")

if "--debug" in sys.argv:
    app.config["DONT_VALIDATE_SIGNATURE"] = True


headers = {"Authorization": f"Bot {BOT_TOKEN}", "user-agent": "Purgebot/1.0 (+https://github.com/therealr5/Purge)"}


def get_localizations(key: str) -> dict:
    """
    Returns all localizations for a string
    """
    localizations = {}
    for locale in i18n.get("available_locales"):
        localizations[locale] = i18n.t(key, locale=locale)
    return localizations


@discord.command(
    default_member_permissions="74752",
    name_localizations=get_localizations("commands.purge.name"),
    description_localizations=get_localizations("commands.purge.description"),
    dm_permission=False,
    options=[
        Option(
            name="amount",
            name_localizations=get_localizations("commands.purge.amount.name"),
            description="The amount of messages you want to delete (1-100).",
            description_localizations=get_localizations("commands.purge.amount.description"),
            type=CommandOptionType.INTEGER,
            required=True,
            min_value=1,
            max_value=100,
        ),
        Option(
            name="until",
            name_localizations=get_localizations("commands.purge.until.name"),
            description="[Message link or id] The last message to be deleted (if reached).",
            description_localizations=get_localizations("commands.purge.until.description"),
            type=CommandOptionType.STRING,
            min_length=19,
            max_length=95,
        ),
    ],
)
def purge(ctx, amount: int, until: str = "0"):
    "Deletes up to 100 messages that are not older than 2 weeks."
    set_i18n("locale", ctx.locale)
    logging.debug(
        "%s#%s used /purge. amount: %s until: %s using locale %s",
        ctx.author.username,
        ctx.author.discriminator,
        amount,
        until,
        ctx.locale,
    )
    permissions = {10: "view_channel", 13: "manage_messages", 16: "read_message_history"}

    def has_permission_indicator(num: int) -> str:
        """
        Returns an indicator for the given permission
        """
        return ("✅ " if int(ctx.app_permissions) & (1 << num) else "🚫 ") + t(f"permissions.{permissions[num]}")

    if not all([int(ctx.app_permissions) & (1 << n) for n in permissions.keys()]):
        return Message(
            content=(
                t("permissions.message") + "\n" + "\n".join([has_permission_indicator(n) for n in permissions.keys()])
            ),
            ephemeral=True,
        )
    m = re.match(r"https://discord.com/channels/\d*/\d*/(\d*)", until)
    if m:
        until = m.groups()[0]
    minimum_time = int((time() - 14 * 24 * 60 * 60) * 1000.0 - 1420070400000) << 22
    messages_request = requests.get(
        url=config.BASE_URL + str(ctx.channel_id) + "/messages?limit=" + str(amount), headers=headers
    )
    messages_to_delete = []
    for record in messages_request.json():
        if int(record["id"]) > minimum_time:
            messages_to_delete.append(record["id"])
        if record["id"] == until:
            break
    if len(messages_to_delete) > 0:
        if len(messages_to_delete) > 1:
            delete_request = requests.post(
                url=config.BASE_URL + str(ctx.channel_id) + "/messages/bulk-delete",
                json={"messages": messages_to_delete},
                headers=headers,
            )
        else:
            delete_request = requests.delete(
                url=config.BASE_URL + str(ctx.channel_id) + "/messages/" + messages_to_delete[0],
                headers=headers,
            )
        if delete_request.status_code == 429:
            logging.warn("Ran into a ratelimit at %s", delete_request.request.url)
            return Message(t("ratelimited"), ephemeral=True)
        else:
            delete_request.raise_for_status()

    return Message(t("success", count=len(messages_to_delete)), ephemeral=True)


if "--deploy" in sys.argv:
    discord.update_commands()
    sys.exit()


discord.set_route("/interactions")

if __name__ == "__main__":
    app.run(port=9100, debug=True)
