"""Global bot events and simple commands."""

import discord
from discord.ext import commands


class Events(commands.Cog):
    """Handles on_ready, command errors, and misc commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user} ({self.bot.user.id})")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                description=f"Please try again in {error.retry_after:.2f}s.",
                colour=discord.Colour.red(),
            )
            await ctx.send(embed=embed, ephemeral=True)
        else:
            raise error

    @commands.command(name="hello")
    async def hello(self, ctx: commands.Context):
        """Say hello."""
        await ctx.send("Hello!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
