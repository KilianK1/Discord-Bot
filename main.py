import discord
from discord import app_commands
from datetime import datetime
import locale
import json
import result_list


# Get configuration.json
with open("configuration.json", "r") as config:
    data = json.load(config)
    token = data["token"]
    MATCHES_AND_RESULTS = data["matches_and_results_channel"]
    result_channel = data["result_channel"]

locale.setlocale(locale.LC_ALL, "de_DE")

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
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")


@client.tree.command()
@app_commands.describe(
    mein_team="Der Name deines Teams",
    gegner_team="Der Name des Gegner Teams",
    datum="Datum des Matches, Format: DD.MM.YY",
    uhrzeit="Uhrzeit des Matches",
    ergebnis="Ergebnis des Matches, leer lassen wenn noch nicht gespielt wurde",
    liga="Liga in der das Match stattfindet",
    format="BO1, BO2, etc. oder leer lassen",
)
async def add_result(
    interaction: discord.Interaction,
    mein_team: str,
    gegner_team: str,
    datum: str,
    liga: str,
    uhrzeit: str,
    ergebnis: str = "0 - 0",
    format: str = "",
):
    print("\nadd_result was called\n")

    uhrzeit.strip()
    datum.strip()  # es schleichen sich schnell führende und endende leerzeichen in userinput -> strip removed diese
    channel_id = interaction.channel_id

    try:
        date_format = result_list.zeit_format(datum=datum, zeit=uhrzeit)  # format
    except:
        await interaction.response.send_message(
            content="Format von Zeit oder Datum war nicht richtig, bitte versuche es erneut",
            delete_after=30,
        )
        return
    await interaction.response.send_message(
            content="Bot ist am Arbeiten..."
        )
    antwort = await interaction.original_response()  # Nachricht, die ich gerade gesendet habe
    message_id = str(antwort.id)

    result_dict = {
        "mein_team": mein_team.strip(),
        "gegner_team": gegner_team.strip(),
        "liga": liga.strip(),
        "ergebnis": ergebnis.strip(),
        "format": format.strip(),
        "message_id": message_id,
        "datetime": date_format,
        "game": result_channel[channel_id]
    }

    try:
        liste, jahr_kw = result_list.add(result_dict)
    except:
        await antwort.edit(content="Couldnt add result, looks like a bug :/", delete_after=30)
        return

    await antwort.edit(
        content = result_list.result_to_string(result_dict)
        + f"\nNutze diese Message_ID zum löschen oder bearbeiten deines Ergebnisses: {message_id}"
    )
    
    await update_kw_message(jahr_kw, liste)


@client.tree.command(
    name="edit",
    description="Nutze die Message_ID zum editen, leere Felder = nichts ändern",
)
@app_commands.describe(
    message_id="Die ID der Nachricht die du bearbeiten willst",
    mein_team="Der Name deines Teams",
    gegner_team="Der Name des Gegner Teams",
    datum="Datum des Matches, Format: DD.MM.YY",
    uhrzeit="Uhrzeit des Matches, Format: HH:MM",
    ergebnis="Ergebnis des Matches, leer lassen wenn noch nicht gespielt wurde",
    liga="Liga in der das Match stattfindet",
    format="BO1, BO2, etc. oder leer lassen",
)
async def edit_result(
    interaction: discord.Interaction,
    message_id: str,
    mein_team: str = "-1",
    gegner_team: str = "-1",
    datum: str = "-1",
    liga: str = "-1",
    uhrzeit: str = "-1",
    ergebnis: str = "-1",
    format: str = "-1",
):
    print("\nedit_result was called\n")
    
    try:
        message = await interaction.channel.fetch_message(message_id)
    except:
        await interaction.response.send_message(
            "Etwas ist schiefgelaufen, überprüfe ob deine Messagge_ID stimmt",
            delete_after=30,
        )
        return

    uhrzeit.strip()
    datum.strip()
    # überprüfe format von datum und uhrzeit unabhängig voneinander
    try:
        if datum != "-1":
            datetime.strptime(datum, "%d.%m.%y") 
        
        if uhrzeit != "-1":
            datetime.strptime(uhrzeit, "%H:%M")
    except:
        await interaction.response.send_message(
            "Format von Zeit/Datum ist falsch",
            delete_after=30,
        )
        return

    result_edit_dict = {
        "mein_team": mein_team.strip(),
        "gegner_team": gegner_team.strip(),
        "liga": liga.strip(),
        "ergebnis": ergebnis.strip(),
        "format": format.strip(),
        "message_id": message_id.strip(),
        "date": datum,
        "time": uhrzeit
    }

    try:
        res, new_liste, new_jahr_kw, old_jahr_kw = result_list.edit(result_edit_dict)
    except:
        await interaction.response.send_message(
            content="Couldnt find result you want to edit, check the message ID", delete_after=30
        )
        raise Exception

    await message.edit(
        content = result_list.result_to_string(res)
        + f"\nNutze diese Message_ID zum löschen oder bearbeiten deines Ergebnisses: {message_id}"
    )
    await interaction.response.send_message(
        "Dein Ergebnis wurde bearbeitet",
        delete_after=30,
    )

    old_liste = result_list.read(old_jahr_kw)
    
    # here we update the old kw message
    await update_kw_message(old_jahr_kw, old_liste)

    if new_jahr_kw != old_jahr_kw:
        # if KW was changed during edit we need to update new message as well
        await update_kw_message(new_jahr_kw, new_liste)


