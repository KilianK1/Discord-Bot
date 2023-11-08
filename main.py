from datetime import datetime
import locale
import discord
from discord import app_commands
import json
import result_object
import result_list


# Get configuration.json
with open("configuration.json", "r") as config:
    data = json.load(config)
    token = data["token"]

locale.setlocale(locale.LC_ALL, "de_DE")
MATCHES_AND_RESULTS = (
    1163162296588185640  # TODO Hardcode matches and results channel-ID here
)
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

    mein_team.strip()
    gegner_team.strip()
    liga.strip()
    ergebnis.strip()
    format.strip()
    uhrzeit.strip()
    datum.strip()  # es schleichen sich schnell führende und endende leerzeichen in userinput -> strip removed diese

    await interaction.response.send_message(
        "Bot ist am Arbeiten..."
    )  # wird ausgeführt, damit man message_id bekommen kann

    antwort = (
        await interaction.original_response()
    )  # Nachricht, die ich gerade gesendet habe
    message = (
        await antwort.fetch()
    )  # message transformiert, so dass ich id rausfinden kann
    message_id = str(message.id)

    try:
        date_format = zeit_format(datum=datum, zeit=uhrzeit)  # format
    except:
        await message.edit(
            content="Format von Zeit oder Datum war nicht richtig, bitte versuche es erneut",
            delete_after=30,
        )
        return

    res = result_object.result(
        mein_team, gegner_team, date_format, liga, ergebnis, format, message_id
    )  # erstelle result objekt
    try:
        result_list.add(res)
    except:
        await message.edit(content="Something went wrong", delete_after=30)
        raise IOError("Somethin went wrong while adding the result")
        # proper format
    await message.edit(
        content=res.toString()
        + f"\nNutze diese Message_ID zum löschen oder bearbeiten deines Ergebnisses: {message_id}"
    )  # proper format
    jahr_kalenderWoche = res.date.strftime("%y_%W")
    # here we update the KW messages
    await update_kw_message(jahr_kalenderWoche)


