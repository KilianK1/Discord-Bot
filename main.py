from datetime import datetime
import locale
import discord
from discord import app_commands
import json
import result_module
import result_list


# Get configuration.json
with open("configuration.json", "r") as config: 
	data = json.load(config)
	token = data["token"]

locale.setlocale(locale.LC_ALL, 'de_DE')

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
    mein_team ='Der Name deines Teams',
    gegner_team='Der Name des Gegner Teams',
    datum = 'Datum des Matches, Format: DD.MM.YY',
    uhrzeit = 'Uhrzeit des Matches',
    ergebnis = 'Ergebnis des Matches, leer lassen wenn noch nicht gespielt wurde',
    liga = 'Liga in der das Match stattfindet',
    format = 'BO1, BO2, etc. oder leer lassen'
)
async def add_result(interaction: discord.Interaction, mein_team: str, gegner_team: str, datum: str, liga: str, uhrzeit: str, ergebnis: str = '0 - 0', format: str = ""):
    
    mein_team.strip()
    gegner_team.strip()
    liga.strip()
    ergebnis.strip()
    format.strip() #es schleichen sich schnell führende und endende leerzeichen in userinput -> strip removed diese

    await interaction.response.send_message('Bot ist am Arbeiten...') # wird ausgeführt, damit man message_id bekommen kann
    
    antwort = await interaction.original_response()     #Nachricht, die ich gerade gesendet habe
    message = await antwort.fetch()                     #message transformiert, so dass ich id rausfinden kann
    message_id = message.id

    try:
        date_format = zeit_format(datum = datum, zeit = uhrzeit) #format
    except:
         message.edit('Format von Zeit oder Datum war nicht richtig, bitte versuche es erneut', delete_after= 30)
         return

    
    res = result_module.result(mein_team, gegner_team, date_format, liga, ergebnis, format, message_id) #erstelle result objekt
    await message.edit(content= res.toString() + f"\nNutze diese Message_ID zum löschen oder bearbeiten deines Ergebnisses: {message_id}")  #proper format
    
    result_list.add(res)
	

@client.tree.command()
@app_commands.describe(
    message_id = 'Die ID der Nachricht die du bearbeiten willst',
    mein_team ='Der Name deines Teams',
    gegner_team = 'Der Name des Gegner Teams',
    datum = 'Datum des Matches, Format: DD.MM.YY',
    uhrzeit = 'Uhrzeit des Matches',
    ergebnis = 'Ergebnis des Matches, leer lassen wenn noch nicht gespielt wurde',
    liga = 'Liga in der das Match stattfindet',
    format = 'BO1, BO2, etc. oder leer lassen'
)
async def edit_result(interaction: discord.Interaction, message_id: str, mein_team: str = '-1', gegner_team: str = '-1', datum: str = '-1', liga: str = '-1', uhrzeit: str = '-1', ergebnis: str = '-1', format: str = '-1'):
    result_list.edit(message_id, mein_team, gegner_team, datum, liga, uhrzeit, ergebnis, format)


def zeit_format(datum: str, zeit: str):
        #parse input values to datetime objects according to format given in strptime
        try:
            zeit_parse = datetime.strptime(zeit, "%H:%M")       #%H:%M    accepts time in format 'HH:MM' with H = 0-23 and M = 0-59
        except ValueError:
            raise Exception('Invalid time given')
        try:
            datum_parse = datetime.strptime(datum, "%d.%m.%y")      #accepts date in format 'DD.MM.YY'
        except ValueError:
            raise Exception('Invalid date given')

        try:
            print(f"{zeit} = zeit\n{zeit_parse.hour}:{zeit_parse.minute}  = zeit_parse\n{datum}  = datum\n{datum_parse.day}.{datum_parse.month}.{datum_parse.year}  = datum parse")
            
            Date_final = datetime.combine(datum_parse.date(), zeit_parse.time())    #combine date and time into a single object
            
            print(Date_final)

        except NameError:
            raise Exception('Could not format date')


        return(Date_final)

client.run(token)