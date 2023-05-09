import asyncio
import os
from dotenv import load_dotenv
import discord
from discord import app_commands
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
BOT_DEV_ROLE = 1014572791183441931

# ------------------------- VARIABLES: END -------------------------


# ------------------------- GROUPS: START -------------------------

suggestion_group = app_commands.Group(name="suggestion", description='Suggestion group for Discord or MC')


# ------------------------- GROUPS: SEND -------------------------


# ------------------------- VIEWS: START -------------------------

class SuggestionConfirmation(discord.ui.View):
    def __init__(self, InteractionUser, suggestion_content, suggestion_type, InteractionCreation, InteractionCMD):
        self.InteractionUser = InteractionUser
        self.suggestion_content = suggestion_content
        self.suggestion_type = suggestion_type
        self.InteractionCreation = InteractionCreation
        self.InteractionCMD = InteractionCMD
        super(SuggestionConfirmation, self).__init__(timeout=300)

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if self.InteractionUser == interaction.user.id:
            return True
        else:
            await interaction.response.send_message("Actions with that Interaction can't be operated by you!",
                                                    ephemeral=True)
            return False

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True

        try:
            user = await bot.fetch_user(self.InteractionUser)
            await discord.DMChannel.send(
                user,
                embed=discord.Embed(
                    title=f"Suggestion: {self.suggestion_type}",
                    description=self.suggestion_content,
                    timestamp=self.InteractionCreation,
                    color=user.accent_color
                ).set_author(
                    name=user.name,
                    url=f"https://discord.com/users/{user.id}",
                    icon_url=user.avatar.url
                )
            )
            await self.message.edit(
                content="The buttons are disabled because the view is timed out. The Timeout occurred after 5 minutes!",
                view=self)
        except:
            pass

        try:
            self.stop()
        except:
            pass
        
        await sendLog(self.InteractionUser, self.InteractionCreation,
                      f"Suggestion Submission Process: `/{self.InteractionCMD}`",
                      f"Buttons Timed out as no action within 5 minutes!")

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=None)
        followup = await interaction.followup.send('Confirming...', ephemeral=True)
        m = await bot.get_channel(SUGGESTION_CHANNEL).send(
            embed=discord.Embed(
                title=f"Suggestion: {self.suggestion_type}",
                description=self.suggestion_content,
                timestamp=interaction.created_at,
                color=(await bot.fetch_user(interaction.user.id)).accent_color
            ).set_author(
                name=interaction.user.name,
                url=f"https://discord.com/users/{interaction.user.id}",
                icon_url=interaction.user.avatar.url
            )
        )
        await followup.edit(
            content="Thanks for your Suggestion!\n\nHappy crafting! 🎉🎮🧱"
        )
        try:
            self.stop()
        except:
            pass
        await sendLog(interaction.user.id, interaction.created_at,
                      f"Suggestion Submission Process: `/{self.InteractionCMD}`",
                      f"Suggestion Submission Confirmed from Confirmation Procedure!\n[Suggestion Message]({m.jump_url})")

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=None)
        followup = await interaction.followup.send('Cancelling...', ephemeral=True)
        await asyncio.sleep(2)
        try:
            await interaction.user.send(
                embed=discord.Embed(
                    title=f"Suggestion: {self.suggestion_type}",
                    description=self.suggestion_content,
                    timestamp=interaction.created_at,
                    color=(await bot.fetch_user(interaction.user.id)).accent_color
                ).set_author(
                    name=interaction.user.name,
                    url=f"https://discord.com/users/{interaction.user.id}",
                    icon_url=interaction.user.avatar.url
                )
            )

            await followup.edit(
                content="Suggestion Process Aborted! But we'd like to get new suggestion(s) from you, that's why a copy of this suggestion draft has sent to your DM.\n\nHappy crafting! 🎉🎮🧱"
            )

        except:
            await followup.edit(
                content="Suggestion Process Aborted! But we'd like to get new suggestion(s) from you, that's why I tried to send a copy of this suggestion draft to your DM but failed somehow (might be Blocking Issue).\n\nHappy crafting! 🎉🎮🧱"
            )
        try:
            self.stop()
        except:
            pass
        await sendLog(interaction.user.id, interaction.created_at,
                      f"Suggestion Submission Process: `/{self.InteractionCMD}`",
                      f"Suggestion Submission Cancelled in Confirmation Procedure!")


