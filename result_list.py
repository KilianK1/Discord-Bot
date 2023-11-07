import result_object
import pickle
import os.path
import jsonpickle


# in the pickle file I always store a list of results
# when adding a result I first read the list, add the result to the list and then save the new list


def add(result: result_object.result):
    print("executing result_list.add")
    jahr_kalenderWoche = result.date.strftime("%y_%W")

    try:
        res_list = read(jahr_kalenderWoche)
    except:
        print(f"couldnt read file: {jahr_kalenderWoche}")
        res_list = []  # file doesnt exist so we create a new list

    res_list.append(result)
    write(res_list, jahr_kalenderWoche)
    # write new list with added result to file

    res_list.sort(key=lambda x: x.date)  # compare list items by date and sort them
    print(f"result list for {jahr_kalenderWoche}:")
    for r in res_list:
        print(r.toString())

    # these are the things we do to keep everything synced up after a change
    update_dictionary(result.id, jahr_kalenderWoche)
    write(res_list, jahr_kalenderWoche)


def edit(message_id: str, result_edit: result_object.result, uhrzeit, datum):
    print("executing result_list.edit")
    kw = read_dictionary(message_id)
    liste = read(kw)

    for r in liste:
        if r.id == message_id:
            print(r.toString())
            result = r
    result.update(result_edit, uhrzeit, datum)

    # these are the things we do to keep everything synced up after a change
    print(f"result should now be edited: {result.toString()}")
    delete(message_id)  # einmal löschen und neu adden falls KW sich geändert hat
    add(result)
    return result


def delete(message_id: str):
    print("executing result_list.delete")
    kw = read_dictionary(message_id)
    liste = read(kw)

    for r in list(liste):  # iterate over copy so I can delete element
        if r.id == message_id:
            liste.remove(r)
    write(liste, kw)
    return kw


def update_dictionary(key, value):
    print(f"executing update_dictionary(key: {key}, value: {value})")
    try:
        dictionary = read("dictionary")  # open file and return dictionary
    except IOError:
        if not os.path.exists("gurken\\dictionary"):
            new_dictionary = {}  # creating a dictionary because it didnt exist yet
            write(new_dictionary, "gurken\\dictionary")
            dictionary = new_dictionary
        else:
            raise IOError(
                "Pickle file couldnt be opened. It seems to exist but it couldnt be opened"
            )
    dictionary[key] = value
    try:
        write(dictionary, "dictionary")
    except:
        print("Error during pickling object (Possibly unsupported):")


# dictionary saves for all "KWs" a corresponding message id
# dictionary also contains for all message_ids of individual results the corresponding kw
def read_dictionary(KW_or_ID):
    print(f"read_dictionary at key: {KW_or_ID}")
    try:
        dictionary = read("dictionary")  # open file and return dict
    except IOError:
        print(f"file dictionary.pickle didnt exist yet")
        if not os.path.isfile("gurken\\dictionary"): #TODO not good because not platform independetn
            new_dictionary = {}  # creating a dictionary because it didnt exist yet
            write(new_dictionary, "dictionary")
        else:
            raise IOError("Pickle file seems to exist but it couldnt be opened")
    try:
        id_or_kw_return = dictionary[KW_or_ID]
    except KeyError:
        print(f"Key {KW_or_ID} is not yet in Dictionary")
        raise KeyError()
    return id_or_kw_return


def read(file_name: str):
    path = os.path.join('gurken', file_name + '.json')
    print(f" result_list.read gurken\{file_name}.pickle")
    try:
        file = open(path, "r")
        json_str = file.readline()
        # open file and return whats inside
        return jsonpickle.decode(json_str, keys=True)
    except IOError:
        print(f"file gurken\{file_name}.pickle does not exist yet")
        raise IOError(
            "Pickle file couldnt be opened. This usually means it doesnt exist"
        )


def write(pickle_data, file_name: str):
    path = os.path.join('gurken', file_name + '.json')
    json_str = jsonpickle.encode(pickle_data, keys=True)
    print(f"writing to gurken\{file_name}.pickle")
    try:
        file = open(path, "w")
        file.write(json_str)
    except:
        print("Error during pickling object (Possibly unsupported):")


# def readFile(file, KW: str):   #opens or creates file for corresponding KW