@client.tree.command(
    name="delete", description="Nutze die Message_ID vom Ergebnis um es zu löschen"
)
@app_commands.describe(
    message_id="Die ID der Nachricht die du löschen willst",
)
async def delete_result(
    interaction: discord.Interaction,
    message_id: str,
):
    print("\ndelete_result was called\n")

    message_id.strip()  # führende und endende leerzeichen in userinput -> strip removed diese
    try:
        message = await interaction.channel.fetch_message(message_id)
    except:
        await interaction.response.send_message(
            "Etwas ist schiefgelaufen, überprüfe ob deine Messagge_ID stimmt",
            delete_after=30,
        )
        return

    try:
        kw, liste = result_list.delete(message_id)
    except:
        await interaction.response.send_message(
            content="Something went wrong", delete_after=30
        )
        return

    await message.delete()

    await interaction.response.send_message(
        content="Nachricht wurde gelöscht", delete_after=30
    )
    await update_kw_message(kw, liste)


async def update_kw_message(jahr_KW, liste):
    print(f'\nstarting main.update_KW_Message for KW: {jahr_KW}\n')

    channel = client.get_channel(MATCHES_AND_RESULTS)

    
    # Do I need a new message or does it exist? create it if doesnt exist
    try:
        message_ID = result_list.read_dictionary(jahr_KW)  # message_id finden
    except KeyError:
        message_ID = await create_kw_message(jahr_KW, liste)

    try:
        message = await channel.fetch_message(message_ID)
    except:
        await channel.send_message(
            "Etwas ist schiefgelaufen, KW Messagge wurde nicht gefunden",
            delete_after=30,
        )
        return
    
    if not liste: #liste ist leer
        await delete_kw_message(jahr_KW, message)
        return

    text = kw_string(liste, jahr_KW)
    await message.edit(content = text)
    print(f'finished main.update_KW_Message for KW: {jahr_KW}\n')

def kw_string(liste, jahr_KW):

    split_dict = dict()
    while liste:
        current_game = liste[0]["game"] #take first results game
        split_dict[current_game] = list()   #create a list for each game
        for i in liste:
            if i["game"] == current_game:
                # fülle neue liste mit allen results die zu current game gehören
                split_dict[current_game].append(liste[i])   
            #sollte automatisch nach zeit sortiert sein weil input liste nach zeit sortiert war

    new_text = f"# __KW {jahr_KW}:__\n\n"  # # ist für Header
    for split_liste in split_dict:
        game = split_liste[0]["game"]
        new_text += "## " + game + "\n"
        for result in split_liste:
            new_text += (
                result_list.result_to_string(result) + "\n"
            ) 

async def delete_kw_message(jahr_KW, message):
    dict = result_list.read("dictionary")

    #delete dict entry (kw, message_id)
    dict.pop(jahr_KW)
    #delete kw_liste(jahr_KW) entry in ditctionary
    dict["kw_liste"].remove(jahr_KW)

    result_list.write(dict ,"dictionary")
    
    #delete message
    await message.delete()


async def create_kw_message(jahr_KW, liste):
    print(f'\nstarting main.create_KW_Message for KW: {jahr_KW}\n')
    channel = client.get_channel(MATCHES_AND_RESULTS)

    # read entry "kw_liste" which contains a list of all existing weekly messages
    try:
        kw_liste = result_list.read_dictionary("kw_liste")
    except KeyError:
        kw_liste = []
    # create new liste if it didnt exist before

    index = 0
    for x in kw_liste:
        if x < jahr_KW:
            index += 1
    # find at which index I need to insert the message, am I stupid? is there no easier way to do this?

    kw_liste.insert(index, jahr_KW)
    result_list.update_dictionary("kw_liste", kw_liste)

    # message wird geschrieben als platzhalter
    message = await channel.send(content=f"**{jahr_KW}:**")
    message_ID = message.id
    result_list.update_dictionary(jahr_KW, message_ID)
    # creating a new KW message we add it to the list

    # delete and rewrite all following weekly messages to restore order
    for item in range(index + 1, len(kw_liste)):
        await rewrite_KW(kw_liste[item], channel, liste)
    print(f'finished main.create_KW_Message for KW: {jahr_KW}\n')
    return message_ID

async def rewrite_KW(item, channel, liste):
    old_message_id = result_list.read_dictionary(item)
    old_kw_message = await channel.fetch_message(old_message_id)
    await old_kw_message.delete()

    # New Placeholder message
    new_kw_message = await channel.send(f"**{item}:**")  
    
    # enter new Message_id into dict
    result_list.update_dictionary(item, new_kw_message.id)

    await update_kw_message(item, liste)  # message gets properly written here

client.run(token)