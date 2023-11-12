# Discord-Bot
## What to do?  
    change picklejson to json, enabled by change to result dicts -> no packages other than discord.py needed

## Clean ups?:
    1. remove format time function from main -> maybe to result_object
    2. check all kinds of edge cases
    
## Want to do:
    1. Input möglich von verschiedenen channels aus
    2. Verschiedene Channels -> Game wird in result gespeichert und message wird nach games getrennt -> Gruppiert erst nach games und sortiert erst dann die Gruppen nach Zeit

## OPTIONAL Features:
    1. Markiert matches die aktuell laufen
    2. Bot notified result author wenn ein Match termin rum ist und kein Result eingetragen wurde
    3. Automated ?Yearly/Monthly/Weekly? reports on amount of matches played and other stats etc.
    4. Bessere möglichkeit um result zu editen? User replied auf messsage oder ähnliches? Hab bisher nichts gefunden
    5. Zuweisung von Team zum result nach team rolle? -> schwierig für doppelte team zugehörigkeit, viel hard coding
    6. Gruppierung nach Liga? -> String matching schwierig weil user oft gleiche liga unterschiedlich schreiben -> jeder typo wird zu eigenem Absatz

## ERRORS THAT CAN HAPPEN:
    1. deleting a bot message manually somewhere can desync data the bot has and whats actually on the server 
        -> No idea how to solve if files were json files, admin could go into files and restore sync manually
        maybe let bot delete all data in corresponding file if he cant find message anymore

## Done:
    1. how to manage all KW messages after edit and deletes, keep them all in order.
        - 1 message per week
        - add a new KW in between existing KWs, we would have to delete all newer KWs and rewrite

        -> when a new KW is created, also create all missing elements in between? No
        -> Update all elements after the one we added?    for weekly messages this would mean deleting and readding or keeping empty messages
    
    2. Edge case: clear a list of all entries, what happens? -> need to delete list and corresponding kw message
    3. changed result objects to result dictionaries for easier json handling
