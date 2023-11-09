from datetime import datetime


class result:
    def __init__(
        self,
        mein_team: str,
        gegner_team: str,
        datum: datetime,
        liga: str,
        ergebnis: str,
        format: str,
        message_id: str,
    ):
        self.me = mein_team
        self.enemy = gegner_team
        self.league = liga
        self.date = datum
        self.result = ergebnis
        self.form = format
        self.id = message_id

    def toString(self):
        datestring = self.date.strftime(
            "%a, %d.%m.%y, %H:%M Uhr"
        )  # datetime to string format
        text = f"## {self.league}\n**{datestring}**: {self.me} {self.result} {self.enemy}  {self.form}"
        return text


    # this will be needed for formatting of weekly messages, whenever i feel like doing that
    # def toKWString(self):
    #     datestring = self.date.strftime(
    #         "%a, %d.%m.%y, %H:%M Uhr"
    #     )  # datetime to string format
    #     text = f"**{self.league}, {datestring}:** {self.me} {self.result} {self.enemy}  {self.form}" 
    #     return text

    def update(self, result_edit: "result", uhrzeit, datum):
        if result_edit.me != "-1":
            self.me = result_edit.me
        if result_edit.enemy != "-1":
            self.enemy = result_edit.enemy
        if result_edit.league != "-1":
            self.league = result_edit.league
        if uhrzeit != "-1":
            zeit_parse = datetime.strptime(uhrzeit, "%H:%M")
            self.date = self.date.combine(self.date.date(), zeit_parse.time())
        if datum != "-1":
            zeit_parse = datetime.strptime(datum, "%d.%m.%y")
            self.date = self.date.combine(zeit_parse.date(), self.date.time())
        if result_edit.result != "-1":
            self.result = result_edit.result
        if result_edit.form != "-1":
            self.form = result_edit.form
