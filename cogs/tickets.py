"""Ticket system: modals, views, and send command."""

import asyncio
import io
from datetime import datetime

import discord
from discord import ui
from discord.ext import commands
from discord.utils import get

import config
from constants import (
    Emojis,
    GUILD_ID,
    ICON_URL,
    LOG_CHANNEL_ID,
    TICKET_CATEGORY_NAME,
    TICKET_IMAGE_URL,
    TOS_URL,
)


def _avatar_url(user: discord.User) -> str:
    return user.avatar.url if user.avatar else user.default_avatar.url


# --- Modals ---


class SupportModal(ui.Modal, title="Support Ticket"):
    subject = ui.TextInput(
        label="Subject",
        placeholder="Type your Subject of opening Support Ticket",
        style=discord.TextStyle.short,
    )
    description = ui.TextInput(
        label="Description:",
        placeholder="Write about your Description Of your Problem",
        style=discord.TextStyle.paragraph,
    )

    def __init__(self, bot: commands.Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        ticket_category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)
        user = interaction.user

        embed = discord.Embed(
            title=f"{Emojis.CY_USER} New Support",
            description=(
                f"{Emojis.B7_BULLET}**Title:**\n{Emojis.B7_VALUE}{self.subject.value}\n\n"
                f"{Emojis.B7_BULLET}**Description:**\n> {self.description.value}"
            ),
            color=discord.Color.green(),
            timestamp=datetime.utcnow(),
        )
        embed.set_thumbnail(url=_avatar_url(user))

        ticket_channel = await guild.create_text_channel(
            f"❓〢{interaction.user.name.lower()}", category=ticket_category
        )
        await ticket_channel.set_permissions(
            guild.default_role, view_channel=False, read_messages=False, send_messages=False
        )
        await ticket_channel.set_permissions(
            interaction.user, read_messages=True, send_messages=True
        )

        await interaction.response.send_message(
            embed=discord.Embed(
                description=f"**Your Ticket was created in** {ticket_channel.mention}",
                color=discord.Color.green(),
            ),
            ephemeral=True,
        )

        msg = await ticket_channel.send(
            content=interaction.user.mention,
            embed=embed,
            view=TicketView(self.bot, ticket_channel),
        )
        await msg.pin()

        await ticket_channel.send(
            embed=discord.Embed(
                title=f"{Emojis.CHECK} Commission Successful",
                description="Please wait for our freelancer to respond",
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )
        )


class OrderModal(ui.Modal, title="Placing Order"):
    service_type = ui.TextInput(
        label="Service Type: (for eg- Web Development)",
        placeholder="Bot Development, Web Development, Web Design etc",
        style=discord.TextStyle.short,
    )
    short_title = ui.TextInput(
        label="Project Short title",
        placeholder="Say us what you want in short",
        style=discord.TextStyle.short,
    )
    long_desc = ui.TextInput(
        label="Long Description of the Project",
        placeholder="Write about your Project in Details",
        style=discord.TextStyle.paragraph,
    )
    budget = ui.TextInput(
        label="Budget: (In USD)",
        placeholder="Give us rough idea about your Pricings",
        style=discord.TextStyle.short,
    )
    deadline = ui.TextInput(
        label="Deadline",
        placeholder="Deadline of your Project",
        style=discord.TextStyle.short,
    )

    def __init__(self, bot: commands.Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        ticket_category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)
        user = interaction.user

        embed = discord.Embed(
            title=f"{Emojis.CY_USER} New Commission",
            description=(
                f"{Emojis.B7_BULLET}**Service Type:**\n{Emojis.B7_VALUE}{self.service_type.value}\n\n"
                f"{Emojis.B7_BULLET}**Project Title:**\n{Emojis.B7_VALUE}{self.short_title.value}\n\n"
                f"{Emojis.B7_BULLET}**Description:**\n> {self.long_desc.value}\n\n"
            ),
            color=discord.Color.green(),
            timestamp=datetime.utcnow(),
        )
        embed.add_field(
            name=f"{Emojis.B7_BULLET} Budget",
            value=f"{Emojis.B7_VALUE} {self.budget.value}",
            inline=True,
        )
        embed.add_field(
            name=f"{Emojis.B7_BULLET} Deadline",
            value=f"{Emojis.B7_VALUE} {self.deadline.value}",
            inline=True,
        )
        embed.add_field(
            name=f"{Emojis.B7_BULLET} User:",
            value=f"{Emojis.B7_VALUE} {interaction.user.mention}",
            inline=True,
        )
        embed.set_thumbnail(url=_avatar_url(user))

        ticket_channel = await guild.create_text_channel(
            f"🎫〢{interaction.user.name.lower()}", category=ticket_category
        )
        await ticket_channel.set_permissions(
            guild.default_role, view_channel=False, read_messages=False, send_messages=False
        )
        await ticket_channel.set_permissions(
            interaction.user, read_messages=True, send_messages=True
        )

        await interaction.response.send_message(
            embed=discord.Embed(
                description=f"**Your Ticket was created in** {ticket_channel.mention}",
                color=discord.Color.green(),
            ),
            ephemeral=True,
        )

        msg = await ticket_channel.send(
            content=interaction.user.mention,
            embed=embed,
            view=TicketView(self.bot, ticket_channel),
        )
        await msg.pin()

        await ticket_channel.send(
            embed=discord.Embed(
                title=f"{Emojis.CHECK} Commission Successful",
                description="Please wait for our freelancer to respond",
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )
        )


# --- Ticket view (Close / Claim) ---