# ------------------------- VIEWS: END -------------------------


async def sendLog(user: int, timestamp, title, msg, content=None):
    user = await bot.fetch_user(user)
    await bot.get_channel(LOG_CHANNEL).send(
        content=content,
        embed=discord.Embed(
            title=title,
            description=msg,
            color=user.accent_color,
            timestamp=timestamp
        ).set_author(name=user.name, url=f"https://discord.com/users/{user.id}", icon_url=user.avatar.url)
    )


@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    await sendLog(interaction.user.id, interaction.created_at, f"Exception Raised on `/{interaction.command.name}`",
                  f"```py\n{str(error)}\n```",
                  f"{discord.utils.get(interaction.guild.roles, id=1014572791183441931).mention}")
    await interaction.followup.send(
        "Unfortunately an unexpected error occurred when executing! I just informed about the issue to the Developers and hopefully they will fix it soon!\n\nThanks for your patience! Mine with DCB! ⛏🎮🧱",
        ephemeral=True)


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
            description=f"Bot Latency: {round(bot.latency * 1000)} ms",
            color=(await bot.fetch_user(interaction.user.id)).accent_color
        ),
        content=""
    )
    await sendLog(interaction.user.id, interaction.created_at, "Command Execution",
                  f"Successfully executed: `{ping.name}`")


@tree.command(name="sync", description="Sync the Command Tree [AUTHORIZATION REQUIRED]",
              guild=discord.Object(id=797125529031016448))
async def sync(interaction: discord.Interaction) -> None:
    class AuthorizationModal(discord.ui.Modal, title="Sync Authorization"):
        def __init__(self):
            super(AuthorizationModal, self).__init__(timeout=None)

        code = discord.ui.TextInput(
            label="Enter the Authentication Code",
            style=discord.TextStyle.short,
            placeholder="Enter the Developer Authorization Code",
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


@suggestion_group.command(name="minecraft-server", description="Give us suggestion for our Minecraft Server")
async def suggestion_mc(interaction: discord.Interaction) -> None:
    class SuggestionModal(discord.ui.Modal, title="Suggestion"):
        def __init__(self):
            super(SuggestionModal, self).__init__(timeout=None)

        suggestion_content = discord.ui.TextInput(
            label="What's the Suggestion?",
            style=discord.TextStyle.short,
            placeholder="Write your Suggestion here...",
            min_length=10,
            required=True
        )

        async def on_submit(self, interaction: discord.Interaction, /) -> None:
            await interaction.response.send_message("Hang on a second...", ephemeral=True)
            embed = discord.Embed(
                title=f"Suggestion: Minecraft Server",
                description=self.suggestion_content.value,
                timestamp=interaction.created_at,
                color=(await bot.fetch_user(interaction.user.id)).accent_color
            ).set_author(
                name=interaction.user.name,
                url=f"https://discord.com/users/{interaction.user.id}",
                icon_url=interaction.user.avatar.url
            )
            view = SuggestionConfirmation(
                interaction.user.id,
                self.suggestion_content.value,
                "Minecraft Server",
                interaction.created_at,
                f"{suggestion_group.name} {interaction.command.name}"
            )
            await interaction.edit_original_response(
                content="",
                embed=embed,
                view=view
            )
            view.message = await interaction.original_response()
            await sendLog(interaction.user.id, interaction.created_at,
                          f"Suggestion Submission Process: `/suggestion minecraft-server`",
                          f"Suggestion Confirmation Buttons Issued!")

    await interaction.response.send_modal(SuggestionModal())
    await sendLog(interaction.user.id, interaction.created_at, f"`/{suggestion_group.name} {interaction.command.name}`",
                  f"Suggestion Submission Form Issued!")


if __name__ == '__main__':
    tree.add_command(suggestion_group)
    bot.run(os.getenv("TOKEN"))
