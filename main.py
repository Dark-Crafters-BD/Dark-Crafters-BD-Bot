import asyncio
import collections
import json
import os
import random
import string
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
import firebase_admin
from firebase_admin import credentials, db


# VARIABLES
SUBMIT_CHANNEL_ID = 915567338126974976
POINT_PER_CORRECT = 3
POINT_DEDUCT_PER_WRONG = 1
RULES_MESSAGE_LINK = "https://discord.com/channels/797125529031016448/1105012708052574268/1119165124293427201"
QUIZ_PING_ROLE_ID = 1117758291313963149
QUIZ_MOD_ROLE_ID = 1117729292923719721


load_dotenv()
AUTHORIZATION_CODES = os.getenv("AUTHORIZATION_CODES").split(", ")
__KEY__ = os.getenv("FIREBASE_KEY")

bot = commands.AutoShardedBot(command_prefix="~",
                              intents=discord.Intents(guilds=True, members=True, messages=True, message_content=True))
bot.remove_command('help')
tree = bot.tree
cred = credentials.Certificate(json.loads(__KEY__))
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://dark-crafters-bd-default-rtdb.firebaseio.com/'
})
ref = db.reference()

# ------------------------- VARIABLES: START -------------------------

SUGGESTION_CHANNEL = 1105144058977980510
REPORT_CHANNEL = 1105144082382205020
LOG_CHANNEL = 1105147469152669806
BOT_DEV_ROLE = 1014572791183441931

# ------------------------- VARIABLES: END -------------------------

# ------------------------- FUNCTION: START -------------------------

def generate_id(length):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


# ------------------------- FUNCTION: END -------------------------

# ------------------------- PERSISTENT: START -------------------------

