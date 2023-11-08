import result_object
import pickle
import os.path
import jsonpickle


# in the pickle file I always store a list of results
# when adding a result I first read the list, add the result to the list and then save the new list


def add(result: result_object.result):
    print("\nexecuting result_list.add")
    jahr_kalenderWoche = result.date.strftime("%y_%W")

    try:
        res_list = read(jahr_kalenderWoche)
    except:
        res_list = []  # file doesnt exist so we create a new list

    res_list.append(result)

    res_list.sort(key=lambda x: x.date)  # compare list items by date and sort them
    print(f"result list for {jahr_kalenderWoche}:")
    for r in res_list:
        print(r.toString())

    # these are the things we do to keep everything synced up after a change
    update_dictionary(result.id, jahr_kalenderWoche)
    write(res_list, jahr_kalenderWoche)
    print('finished result_list.add\n')


def edit(message_id: str, result_edit: result_object.result, uhrzeit, datum, kw: str):
    print("\nexecuting result_list.edit")
    liste = read(kw)

    for r in liste:
        if r.id == message_id:
            print(r.toString())
            result = r
            break
    result.update(result_edit, uhrzeit, datum)
    new_kw = result.date.strftime("%y_%W")
    # these are the things we do to keep everything synced up after a change
    print(f"result should now be edited: {result.toString()}")

    #check if kw is changed 
    if(kw != new_kw):
        delete(message_id)  # einmal löschen und neu adden wenn KW sich geändert hat
        add(result)
    return result


def delete(message_id: str):
    print("\nexecuting result_list.delete")
    kw = read_dictionary(message_id)
    liste = read(kw)

    for r in list(liste):  # iterate over copy so I can delete element
        if r.id == message_id:
            liste.remove(r)
    write(liste, kw)
    delete_from_dictionary(message_id)
    return kw


def delete_from_dictionary(key):
    print(f"executing delete_from_dictionary(key: {key}")
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
        create_dictionary()
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


# def readFile(file, KW: str):   #opens or creates file for corresponding KW
