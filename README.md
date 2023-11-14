# Discord-Bot
## How to use Bot
1. for running the bot you only need the required Python version and the required Discord.py
2. Commands are "/add_result", "/edit" and "/delete"
3. "/add_result" formats the user input it gets and creates and saves a result, user can see the result in the channel he executed the command in. Result gets grouped with other results by week and game(determined by input channel) and posted to matches-and-results channel
4. "/edit" allows user to edit a result by using the message_id of the result as the identifier, automatically syncs all instances of result(save files, result message, weekly message)
5. "/delete" works same as /edit but removes the result from all instances
6. Results are saved in backend using json in weekly files to avoid bloated file sizes after long time usage

## Development status

### Current
1. Trying to figure out how to schedule tasks for specific time(for OPT features 2. & 3.)


### Clean ups:
1. check all kinds of edge cases
    
### Want to do:
1. Games are currently in order of their eaerliest game per week -> fix order for games? or does this not matter?
2. add game emojis to weekly message, make weekly message look nice in general
3. Gruppierung nach Liga? -> ausprobieren i guess
4. Can Bot be configured so it only reacts to messages in certain channels?

### OPTIONAL Features:

1. Gruppierung nach Liga? -> String matching schwierig weil user oft gleiche liga unterschiedlich schreiben -> jeder typo wird zu eigenem Absatz
2. Markiert matches die aktuell laufen
3. Bot notified result author wenn ein Match termin rum ist und kein Result eingetragen wurde
4. Automated ?Yearly/Monthly/Weekly? reports on amount of matches played and other stats etc.
5. Bessere möglichkeit um result zu editen? User replied auf messsage oder ähnliches? Hab bisher nichts gefunden
6. Zuweisung von Team zum result nach team rolle? -> schwierig für doppelte team zugehörigkeit, viel hard coding
7. Add link to streams in result, could be used for automated match posts?

Can you see who edited and deleted results? -> maybe through some discord logs -> trolling is possible?

### ERRORS THAT CAN HAPPEN:
1. deleting a bot message manually somewhere can desync data the bot has and whats actually on the server
       -> No idea how to solve if files were json files, admin could go into files and restore sync manually
       maybe let bot delete all data in corresponding file if he cant find message anymore

### Done:
1. how to manage all KW messages after edit and deletes, keep them all in order.
    - 1 message per week
    - add a new KW in between existing KWs, we would have to delete all newer KWs and rewrite
    -> when a new KW is created, also create all missing elements in between? No
    -> Update all elements after the one we added?    for weekly messages this would mean **deleting and readding** (or keeping empty messages)
2. Edge case: clear a list of all entries, what happens? -> need to delete list and corresponding kw message
3. changed result objects to result dictionaries for easier json handling
4. change picklejson to json, enabled by change to result dicts -> no packages other than discord.py needed
5. remove format time function from main -> to result_list
6. Input möglich von verschiedenen channels aus
7. Verschiedene Channels -> Game wird in result gespeichert und message wird nach games getrennt -> Gruppiert nach games sortierung nach zeit war davor schon gegeben und wird beibehalten