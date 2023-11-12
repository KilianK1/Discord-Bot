import os.path
import jsonpickle
from datetime import datetime


# in the pickle file I always store a list of results
# when adding a result I first read the list, add the result to the list and then save the new list


def add(result: dict):
    print("\nexecuting result_list.add")
    jahr_kw = datetime.fromisoformat(result["datetime"]).strftime("%y_%W")
    
    try:
        res_list = read(jahr_kw)
    except:
        res_list = []  # file doesnt exist so we create a new list

    res_list.append(result)

    res_list.sort(key=lambda x: x["datetime"])  # compare list items by date and sort them
    print(f"result list for {jahr_kw}:")
    for r in res_list:
        print(str(r))

    # these are the things we do to keep everything synced up after a change
    update_dictionary(result["message_id"], jahr_kw)
    write(res_list, jahr_kw)
    print('finished result_list.add\n')
    return res_list, jahr_kw


def edit(result_edit: dict):
    print("\nexecuting result_list.edit")
    old_kw = read_dictionary(result_edit["message_id"])
    liste = read(old_kw)
    
    index = 0
    #find old result
    for result in liste:
        index += 1
        if result["message_id"] == result_edit["message_id"]:
            new_result = update_result(result, result_edit)
            break

    new_kw = datetime.fromisoformat(new_result["datetime"]).strftime("%y_%W")
    print(f"result should now be edited: {str(new_result)}")

    old_kw, liste_minus_element = delete(new_result["message_id"])  # einmal löschen und neu adden wenn KW sich geändert hat
    new_liste, new_jahr_kw = add(new_result)
    
    print('finished result_list.edit\n')
    return result, new_liste, new_jahr_kw, old_kw

def delete(message_id: str):
    print("\nexecuting result_list.delete")
    kw = read_dictionary(message_id)
    liste = read(kw)

    for r in list(liste):  # iterate over copy so I can delete element
        if r["message_id"] == message_id:
            liste.remove(r)
            break
    write(liste, kw)
    delete_from_dictionary(message_id)
    print("liste nach löschen:\n")
    print(liste)
    print('finished result_list.delete\n')
    return kw, liste

def update_result(result: dict, edit_result: dict):
    old_date = datetime.fromisoformat(result["datetime"])
    
    if (edit_result["date"] != "-1") and (edit_result["time"] != "-1"):
        new_datetime = datetime.strptime(edit_result["date"] + "." + edit_result["time"], "%d.%m.%y.%H:%M")
        result["datetime"] = new_datetime.isoformat()
        
    if (edit_result["date"] == "-1") and (edit_result["time"] != "-1"):
        new_time = datetime.strptime(edit_result["time"], "%H:%M")
        result["datetime"] = datetime.combine(old_date.date(), new_time.time()).isoformat()
        
    if (edit_result["date"] != "-1") and (edit_result["time"] == "-1"):
        new_date = datetime.strptime(edit_result["date"], "%d.%m.%y")
        result["datetime"] = datetime.combine(new_date.date(), old_date.time()).isoformat()
        

    edit_result.pop("date")
    edit_result.pop("time")

    for key in edit_result:
        if(edit_result[key] != "-1"):
            result[key] = edit_result[key]

    return result

def result_to_string(result: dict):
    datestring = datetime.fromisoformat(result["datetime"]).strftime(
            "%a, %d.%m.%y, %H:%M Uhr"
        )  # datetime to string format
    
    text = f"## {result['liga']}\n**{datestring}**: {result['mein_team']} {result['ergebnis']} {result['gegner_team']}  {result['format']}"
    return text


def delete_from_dictionary(key):
    print(f"executing delete_from_dictionary(key: {key})")
    try:
        dictionary = read("dictionary")
    except:
        raise IOError("Dictionary couldnt be opened")
    dictionary.pop(key) #removes from dictionary
    write(dictionary, "dictionary")
    

def update_dictionary(key, value):
    print(f"executing update_dictionary(key: {key}, value: {value})")
    try:
        dictionary = read("dictionary")  # open file and return dictionary
    except IOError:
        dictionary = create_dictionary()
    dictionary[key] = value
    sorted_dict = dict(sorted(dictionary.items()))
    write(sorted_dict, "dictionary")
    

# dictionary saves for all "KWs" a corresponding message id
# dictionary also contains for all message_ids of individual results the corresponding kw
def read_dictionary(KW_or_ID):
    print(f"read_dictionary at key: {KW_or_ID}")
    try:
        dictionary = read("dictionary")  # open file and return dict
    except IOError:
        dictionary = create_dictionary()
        
    try:
        id_or_kw_return = dictionary[KW_or_ID]
    except KeyError:
        print(f"Key {KW_or_ID} is not yet in Dictionary")
        raise KeyError()
    return id_or_kw_return

def create_dictionary():
    path = os.path.join('gurken', 'dictionary.json')
    print(f"file dictionary.json didnt exist yet")
    if not os.path.isfile(path):
        new_dictionary = {}  # creating a dictionary because it didnt exist yet
        write(new_dictionary, "dictionary")
        return new_dictionary
    else:
        raise IOError("json file seems to exist but it couldnt be opened")

def read(file_name: str):
    path = os.path.join('gurken', file_name + '.json')
    print(f" result_list.read gurken\{file_name}.json")
    try:
        file = open(path, "r")
        json_str = file.read()
        # open file and return whats inside
        return jsonpickle.decode(json_str, keys=True)
    except IOError:
        print(f"file gurken\{file_name}.json does not exist yet")
        raise IOError(
            "json file couldnt be opened. This usually means it doesnt exist"
        )

def write(pickle_data, file_name: str):
    path = os.path.join('gurken', file_name + '.json')
    json_str = jsonpickle.encode(pickle_data, keys=True, indent = 4)
    print(f"writing to gurken\{file_name}.json")
    try:
        file = open(path, "w")
        file.write(json_str)
    except:
        print("Error during pickling object (Possibly unsupported):")