@client.tree.command(
    name="edit",
    description="Nutze die Message_ID zum editen, leere Felder = nichts ändern",
)
@app_commands.describe(
    message_id="Die ID der Nachricht die du bearbeiten willst",
    mein_team="Der Name deines Teams",
    gegner_team="Der Name des Gegner Teams",
    datum="Datum des Matches, Format: DD.MM.YY",
    uhrzeit="Uhrzeit des Matches",
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

    message_id.strip
    mein_team.strip()
    gegner_team.strip()
    liga.strip()
    ergebnis.strip()
    format.strip()
    uhrzeit.strip()
    datum.strip()
    try:
        message = await interaction.channel.fetch_message(message_id)
    except:
        await interaction.response.send_message(
            "Etwas ist schiefgelaufen, überprüfe ob deine Messagge_ID stimmt",
            delete_after=30,
        )
        return

    if datum != "-1":
        date = zeit_format(
            datum, "00:00"
        )  # überprüfe format von datum und uhrzeit unabhängig voneinander
    if (
        uhrzeit != "-1"
    ):  # erstelle datetime objekt, welches die relevante veränderung enthält. damit später combine ausgeführt werden kann
        date = zeit_format("01.01.23", uhrzeit)
    else:
        date = zeit_format("01.01.23", "00:00")

    res = result_object.result(
        mein_team,
        gegner_team,
        date,
        liga,
        ergebnis,
        format,
        message_id,
    )
    # find in which KW message was before edit
    old_jahrKW = result_list.read_dictionary(message_id)

    try:
        res = result_list.edit(
            message_id, res, uhrzeit, datum, old_jahrKW
        )  # uhrzeit und datum angefügt, zum überprüfen welche values übernommen werden sollen
    except:
        await interaction.response.send_message(
            content="Something went wrong", delete_after=30
        )
        raise IOError("Somethin went wrong while editing the result")

    await message.edit(
        content=res.toString()
        + f"\nNutze diese Message_ID zum löschen oder bearbeiten deines Ergebnisses: {message_id}"
    )
    await interaction.response.send_message(
        "Dein Ergebnis wurde bearbeitet",
        delete_after=30,
    )
    # Which kw is message in after editing
    jahr_kalenderWoche = res.date.strftime("%y_%W")

    # here we update the KW messages
    await update_kw_message(jahr_kalenderWoche)

    if jahr_kalenderWoche != old_jahrKW:
        # if KW was changed during edit we need to update both messages
        await update_kw_message(old_jahrKW)


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

    await message.delete()
    try:
        kw = result_list.delete(message_id)
    except:
        await interaction.response.send_message(
            content="Something went wrong", delete_after=30
        )
        raise IOError("Somethin went wrong while deleting the result")

    await interaction.response.send_message(
        content="Nachricht wurde gelöscht", delete_after=30
    )
    await update_kw_message(kw)


async def update_kw_message(jahr_KW):
    print(f'starting main.update_KW_Message for KW: {jahr_KW}\n')
    liste = result_list.read(jahr_KW)

    if not liste: #liste ist leer
        #delete file with list?  maybe dont do that
        #delete message!
        #delete dict entry for message! done
        #delete from kw_liste in dict! done
        id = result_list.read_dictionary(jahr_KW)
        result_list.delete_from_dictionary(id)
        kw_liste = result_list.read_dictionary("kw_liste")
        kw_liste.remove(jahr_KW) #TODO


    channel = client.get_channel(MATCHES_AND_RESULTS)
    # need to get all results from this week -> read corresponding file

    # Do I need a new message or does it exist? create it if doesnt exist
    try:
        message_ID = result_list.read_dictionary(jahr_KW)  # message_id finden
    except KeyError:
        message_ID = await create_kw_message(jahr_KW)

    try:
        message = await channel.fetch_message(message_ID)
    except:
        await channel.send_message(
            "Etwas ist schiefgelaufen, KW Messagge wurde nicht gefunden",
            delete_after=30,
        )
        return

    new_text = f"-----------------------------\n**KW {jahr_KW}:**\n\n"  # # ist für Header        TODO kann man hier nach Spiel sortieren?
    for x in liste:
        new_text += (
            x.toString() + "\n"
        )  # für jedes element in liste wird der string angehängt + newline
        # durch .toKWString ersetzen wenn anderes format gewünscht

    await message.edit(content=new_text)
    print(f'finished main.update_KW_Message for KW: {jahr_KW}\n')


async def create_kw_message(jahr_KW):
    print(f'starting main.create_KW_Message for KW: {jahr_KW}\n')
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
    for x in range(index + 1, len(kw_liste)):
        old_message_id = result_list.read_dictionary(kw_liste[x])
        old_kw_message = await channel.fetch_message(old_message_id)
        await old_kw_message.delete()
        new_kw_message = await channel.send(
            f"**{kw_liste[x]}:**"
        )  # New Placeholder message
        result_list.update_dictionary(
            kw_liste[x], new_kw_message.id
        )  # enter new Message_id into dict
        await update_kw_message(kw_liste[x])  # message gets properly written here
    print(f'finished main.create_KW_Message for KW: {jahr_KW}\n')
    return message_ID


def zeit_format(datum: str, zeit: str):
    # parse input values to datetime objects according to format given in strptime
    try:
        zeit_parse = datetime.strptime(
            zeit, "%H:%M"
        )  # %H:%M    accepts time in format 'HH:MM' with H = 0-23 and M = 0-59
    except ValueError:
        raise Exception("Invalid time given")
    try:
        datum_parse = datetime.strptime(
            datum, "%d.%m.%y"
        )  # accepts date in format 'DD.MM.YY'
    except ValueError:
        raise Exception("Invalid date given")

    try:
        Date_final = datetime.combine(
            datum_parse.date(), zeit_parse.time()
        )  # combine date and time into a single object

    except NameError:
        raise Exception("Could not format date")

    return Date_final


client.run(token)
