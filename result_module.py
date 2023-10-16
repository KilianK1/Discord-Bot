from datetime import datetime


class result:
    
    def __init__(self, mein_team: str, gegner_team: str, datum: datetime, liga: str, ergebnis: str, format: str, message_id: str):
        self.me = mein_team
        self.enemy = gegner_team
        self.league = liga
        self.date = datum
        self.result = ergebnis
        self.form = format
        self.id = message_id

    def toString(self):
        datestring = self.date.strftime('%a, %d.%m.%y, %H:%M Uhr') #datetime to string format
        text = f'__**{self.league}**__\n**{datestring}:** {self.me} {self.result} {self.enemy}'
        return text
    