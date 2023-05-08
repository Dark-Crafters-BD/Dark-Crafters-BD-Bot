import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
AUTHORIZATION_CODES = os.getenv("AUTHORIZATION_CODES").split(", ")
bot = commands.AutoShardedBot(command_prefix="~",
                              intents=discord.Intents(guilds=True, members=True, messages=True, message_content=True))
bot.remove_command('help')
tree = bot.tree

# ------------------------- VARIABLES: START -------------------------
SUGGESTION_CHANNEL = 1105144058977980510
REPORT_CHANNEL = 1105144082382205020
LOG_CHANNEL = 1105147469152669806


# ------------------------- VARIABLES: END -------------------------


async def sendLog(user: int, timestamp, title, msg):
    user = await bot.fetch_user(user)
    await bot.get_channel(LOG_CHANNEL).send(
        embed=discord.Embed(
            title=title,
            description=msg,
            color=user.accent_color,
            timestamp=timestamp
        ).set_author(name=user.name, url=f"https://discord.com/users/{user.id}", icon_url=user.avatar.url)
    )


@bot.event
async def on_ready():
    print(f"{bot.user.name} is Ready!")


@tree.command(name="ping", description="🏓 Shows the Bot Latency")
async def ping(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(
        content="Pinging..."
    )

    await interaction.edit_original_response(
        embed=discord.Embed(
            title="Ping",
            description=f"Bot Latency: {round(bot.latency * 1000)}",
            color=discord.Color.random()
        ),
        content=""
    )


@tree.command(name="sync", description="Sync the Command Tree [AUTHORIZATION REQUIRED]",
              guild=discord.Object(id=797125529031016448))
async def sync(interaction: discord.Interaction):
    class AuthorizationModal(discord.ui.Modal, title="Authorization"):
        def __init__(self):
            super(AuthorizationModal, self).__init__(timeout=None)

        code = discord.ui.TextInput(
            label="Enter the Authentication Code",
            style=discord.TextStyle.short,
            placeholder="Enter the Assistant Authorization Code",
            min_length=4,
            max_length=4,
            required=True
        )

        async def on_submit(self, interaction: discord.Interaction, /) -> None:
            if self.code.value not in AUTHORIZATION_CODES:
                await sendLog(interaction.user.id, interaction.created_at, "Command Tree Synchronization",
                              "Command Tree Synchronization Failed: Authorization Failed!")
                return await interaction.response.send_message("Authorization Failed! Invalid Code!", ephemeral=True)
            await interaction.response.send_message("Syncing...")
            await tree.sync()
            await sendLog(interaction.user.id, interaction.created_at, "Command Tree Synchronization",
                          "Command Tree Successfully Synced!")
            await interaction.edit_original_response(content="Successfully Synced!")

    await interaction.response.send_modal(AuthorizationModal())


bot.run(os.getenv("TOKEN"))
