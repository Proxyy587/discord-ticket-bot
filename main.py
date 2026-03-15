"""Cypro Discord bot entry point."""

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True


class CyproBot(commands.Bot):
    async def setup_hook(self):
        """Load all cogs before the bot connects."""
        for filename in os.listdir("cogs"):
            if filename.endswith(".py") and not filename.startswith("_"):
                await self.load_extension(f"cogs.{filename[:-3]}")


bot = CyproBot(command_prefix="$", intents=intents)


def main():
    bot.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    main()
