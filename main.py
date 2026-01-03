
import discord
from discord.ext import commands
from discord import ui
import datetime
import io
import asyncio
import config as c
from discord.utils import get
import os 
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- EVENTS ---

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(description=f'Please try again in {error.retry_after:.2f}s.', colour=discord.Colour.red())
        await ctx.send(embed=embed, ephemeral=True)
    else:
        raise error

# --- MODALS ---

class Support(ui.Modal, title="Support Ticket"):
    subject = ui.TextInput(label="Subject", placeholder="Type your Subject of opening Support Ticket", style=discord.TextStyle.short)
    description = ui.TextInput(label="Description:", placeholder="Write about your Description Of your Problem", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        guild = bot.get_guild(c.guild)
        ticket_category = discord.utils.get(
        guild.categories, name="━━━| 🎫 TICKETS |━━━")
        user = interaction.user
        user_avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
        embed = discord.Embed(
            title=f"<:CY_user:1089898348519112735> New Support",
            description=f"<:B7:1089799856618475591>**Title:**\n<:B7:1089799798216986634>{self.subject.value}\n\n<:B7:1089799856618475591>**Description:**\n> {self.description.value}",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=user_avatar_url)

        ticket_channel = await guild.create_text_channel(f"❓〢{interaction.user.name.lower()}", category=ticket_category)
        await ticket_channel.set_permissions(guild.default_role, view_channel=False, read_messages=False, send_messages=False)
        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        em = discord.Embed(
            description=f"**Your Ticket was created in** {ticket_channel.mention}", color=discord.Color.green())
        await interaction.response.send_message(embed=em, ephemeral=True)
        damn = await ticket_channel.send(content=interaction.user.mention, embed=embed, view=TicketView(ticket_channel))
        await damn.pin()
        com = discord.Embed(title="<:CHECK_CHECK_2:1089800076370653184> Commission Successful",
                            description="Please wait for our freelancer to respond", color=discord.Color.green(), timestamp=datetime.datetime.utcnow())
        await ticket_channel.send(embed=com)

class MyModal(ui.Modal, title="Placing Order"):
    service_type = ui.TextInput(label="Service Type: (for eg- Web Development)",
                      placeholder="Bot Development, Web Development, Web Design etc", style=discord.TextStyle.short)
    short_title = ui.TextInput(label="Project Short title",
                      placeholder="Say us what you want in short", style=discord.TextStyle.short)
    long_desc = ui.TextInput(label="Long Description of the Project",
                      placeholder="Write about your Project in Details", style=discord.TextStyle.paragraph)
    budget = ui.TextInput(label="Budget: (In USD)",
                      placeholder="Give us rough idea about your Pricings", style=discord.TextStyle.short)
    deadline = ui.TextInput(label="Deadline", placeholder="Deadline of your Project",
                      style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        guild = bot.get_guild(c.guild)
        ticket_category = discord.utils.get(guild.categories, name="━━━| 🎫 TICKETS |━━━")
        user = interaction.user
        user_avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
        embed = discord.Embed(
            title=f"<:CY_user:1089898348519112735> New Commission",
            description=f"<:B7:1089799856618475591>**Service Type:**\n<:B7:1089799798216986634>{self.service_type.value}\n\n<:B7:1089799856618475591>**Project Title:**\n<:B7:1089799798216986634>{self.short_title.value}\n\n<:B7:1089799856618475591>**Description:**\n> {self.long_desc.value}\n\n",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="<:B7:1089799856618475591> Budget", value=f"<:B7:1089799798216986634> {self.budget.value}", inline=True)
        embed.add_field(name="<:B7:1089799856618475591> Deadline", value=f"<:B7:1089799798216986634> {self.deadline.value}", inline=True)
        embed.add_field(name="<:B7:1089799856618475591> User:", value=f"<:B7:1089799798216986634> {interaction.user.mention}", inline=True)
        embed.set_thumbnail(url=user_avatar_url)

        ticket_channel = await guild.create_text_channel(f"🎫〢{interaction.user.name.lower()}", category=ticket_category)
        await ticket_channel.set_permissions(guild.default_role, view_channel=False, read_messages=False, send_messages=False)
        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        em = discord.Embed(
            description=f"**Your Ticket was created in** {ticket_channel.mention}", color=discord.Color.green())
        await interaction.response.send_message(embed=em, ephemeral=True)
        damn = await ticket_channel.send(content=interaction.user.mention, embed=embed, view=TicketView(ticket_channel))
        await damn.pin()
        com = discord.Embed(title="<:CHECK_CHECK_2:1089800076370653184> Commission Successful",
                            description="Please wait for our freelancer to respond", color=discord.Color.green(), timestamp=datetime.datetime.utcnow())
        await ticket_channel.send(embed=com)

# --- TICKET VIEW ---

class TicketView(discord.ui.View):
    def __init__(self, ticket_channel):
        super().__init__(timeout=None)
        self.ticket_channel = ticket_channel

    @ui.button(label="Close", emoji="🔒", custom_id="ticket:close")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_permissions = interaction.user.guild_permissions
        if user_permissions.administrator:
            await interaction.response.defer()
            em = discord.Embed(description="<:ALERT_1:1089800062575591454>Please wait.....")
            await interaction.channel.send(embed=em)
            await asyncio.sleep(5)
            emd = discord.Embed(description="<:ALERT_1:1089800062575591454> Closing ticket...")
            await interaction.channel.send(embed=emd)

            messages = []
            async for message in self.ticket_channel.history():
                messages.append(message)

            transcript = ""
            for message in reversed(messages):
                author_name = message.author.name
                author_avatar = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url
                message_content = message.content
                timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                transcript += f'<div class="message"><img src="{author_avatar}" alt="{author_name}"/><span class="author">{author_name}</span><span class="timestamp">{timestamp}</span><div class="content">{message_content}</div></div>'

            log_channel = bot.get_channel(1076174920360402984)
            if log_channel:
                transcript_html = f'<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{c.CSS}</style></head><body><div class="messages">{transcript}</div></body></html>'
                with io.StringIO(transcript_html) as transcript_file:
                    await log_channel.send(file=discord.File(transcript_file, filename="transcript.html"))
            await interaction.channel.delete()
        else:
            embed = discord.Embed(title="<:ALERT_1:1089800062575591454> No Permission",
                                  description="You can't delete this ticket, If you accidently created this ticket please ping our staff members to pursue your request")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="Claim", emoji="<:CY_rocket:1089897485297778709>", custom_id="ticket:claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        claimer = interaction.user
        freelancer_role = discord.utils.get(guild.roles, name="Freelancer")

        if freelancer_role in claimer.roles:
            await interaction.response.send_message(f"{claimer.mention} feature coming soon", ephemeral=True)
        else:
            await interaction.response.send_message("feature coming soon.", ephemeral=True)

# --- PERSISTENT VIEW ---

class persistent(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown = commands.CooldownMapping.from_cooldown(
            1, 7200, commands.BucketType.user)
        self.add_item(discord.ui.Button(label='Terms of Service',
                      url='https://discord.com/channels/1076165556849356860/1076174059127177247', emoji="<:CY_book:1089904601945354390>"))

    @ui.button(label="Order", style=discord.ButtonStyle.gray, emoji="<:CY_cart:1089894161383178310>", custom_id="persistent_view:ticket")
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = bot.get_guild(c.guild)
        ticket_category = discord.utils.get(guild.categories, name="━━━| 🎫 TICKETS |━━━")
        existing_ticket_channel = get(ticket_category.channels, name=f"🎫〢{interaction.user.name.lower()}")

        if existing_ticket_channel is not None:
            await interaction.response.send_message("You already have a ticket open. Please wait for a Staff to respond before creating a new ticket.", ephemeral=True)
            return
        else:
            modal = MyModal()
            await interaction.response.send_modal(modal)

    @ui.button(label="Support", style=discord.ButtonStyle.gray, emoji="<:CY_user:1089898348519112735>", custom_id="persistent_view:support")
    async def support(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = bot.get_guild(c.guild)
        ticket_category = discord.utils.get(guild.categories, name="━━━| 🎫 TICKETS |━━━")
        existing_ticket_channel = get(ticket_category.channels, name=f"🎫〢{interaction.user.name.lower()}")

        if existing_ticket_channel is not None:
            await interaction.response.send_message("You already have a ticket open. Please wait for a Staff to respond before creating a new ticket.", ephemeral=True)
            return
        else:
            modal = Support()
            await interaction.response.send_modal(modal)

# --- COMMANDS ---

@bot.command(name="send")
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(title="<:CY_ticket:1089895595126300802> Ticket Counter!",
                          description="<:CY_cart:1089894161383178310>**__Making a Purchase__**\n> <:B7:1089799856618475591> If you would like to **purchase** any sort of *service or items*. `kindly react` with <:CY_cart:1089894161383178310>\n\n<:CY_user:1089898348519112735>**__Help or Support__**\n> <:B7:1089799856618475591> If you require any help related to our service or need any *fixes or Refunds* `please React` with <:CY_user:1089898348519112735>\n\n<:CY_book:1089904601945354390>**__Terms Of Service__**\n> <:B7:1089799856618475591> Kindly Go through the Terms of our Service before `making any purchase`. We wont be responsible for any of confusion caused <:CY_book:1089904601945354390>\n\n**__ACCEPTED PAYMENT__**\n> <:Paypal40:1090162392022917181> <:0_CashApp:1090161966376566907> <:crypto19:1090161976279318538> <:vls_bank:1090162364961263726> <:upi:1090188335781257286>", color=discord.Color.red())
    embed.set_footer(text="Cypro Freelance", icon_url=c.icon_url)
    embed.set_image(
        url="https://media.discordapp.net/attachments/931781513723404339/1117717972228780122/ticket.png")
    embed.set_thumbnail(url=c.icon_url)

    await ctx.send(embed=embed, view=persistent())


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user} ({bot.user.id})')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    await bot.process_commands(message)

bot.run(os.getenv('TOKEN'))