class TicketView(discord.ui.View):
    def __init__(self, bot: commands.Bot, ticket_channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.bot = bot
        self.ticket_channel = ticket_channel

    @ui.button(label="Close", emoji="🔒", custom_id="ticket:close")
    async def close_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{Emojis.ALERT} No Permission",
                    description=(
                        "You can't delete this ticket. If you accidentally created this "
                        "ticket please ping our staff members to pursue your request."
                    ),
                ),
                ephemeral=True,
            )
            return

        await interaction.response.defer()
        await interaction.channel.send(
            embed=discord.Embed(description=f"{Emojis.ALERT} Please wait.....")
        )
        await asyncio.sleep(5)
        await interaction.channel.send(
            embed=discord.Embed(description=f"{Emojis.ALERT} Closing ticket...")
        )

        messages = []
        async for message in self.ticket_channel.history():
            messages.append(message)

        transcript = ""
        for message in reversed(messages):
            author_name = message.author.name
            author_avatar = _avatar_url(message.author)
            message_content = message.content
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            transcript += (
                f'<div class="message">'
                f'<img src="{author_avatar}" alt="{author_name}"/>'
                f'<span class="author">{author_name}</span>'
                f'<span class="timestamp">{timestamp}</span>'
                f'<div class="content">{message_content}</div></div>'
            )

        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            transcript_html = (
                f"<!DOCTYPE html><html><head><meta charset=\"UTF-8\">"
                f"<style>{config.CSS}</style></head><body>"
                f"<div class=\"messages\">{transcript}</div></body></html>"
            )
            with io.StringIO(transcript_html) as f:
                await log_channel.send(
                    file=discord.File(f, filename="transcript.html")
                )

        await interaction.channel.delete()

    @ui.button(label="Claim", emoji=Emojis.CY_ROCKET, custom_id="ticket:claim")
    async def claim(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        freelancer_role = discord.utils.get(
            interaction.guild.roles, name="Freelancer"
        )
        if freelancer_role in interaction.user.roles:
            await interaction.response.send_message(
                f"{interaction.user.mention} feature coming soon", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "feature coming soon.", ephemeral=True
            )


# --- Persistent ticket panel view ---


class TicketPanelView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.cooldown = commands.CooldownMapping.from_cooldown(
            1, 7200, commands.BucketType.user
        )
        self.add_item(
            discord.ui.Button(
                label="Terms of Service",
                url=TOS_URL,
                emoji=Emojis.CY_BOOK,
            )
        )

    @ui.button(
        label="Order",
        style=discord.ButtonStyle.gray,
        emoji=Emojis.CY_CART,
        custom_id="persistent_view:ticket",
    )
    async def order(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        guild = self.bot.get_guild(GUILD_ID)
        ticket_category = discord.utils.get(
            guild.categories, name=TICKET_CATEGORY_NAME
        )
        existing = get(
            ticket_category.channels,
            name=f"🎫〢{interaction.user.name.lower()}",
        )
        if existing:
            await interaction.response.send_message(
                "You already have a ticket open. Please wait for a Staff to "
                "respond before creating a new ticket.",
                ephemeral=True,
            )
            return
        await interaction.response.send_modal(OrderModal(self.bot))

    @ui.button(
        label="Support",
        style=discord.ButtonStyle.gray,
        emoji=Emojis.CY_USER,
        custom_id="persistent_view:support",
    )
    async def support(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        guild = self.bot.get_guild(GUILD_ID)
        ticket_category = discord.utils.get(
            guild.categories, name=TICKET_CATEGORY_NAME
        )
        existing = get(
            ticket_category.channels,
            name=f"❓〢{interaction.user.name.lower()}",
        )
        if existing:
            await interaction.response.send_message(
                "You already have a ticket open. Please wait for a Staff to "
                "respond before creating a new ticket.",
                ephemeral=True,
            )
            return
        await interaction.response.send_modal(SupportModal(self.bot))


# --- Cog ---


class Tickets(commands.Cog):
    """Ticket counter and order/support flows."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="send")
    @commands.has_permissions(administrator=True)
    async def send_ticket_panel(self, ctx: commands.Context):
        """Post the ticket counter embed with Order/Support buttons."""
        embed = discord.Embed(
            title=f"{Emojis.CY_TICKET} Ticket Counter!",
            description=(
                f"{Emojis.CY_CART}**__Making a Purchase__**\n"
                f"> {Emojis.B7_BULLET} If you would like to **purchase** any sort of *service or items*. "
                f"`kindly react` with {Emojis.CY_CART}\n\n"
                f"{Emojis.CY_USER}**__Help or Support__**\n"
                f"> {Emojis.B7_BULLET} If you require any help related to our service or need any "
                f"*fixes or Refunds* `please React` with {Emojis.CY_USER}\n\n"
                f"{Emojis.CY_BOOK}**__Terms Of Service__**\n"
                f"> {Emojis.B7_BULLET} Kindly go through the Terms of our Service before `making any "
                f"purchase`. We won't be responsible for any confusion caused {Emojis.CY_BOOK}\n\n"
                f"**__ACCEPTED PAYMENT__**\n"
                f"> {Emojis.PAYPAL} {Emojis.CASHAPP} {Emojis.CRYPTO} {Emojis.BANK} {Emojis.UPI}"
            ),
            color=discord.Color.red(),
        )
        embed.set_footer(text="Cypro Freelance", icon_url=ICON_URL)
        embed.set_image(url=TICKET_IMAGE_URL)
        embed.set_thumbnail(url=ICON_URL)

        await ctx.send(embed=embed, view=TicketPanelView(self.bot))


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
