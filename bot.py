#!/usr/bin/env python3
"""Bot Argon entrypoint.

Original template: Python-Discord-Bot-Template v6.6.0
(https://github.com/kkrypt0nn/Python-Discord-Bot-Template, Apache-2.0).
"""
import os

from dotenv import load_dotenv

from app.modules.discord_bot.infrastructure.gateway import build_bot

load_dotenv()

if __name__ == "__main__":
    build_bot().run(os.getenv("TOKEN"))

