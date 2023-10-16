import discord
from discord.ext import commands
from discord import app_commands
import json
import datetime
from typing import Optional
import result_module
import result_list


# Get configuration.json
with open("configuration.json", "r") as config: 
	data = json.load(config)
	token = data["token"]

MY_GUILD = discord.Object(id=1162339357106131028)

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

@client.tree.command()
@app_commands.describe(
    #message_id = 'Nachricht-ID von dem Ergebnis, das bearbeitet werden soll'
)
async def add_result(interaction: discord.Interaction):
    text = "Nachricht"
    
    await interaction.response.send_message(text) #ephemeral=True macht die nachricht unsichtbar aber gibt option zum verwerfen -> BAD
    antwort = await interaction.original_response() #Nachricht, die ich gerade gesendet habe
    message = await antwort.fetch()    #message transformiert, so dass ich id rausfinden kann
    id = message.id
    await message.edit(content= text + f"\nNutze diese Message_ID zum löschen oder bearbeiten dieses Ergebnisses: __{id}__")
    print(id)

#EDIT hat problem: Message-ID ist Devmode feature, wie kann user seine alte nachricht editen? -> Delete braucht auch message_ID
client.run(token)