def PERSISTENT():
    class UporDownVotePERSISTENT(discord.ui.View):
        def __init__(self):
            super(UporDownVotePERSISTENT, self).__init__(timeout=None)

        @discord.ui.button(label='Upvote', style=discord.ButtonStyle.green, emoji="⬆️", custom_id="vote_up")
        async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed = interaction.message.embeds[0]
            SuggestionID = embed.footer.text.split("\n")[1].replace("Suggestion ID: ", '')
            SuggestionDB = ref.get()['Suggestions'][SuggestionID]
            ischanged = False
            isedit = False
            if "Upvoters" in SuggestionDB and str(interaction.user.id) in SuggestionDB['Upvoters']:
                pass
            elif "Downvoters" in SuggestionDB and str(interaction.user.id) in SuggestionDB['Downvoters']:
                up_vote_count = int(SuggestionDB['Upvotes']) + 1 if 'Upvotes' in SuggestionDB else 1
                down_vote_count = int(SuggestionDB['Downvotes']) - 1 if 'Downvotes' in SuggestionDB else 0
                count_value = f"```\nUpvotes: {up_vote_count}\nDownvotes: {down_vote_count}\n```"
                ref.child("Suggestions").child(SuggestionID).child("Upvotes").set(str(up_vote_count))
                ref.child("Suggestions").child(SuggestionID).child("Downvotes").set(str(down_vote_count))
                ref.child("Suggestions").child(SuggestionID).child("Downvoters").child(
                    str(interaction.user.id)).delete()
                ref.child("Suggestions").child(SuggestionID).child("Upvoters").child(str(interaction.user.id)).set(
                    str(interaction.user))
                ischanged = True
                isedit = True
            else:
                up_vote_count = int(SuggestionDB['Upvotes']) + 1 if 'Upvotes' in SuggestionDB else 1
                down_vote_count = int(SuggestionDB['Downvotes']) if 'Downvotes' in SuggestionDB else 0
                count_value = f"```\nUpvotes: {up_vote_count}\nDownvotes: {down_vote_count}\n```"

                ref.child("Suggestions").child(SuggestionID).child("Upvotes").set(str(up_vote_count))
                ref.child("Suggestions").child(SuggestionID).child("Upvoters").child(str(interaction.user.id)).set(
                    str(interaction.user))
                isedit = True

            if isedit:
                embed.insert_field_at(index=0,
                                      name=embed.fields[-2].name,
                                      value=count_value,
                                      inline=False)
                embed.remove_field(1)
                if (up_vote_count + 1) == down_vote_count:
                    embed.insert_field_at(index=1,
                                          name=embed.fields[1].name,
                                          value="```\nTied```\n", inline=False)
                    embed.remove_field(2)
                elif (up_vote_count + 1) > down_vote_count:
                    embed.insert_field_at(index=1,
                                          name=embed.fields[1].name,
                                          value="```\nMajority of Upvotes\n```", inline=False)
                    embed.remove_field(2)
                elif (up_vote_count + 1) < down_vote_count:
                    embed.insert_field_at(index=1,
                                          name=embed.fields[1].name,
                                          value="```\nMajority of Downvotes\n```", inline=False)
                    embed.remove_field(2)

                await interaction.response.edit_message(embed=embed)
            if ischanged:
                await interaction.followup.send(
                    "Your vote has been changed from Downvote to Upvote!\n\nThanks for your vote! Your vote helps us to take decisions!",
                    ephemeral=True)
            else:
                await interaction.followup.send("Thanks for your vote! Your vote helps us to take decisions!",
                                                ephemeral=True)
            await sendLog(interaction.user.id, interaction.created_at, "Suggestion Voted",
                          f"Upvote to [Suggestion {SuggestionID}]({SuggestionDB['Suggestion Message URL']})\n**Current Statistics**\n{count_value}")

        @discord.ui.button(label='Downvote', style=discord.ButtonStyle.red, emoji="⬇️", custom_id="vote_down")
        async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed = interaction.message.embeds[0]
            SuggestionID = embed.footer.text.split("\n")[1].replace("Suggestion ID: ", '')
            SuggestionDB = ref.get()['Suggestions'][SuggestionID]
            ischanged = False
            isedit = False
            if "Downvoters" in SuggestionDB and str(interaction.user.id) in SuggestionDB['Downvoters']:
                pass
            elif "Upvoters" in SuggestionDB and str(interaction.user.id) in SuggestionDB['Upvoters']:
                up_vote_count = int(SuggestionDB['Upvotes']) - 1 if 'Upvotes' in SuggestionDB else 0
                down_vote_count = int(SuggestionDB['Downvotes']) + 1 if 'Downvotes' in SuggestionDB else 1
                count_value = f"```\nUpvotes: {up_vote_count}\nDownvotes: {down_vote_count}\n```"
                ref.child("Suggestions").child(SuggestionID).child("Upvotes").set(str(up_vote_count))
                ref.child("Suggestions").child(SuggestionID).child("Downvotes").set(str(down_vote_count))
                ref.child("Suggestions").child(SuggestionID).child("Upvoters").child(str(interaction.user.id)).delete()
                ref.child("Suggestions").child(SuggestionID).child("Downvoters").child(str(interaction.user.id)).set(
                    str(interaction.user))
                ischanged = True
                isedit = True
            else:
                up_vote_count = int(SuggestionDB['Upvotes']) if 'Upvotes' in SuggestionDB else 0
                down_vote_count = int(SuggestionDB['Downvotes']) + 1 if 'Downvotes' in SuggestionDB else 1
                count_value = f"```\nUpvotes: {up_vote_count}\nDownvotes: {down_vote_count}\n```"
                ref.child("Suggestions").child(SuggestionID).child("Upvotes").set(str(up_vote_count))
                ref.child("Suggestions").child(SuggestionID).child("Upvoters").child(str(interaction.user.id)).set(
                    str(interaction.user))
                isedit = True

            if isedit:
                embed.insert_field_at(index=0,
                                      name=embed.fields[-2].name,
                                      value=count_value,
                                      inline=False)
                embed.remove_field(1)
                if up_vote_count == (down_vote_count + 1):
                    embed.insert_field_at(index=1,
                                          name=embed.fields[1].name,
                                          value="```\nTied\n```", inline=False)
                    embed.remove_field(2)
                elif up_vote_count > (down_vote_count + 1):
                    embed.insert_field_at(index=1,
                                          name=embed.fields[1].name,
                                          value="```\nMajority of Upvotes\n```", inline=False)
                    embed.remove_field(2)
                elif up_vote_count < (down_vote_count + 1):
                    embed.insert_field_at(index=1,
                                          name=embed.fields[1].name,
                                          value="```\nMajority of Downvotes\n```", inline=False)
                    embed.remove_field(2)

                await interaction.response.edit_message(embed=embed)
            if ischanged:
                await interaction.followup.send(
                    "Your vote has been changed from Upvote to Downvote!\n\nThanks for your vote! Your vote helps us to take decisions!",
                    ephemeral=True)
            else:
                await interaction.followup.send("Thanks for your vote! Your vote helps us to take decisions!",
                                                ephemeral=True)
            await sendLog(interaction.user.id, interaction.created_at, "Suggestion Voted",
                          f"Downvote to [Suggestion {SuggestionID}]({SuggestionDB['Suggestion Message URL']})\n**Current Statistics**\n{count_value}")


    try:
        SUGGESTIONWHOLEDB = ref.get()['Suggestions']
        for key in SUGGESTIONWHOLEDB:
            msgID = int(str(SUGGESTIONWHOLEDB[key]['Suggestion Message URL']).split("/")[-1])
            bot.add_view(UporDownVotePERSISTENT(), message_id=msgID)
    except TypeError:
        pass

    class QuizSubmitBTNPERSISTENT(discord.ui.View):
        def __init__(self):
            super(QuizSubmitBTNPERSISTENT, self).__init__(timeout=None)
            self.db = ref.get()['Current Quiz']
            self.A.custom_id = f"A_{self.db['data']['id']}"
            self.B.custom_id = f"B_{self.db['data']['id']}"
            self.C.custom_id = f"C_{self.db['data']['id']}"
            self.D.custom_id = f"D_{self.db['data']['id']}"

        async def correct(self, user_id):
            ref.child('Current Quiz').child("Submitters").child(str(user_id)).set("Correct")

        async def wrong(self, user_id):
            ref.child('Current Quiz').child("Submitters").child(str(user_id)).set("Wrong")

        @discord.ui.button(label="A", style=discord.ButtonStyle.blurple)
        async def A(self, interaction: discord.Interaction, button: discord.ui.Button):
            if ref.get() is not None and 'Current Quiz' in ref.get() and 'Submitters' in ref.get()[
                'Current Quiz'] and str(interaction.user.id) in ref.get()['Current Quiz']['Submitters']:
                await interaction.response.send_message("You've already submitted once!", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            if str(self.db['data']['correct']).lower() != "a":
                await self.wrong(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")
            else:
                await self.correct(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")

        @discord.ui.button(label="B", style=discord.ButtonStyle.blurple)
        async def B(self, interaction: discord.Interaction, button: discord.ui.Button):
            if ref.get() is not None and 'Current Quiz' in ref.get() and 'Submitters' in ref.get()[
                'Current Quiz'] and str(interaction.user.id) in ref.get()['Current Quiz']['Submitters']:
                await interaction.response.send_message("You've already submitted once!", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            if str(self.db['data']['correct']).lower() != "b":
                await self.wrong(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")
            else:
                await self.correct(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")

        @discord.ui.button(label="C", style=discord.ButtonStyle.blurple)
        async def C(self, interaction: discord.Interaction, button: discord.ui.Button):
            if ref.get() is not None and 'Current Quiz' in ref.get() and 'Submitters' in ref.get()[
                'Current Quiz'] and str(interaction.user.id) in ref.get()['Current Quiz']['Submitters']:
                await interaction.response.send_message("You've already submitted once!", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            if str(self.db['data']['correct']).lower() != "c":
                await self.wrong(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")
            else:
                await self.correct(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")

        @discord.ui.button(label="D", style=discord.ButtonStyle.blurple)
        async def D(self, interaction: discord.Interaction, button: discord.ui.Button):
            if ref.get() is not None and 'Current Quiz' in ref.get() and 'Submitters' in ref.get()[
                'Current Quiz'] and str(interaction.user.id) in ref.get()['Current Quiz']['Submitters']:
                await interaction.response.send_message("You've already submitted once!", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            if str(self.db['data']['correct']).lower() != "d":
                await self.wrong(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")
            else:
                await self.correct(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")

    try:
        QUIZWHOLEDB = ref.get()['Current Quiz']
        msgID = int(str(QUIZWHOLEDB['data']['id']))
        bot.add_view(QuizSubmitBTNPERSISTENT(), message_id=msgID)
    except TypeError:
        pass
# ------------------------- PERSISTENT: END -------------------------

# ------------------------- VIEWS: START -------------------------

class UporDownVote(discord.ui.View):
    def __init__(self):
        super(UporDownVote, self).__init__(timeout=None)

    @discord.ui.button(label='Upvote', style=discord.ButtonStyle.green, emoji="⬆️", custom_id="vote_up")
    async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = interaction.message.embeds[0]
        SuggestionID = embed.footer.text.split("\n")[1].replace("Suggestion ID: ", '')
        SuggestionDB = ref.get()['Suggestions'][SuggestionID]
        ischanged = False
        isedit = False
        if "Upvoters" in SuggestionDB and str(interaction.user.id) in SuggestionDB['Upvoters']:
            pass
        elif "Downvoters" in SuggestionDB and str(interaction.user.id) in SuggestionDB['Downvoters']:
            up_vote_count = int(SuggestionDB['Upvotes']) + 1 if 'Upvotes' in SuggestionDB else 1
            down_vote_count = int(SuggestionDB['Downvotes']) - 1 if int(SuggestionDB['Downvotes']) > 1 else 0
            count_value = f"```\nUpvotes: {up_vote_count}\nDownvotes: {down_vote_count}\n```"
            ref.child("Suggestions").child(SuggestionID).child("Upvotes").set(str(up_vote_count))
            ref.child("Suggestions").child(SuggestionID).child("Downvotes").set(str(down_vote_count))
            ref.child("Suggestions").child(SuggestionID).child("Downvoters").child(str(interaction.user.id)).delete()
            ref.child("Suggestions").child(SuggestionID).child("Upvoters").child(str(interaction.user.id)).set(str(interaction.user))
            ischanged = True
            isedit = True
        else:
            up_vote_count = int(SuggestionDB['Upvotes']) + 1 if 'Upvotes' in SuggestionDB else 1
            down_vote_count = int(SuggestionDB['Downvotes']) if 'Downvotes' in SuggestionDB else 0

            count_value = f"```\nUpvotes: {up_vote_count}\nDownvotes: {down_vote_count}\n```"

            ref.child("Suggestions").child(SuggestionID).child("Upvotes").set(str(up_vote_count))
            ref.child("Suggestions").child(SuggestionID).child("Upvoters").child(str(interaction.user.id)).set(
                str(interaction.user))
            isedit = True

        if isedit:
            embed.insert_field_at(index=0,
                                  name=embed.fields[-2].name,
                                  value=count_value,
                                  inline=False)
            embed.remove_field(1)
            if (up_vote_count + 1) == down_vote_count:
                embed.insert_field_at(index=1,
                                      name=embed.fields[1].name,
                                      value="```\nTied```\n", inline=False)
                embed.remove_field(2)
            elif (up_vote_count + 1) > down_vote_count:
                embed.insert_field_at(index=1,
                                      name=embed.fields[1].name,
                                      value="```\nMajority of Upvotes\n```", inline=False)
                embed.remove_field(2)
            elif (up_vote_count + 1) < down_vote_count:
                embed.insert_field_at(index=1,
                                      name=embed.fields[1].name,
                                      value="```\nMajority of Downvotes\n```", inline=False)
                embed.remove_field(2)

            await interaction.response.edit_message(embed=embed)
        if ischanged:
            await interaction.followup.send("Your vote has been changed from Downvote to Upvote!\n\nThanks for your vote! Your vote helps us to take decisions!", ephemeral=True)
        else:
            await interaction.followup.send("Thanks for your vote! Your vote helps us to take decisions!", ephemeral=True)
        await sendLog(interaction.user.id, interaction.created_at, "Suggestion Voted", f"Upvote to [Suggestion {SuggestionID}]({SuggestionDB['Suggestion Message URL']})\n**Current Statistics**\n{count_value}")

    @discord.ui.button(label='Downvote', style=discord.ButtonStyle.red, emoji="⬇️", custom_id="vote_down")
    async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = interaction.message.embeds[0]
        SuggestionID = embed.footer.text.split("\n")[1].replace("Suggestion ID: ", '')
        SuggestionDB = ref.get()['Suggestions'][SuggestionID]
        ischanged = False
        isedit = False
        if "Downvoters" in SuggestionDB and str(interaction.user.id) in SuggestionDB['Downvoters']:
            pass
        elif "Upvoters" in SuggestionDB and str(interaction.user.id) in SuggestionDB['Upvoters']:
            up_vote_count = int(SuggestionDB['Upvotes']) - 1 if int(SuggestionDB['Upvotes']) > 1 else 0
            down_vote_count = int(SuggestionDB['Downvotes']) + 1 if 'Downvotes' in SuggestionDB else 1
            count_value = f"```\nUpvotes: {up_vote_count}\nDownvotes: {down_vote_count}\n```"
            ref.child("Suggestions").child(SuggestionID).child("Upvotes").set(str(up_vote_count))
            ref.child("Suggestions").child(SuggestionID).child("Downvotes").set(str(down_vote_count))
            ref.child("Suggestions").child(SuggestionID).child("Upvoters").child(str(interaction.user.id)).delete()
            ref.child("Suggestions").child(SuggestionID).child("Downvoters").child(str(interaction.user.id)).set(
                str(interaction.user))
            ischanged = True
            isedit = True
        else:
            up_vote_count = int(SuggestionDB['Upvotes']) if 'Upvotes' in SuggestionDB else 0
            down_vote_count = int(SuggestionDB['Downvotes']) + 1 if 'Downvotes' in SuggestionDB else 1
            count_value = f"```\nUpvotes: {up_vote_count}\nDownvotes: {down_vote_count}\n```"
            ref.child("Suggestions").child(SuggestionID).child("Upvotes").set(str(up_vote_count))
            ref.child("Suggestions").child(SuggestionID).child("Upvoters").child(str(interaction.user.id)).set(
                str(interaction.user))
            isedit = True

        if isedit:
            embed.insert_field_at(index=0,
                                  name=embed.fields[-2].name,
                                  value=count_value,
                                  inline=False)
            embed.remove_field(1)
            if up_vote_count == (down_vote_count + 1):
                embed.insert_field_at(index=1,
                                      name=embed.fields[1].name,
                                      value="```\nTied\n```", inline=False)
                embed.remove_field(2)
            elif up_vote_count > (down_vote_count + 1):
                embed.insert_field_at(index=1,
                                      name=embed.fields[1].name,
                                      value="```\nMajority of Upvotes\n```", inline=False)
                embed.remove_field(2)
            elif up_vote_count < (down_vote_count + 1):
                embed.insert_field_at(index=1,
                                      name=embed.fields[1].name,
                                      value="```\nMajority of Downvotes\n```", inline=False)
                embed.remove_field(2)

            await interaction.response.edit_message(embed=embed)
        if ischanged:
            await interaction.followup.send("Your vote has been changed from Upvote to Downvote!\n\nThanks for your vote! Your vote helps us to take decisions!", ephemeral=True)
        else:
            await interaction.followup.send("Thanks for your vote! Your vote helps us to take decisions!", ephemeral=True)
        await sendLog(interaction.user.id, interaction.created_at, "Suggestion Voted", f"Downvote to [Suggestion {SuggestionID}]({SuggestionDB['Suggestion Message URL']})\n**Current Statistics**\n{count_value}")


class SuggestionConfirmation(discord.ui.View):
    def __init__(self, InteractionUser, suggestion_content, InteractionCreation, InteractionCMD):
        self.InteractionUser = InteractionUser
        self.suggestion_content = suggestion_content
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
                    title=f"Suggestion",
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
        sid = generate_id(8)

        m = await bot.get_channel(SUGGESTION_CHANNEL).send(
            embed=discord.Embed(
                title=f"Suggestion",
                description=self.suggestion_content,
                timestamp=interaction.created_at,
                color=(await bot.fetch_user(interaction.user.id)).accent_color
            ).set_author(
                name=interaction.user.name,
                url=f"https://discord.com/users/{interaction.user.id}",
                icon_url=interaction.user.avatar.url
            ).add_field(
                name="Statistics",
                value="```\nUpvotes: 0\nDownvotes: 0\n```",
                inline=False
            ).add_field(
                name="Automatic Result (Based on Votes)",
                value="```\nUnrated\n```"
            ).set_footer(text=f"To give Suggestion, use /suggest\nSuggestion ID: {sid}"),
            view=UporDownVote()
        )
        await followup.edit(
            content="Thanks for your Suggestion!\n\nHappy crafting! 🎉🎮🧱"
        )
        data = {
            "Suggestion By": f"{str(interaction.user.id)}",
            "Suggestion Message URL": str(m.jump_url)
        }
        try:
            ref.child("Suggestions").child(sid).set(data)
        except:
            await m.delete()
            await sendLog(interaction.user.id, interaction.created_at,
                          f"Suggestion Submission Process Failed: `/{self.InteractionCMD}`",
                          f"Suggestion Submission Confirmed but suggestion message deleted! ```\nFailed to save Suggestion Data in Database.\n```")
            try:
                self.stop()
            except:
                pass
            return
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
                    title=f"Suggestion",
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
    raise error


@bot.event
async def on_ready():
    PERSISTENT()
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


@tree.command(name="suggest", description="Give us suggestion!")
async def suggestion_mc(interaction: discord.Interaction) -> None:
    class SuggestionModal(discord.ui.Modal, title="Suggestion"):
        def __init__(self, cmd_text):
            self.cmd_text = cmd_text
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
                title=f"Suggestion",
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
                interaction.created_at,
                self.cmd_text
            )
            await interaction.edit_original_response(
                content="",
                embed=embed,
                view=view
            )
            view.message = await interaction.original_response()
            await sendLog(interaction.user.id, interaction.created_at,
                          f"Suggestion Submission Process: `{self.cmd_text}`",
                          f"Suggestion Confirmation Buttons Issued!")

    await interaction.response.send_modal(SuggestionModal(f"{interaction.command.name}"))
    await sendLog(interaction.user.id, interaction.created_at, f"`/{interaction.command.name}`",
                  f"Suggestion Submission Form Issued!")


@tree.command(name="create-quiz", description="Creates a new Quiz!")
@app_commands.describe(
    channel="Mention the Channel where the Quiz will be published",
    title="Enter the Title of the Quiz Embed"
)
async def createQuiz(
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        title: str
):
    if QUIZ_MOD_ROLE_ID not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("You are not allowed to create Quiz!", ephemeral=True)

    class SubmitBTN(discord.ui.View):
        def __init__(self, msg_id):
            super(SubmitBTN, self).__init__(timeout=None)
            self.A.custom_id = f"A_{msg_id}"
            self.B.custom_id = f"B_{msg_id}"
            self.C.custom_id = f"C_{msg_id}"
            self.D.custom_id = f"D_{msg_id}"
            self.db = ref.get()['Current Quiz']

        async def correct(self, user_id):
            ref.child('Current Quiz').child("Submitters").child(str(user_id)).set("Correct")

        async def wrong(self, user_id):
            ref.child('Current Quiz').child("Submitters").child(str(user_id)).set("Wrong")

        @discord.ui.button(label="A", style=discord.ButtonStyle.blurple)
        async def A(self, interaction: discord.Interaction, button: discord.ui.Button):
            if ref.get() is not None and 'Current Quiz' in ref.get() and 'Submitters' in ref.get()[
                'Current Quiz'] and str(interaction.user.id) in ref.get()['Current Quiz']['Submitters']:
                await interaction.response.send_message("You've already submitted once!", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            if str(self.db['data']['correct']).lower() != "a" and:
                await self.wrong(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")
            else:
                await self.correct(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")


        @discord.ui.button(label="B", style=discord.ButtonStyle.blurple)
        async def B(self, interaction: discord.Interaction, button: discord.ui.Button):
            if ref.get() is not None and 'Current Quiz' in ref.get() and 'Submitters' in ref.get()[
                'Current Quiz'] and str(interaction.user.id) in ref.get()['Current Quiz']['Submitters']:
                await interaction.response.send_message("You've already submitted once!", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            if str(self.db['data']['correct']).lower() != "b":
                await self.wrong(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")
            else:
                await self.correct(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")

        @discord.ui.button(label="C", style=discord.ButtonStyle.blurple)
        async def C(self, interaction: discord.Interaction, button: discord.ui.Button):
            if ref.get() is not None and 'Current Quiz' in ref.get() and 'Submitters' in ref.get()[
                'Current Quiz'] and str(interaction.user.id) in ref.get()['Current Quiz']['Submitters']:
                await interaction.response.send_message("You've already submitted once!", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            if str(self.db['data']['correct']).lower() != "c":
                await self.wrong(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")
            else:
                await self.correct(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")

        @discord.ui.button(label="D", style=discord.ButtonStyle.blurple)
        async def D(self, interaction: discord.Interaction, button: discord.ui.Button):
            if ref.get() is not None and 'Current Quiz' in ref.get() and 'Submitters' in ref.get()[
                'Current Quiz'] and str(interaction.user.id) in ref.get()['Current Quiz']['Submitters']:
                await interaction.response.send_message("You've already submitted once!", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            if str(self.db['data']['correct']).lower() != "d":
                await self.wrong(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")

            else:
                await self.correct(interaction.user.id)
                await interaction.followup.send(content="Thanks for your Submission!\n\nYour Points will be added if you're correct!")

    class Confirm(discord.ui.View):
        def __init__(self, user_id, description, opt1, opt2, opt3, opt4, color, correct):
            self.InteractionUser = user_id
            self.description = description
            self.opt1 = opt1
            self.opt2 = opt2
            self.opt3 = opt3
            self.opt4 = opt4
            self.color = color
            self.correct = correct

            super(Confirm, self).__init__(timeout=300)

        async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
            if self.InteractionUser == interaction.user.id:
                return True
            else:
                await interaction.response.send_message("Actions attached with this Interaction can't be used by you!",
                                                        ephemeral=True)
                return False

        async def on_timeout(self) -> None:
            for item in self.children:
                item.disabled = True


            await self.message.edit(content="The buttons are disabled because the view is timed out. The Timeout occurred after 3 minutes!", view=self)


        @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.edit_message(view=None)
            followup = await interaction.followup.send('Confirming')
            em = discord.Embed(
                title=title,
                description=self.description,
                color=self.color,
                timestamp=interaction.created_at
            )

            em.add_field(name="Options", value=f"A. {self.opt1}\nB. {self.opt2}\nC. {self.opt3}\nD. {self.opt4}", inline=False)
            em.add_field(name="Rules", value=f"***\* You can submit once!***\n\n> Kindly check the [Rules of Quizs]({RULES_MESSAGE_LINK})", inline=False)
            em.set_footer(text="Quiz System by Tahsin!")
            if ref.get() != None and 'Current Quiz' in ref.get() and 'data' in ref.get()["Current Quiz"]:
                await followup.edit(content="Storing the Previous Quiz Data...")
                await sendLog(interaction.user.id, interaction.created_at, f"`/create-quiz`",
                              f"Storing the Previous Quiz Data...")
                previous_quiz_db = ref.get()['Current Quiz']['data']
                c = bot.get_channel(int(previous_quiz_db["channel"]))
                msg = await c.fetch_message(int(previous_quiz_db["id"]))

                btns = SubmitBTN(previous_quiz_db['id'])
                for item in btns.children:
                    if str(item.label).lower() == str(previous_quiz_db['correct']).lower():
                        item.style = discord.ButtonStyle.green
                    else:
                        item.style = discord.ButtonStyle.grey
                    item.disabled = True

                await msg.edit(embeds=[msg.embeds[0]], view=btns)

                ref.child("Past Quizs").child(
                    "1" if 'Past Quizs' not in ref.get() else str(len(ref.get()["Past Quizs"]))).set(
                    ref.get()["Current Quiz"])

                if 'Submitters' in ref.get()["Current Quiz"]:
                    await followup.edit(content="Giving points to the correct answer submitters...")
                    await sendLog(interaction.user.id, interaction.created_at, f"`/create-quiz`",
                                  f"Giving points to the correct answer submitters...")
                    for i in ref.get()["Current Quiz"]['Submitters']:
                        iscorrect = True if ref.get()["Current Quiz"]['Submitters'][
                                                str(i)] == 'Correct' else False
                        if 'Quiz Points' in ref.get():
                            if str(i) in ref.get()['Quiz Points']:
                                if iscorrect:
                                    ref.child('Quiz Points').child(str(i)).child("Points").set(
                                        str(int(ref.get()['Quiz Points'][str(i)]["Points"]) + POINT_PER_CORRECT))
                                    ref.child('Quiz Points').child(str(i)).child("Correct").set(
                                        str(int(ref.get()['Quiz Points'][str(i)]["Correct"]) + 1))
                                else:
                                    points = int(
                                        ref.get()['Quiz Points'][str(i)]["Points"]) - POINT_DEDUCT_PER_WRONG
                                    if points > -1:
                                        ref.child('Quiz Points').child(str(i)).child("Points").set(str(points))
                                        ref.child('Quiz Points').child(str(i)).child("Wrong").set(
                                            str(int(ref.get()['Quiz Points'][str(i)]["Wrong"]) + 1))
                                    else:
                                        ref.child('Quiz Points').child(str(i)).child("Wrong").set(
                                            str(int(ref.get()['Quiz Points'][str(i)]["Wrong"]) + 1))
                            else:
                                if iscorrect:
                                    ref.child('Quiz Points').child(str(i)).child("Points").set(
                                        str(POINT_PER_CORRECT))
                                    ref.child('Quiz Points').child(str(i)).child("Correct").set(str(1))
                                    ref.child('Quiz Points').child(str(i)).child("Wrong").set(str(0))
                        else:
                            if iscorrect:
                                ref.child('Quiz Points').child(str(i)).child("Points").set(str(POINT_PER_CORRECT))
                                ref.child('Quiz Points').child(str(i)).child("Correct").set(str(1))
                                ref.child('Quiz Points').child(str(i)).child("Wrong").set(str(0))

                await followup.edit(content="Resetting the Current Quiz DB...")
                await sendLog(interaction.user.id, interaction.created_at, f"`/create-quiz`",
                              f"Resetting the Current Quiz DB...")
                ref.child("Current Quiz").delete()
            await followup.edit(content="Preparing...")
            await sendLog(interaction.user.id, interaction.created_at, f"`/create-quiz`",
                          f"Preparing...")
            m = await channel.send(content=discord.utils.get(interaction.guild.roles, id=QUIZ_PING_ROLE_ID).mention, embed=em)

            ref.child("Current Quiz").child("data").set({
                "id": str(m.id),
                "channel": str(channel.id),
                "title": title,
                "description": self.description,
                "opt1": self.opt1,
                "opt2": self.opt2,
                "opt3": self.opt3,
                "opt4": self.opt4,
                "correct": self.correct
            })
            ref.child("Current Quiz").child("Submit Button").set(str(m.id))
            await m.edit(view=SubmitBTN(m.id))
            await followup.edit(content=f"Quiz Posted in {channel.mention}!")
            await sendLog(interaction.user.id, interaction.created_at, f"`/create-quiz`",
                          f"Quiz Confirmed!\n\n[Quiz Link]({m.jump_url})")

        @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.edit_message(view=None)
            followup = await interaction.followup.send('Cancelling')
            await interaction.followup.edit_message(message_id=followup.id, content=f"Cancelled!")
            await sendLog(interaction.user.id, interaction.created_at, f"`/create-quiz`",
                          f"Quiz Cancelled!")

    class getQuizDetails(discord.ui.Modal, title="Create a new Quiz"):
        def __init__(self):
            super(getQuizDetails, self).__init__(timeout=None)

        description = discord.ui.TextInput(
            label="Description of the Quiz!",
            style=discord.TextStyle.long,
            placeholder="Describe the Quiz Context!",
            required=True,
            max_length=3980,
            custom_id=f"{interaction.user.id}_description"
        )
        option_1 = discord.ui.TextInput(
            label="Option 1 (Correct)",
            style=discord.TextStyle.short,
            required=True,
            max_length=1024,
            custom_id=f"{interaction.user.id}_option1"
        )
        option_2 = discord.ui.TextInput(
            label="Option 2",
            style=discord.TextStyle.short,
            placeholder="",
            required=True,
            max_length=1024,
            custom_id=f"{interaction.user.id}_option2"
        )
        option_3 = discord.ui.TextInput(
            label="Option 3",
            style=discord.TextStyle.short,
            required=True,
            max_length=1024,
            custom_id=f"{interaction.user.id}_option3"
        )
        option_4 = discord.ui.TextInput(
            label="Option 4",
            style=discord.TextStyle.short,
            required=True,
            max_length=1024,
            custom_id=f"{interaction.user.id}_option4"
        )

        async def on_submit(self, interaction: discord.Interaction, /) -> None:
            await interaction.response.send_message("Wait a while...")
            options = [self.option_1.value, self.option_2.value, self.option_3.value, self.option_4.value]
            random.shuffle(options)
            correct = self.option_1.value
            options_as_index = {
                "0": "A",
                "1": "B",
                "2": "C",
                "3": "D"
            }
            option_1, option_2, option_3, option_4 = options[0], options[1], options[2], options[3]
            em = discord.Embed(
                title=title,
                description=self.description.value,
                color=discord.Color.random(),
                timestamp=interaction.created_at
            )
            em.add_field(name="Options", value=f"A. {option_1}\nB. {option_2}\nC. {option_3}\nD. {option_4}", inline=True)

            em.add_field(name="Correct Answer", value=f"{options_as_index[str(options.index(correct))]}. {correct}", inline=False)

            view = Confirm(user_id=interaction.user.id,
                    description=self.description.value,
                    opt1=option_1,
                    opt2=option_2,
                    opt3=option_3,
                    opt4=option_4,
                    color=em.color,
                    correct=options_as_index[str(options.index(correct))].lower())

            await interaction.edit_original_response(content="", embeds=[em],
                                                     view=view)

            view.message = await interaction.original_response()
            await sendLog(interaction.user.id, interaction.created_at, f"`/create-quiz`",
                          f"Quiz Confirmation Buttons Issued!")

    await interaction.response.send_modal(getQuizDetails())
    await sendLog(interaction.user.id, interaction.created_at, f"`/{interaction.command.name}`",
                  f"Quiz Information Form Issued!")


@tree.command(name='leaderboard',
              description="Shows the Leaderboard of the Quiz Point gained by Answering Correct!")
async def lb(interaction: discord.Interaction):
    await interaction.response.send_message("Fetching Database...")
    if ref.get() is not None and 'Quiz Points' in ref.get() and ref.get()['Quiz Points'] is not None:
        data = {}

        for i in ref.get()['Quiz Points']:
            if int(ref.get()['Quiz Points'][i]["Points"]) in data:
                try:
                    data[int(ref.get()['Quiz Points'][i]["Points"])].append(i)
                except:
                    data[int(ref.get()['Quiz Points'][i]["Points"])] = [
                        data[int(ref.get()['Quiz Points'][i]["Points"])], i]
            else:
                data[int(ref.get()['Quiz Points'][i]["Points"])] = i
        all_data = collections.OrderedDict(sorted(data.items()))
        sorted_data = {}
        for k, v in all_data.items():
            if type(v) == list:
                for i in v[::-1]:
                    sorted_data[i] = k
            else:
                sorted_data[v] = k
        sorted_data = dict(reversed(list(sorted_data.items())))
        data = []
        c = 0
        DatawithALLKEY = ref.get()['Quiz Points']
        for key in sorted_data:
            if str(key) in [str(m.id) for m in interaction.guild.members]:
                data.append(
                    f"{c + 1}. {interaction.guild.get_member(int(key)).mention} Points: {sorted_data[key]} ({DatawithALLKEY[str(key)]['Correct']} Correct and {DatawithALLKEY[str(key)]['Wrong']} Wrong Answers)")
                if c == 9:
                    break
                c += 1
        em = discord.Embed(
            title="Quiz Points Leaderboard",
            description="**Top 10**\n" + '\n'.join(data),
            color=discord.Color.random(),
            timestamp=interaction.created_at
        )
        if str(interaction.user.id) in sorted_data:
            em.add_field(name="Your Position",
                         value=f"{list(sorted_data).index(str(interaction.user.id)) + 1}. {interaction.user.mention} Points: {sorted_data[str(interaction.user.id)]} ({DatawithALLKEY[str(interaction.user.id)]['Correct']} Correct and {DatawithALLKEY[str(interaction.user.id)]['Wrong']} Wrong Answers)",
                         inline=False)
        else:
            em.add_field(name="Your Info", value=f"Not Found! You might never answered right of the Quizs!",
                         inline=False)
        await interaction.edit_original_response(content="", embed=em)
        await sendLog(interaction.user.id, interaction.created_at, f"`/{interaction.command.name}`",
                      f"Leaderboard showed!")
    else:
        em = discord.Embed(
            title="Quiz Points Leaderboard",
            description="Unfortunately, No Database Found for Quiz Points!",
            color=discord.Color.random(),
            timestamp=interaction.created_at
        )
        await interaction.edit_original_response(content="", embed=em)
        await sendLog(interaction.user.id, interaction.created_at, f"`/{interaction.command.name}`",
                      f"Leaderboard showing failed: No Database Found!")

if __name__ == '__main__':
    bot.run(os.getenv("TOKEN"))
