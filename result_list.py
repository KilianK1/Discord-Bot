import result_object
import pickle
import os.path

# in the pickle file I always store a list of results
# when adding a result I first read the list, add the result to the list and then save the new list


def add(result: result_object.result):
    print("executing result_list.add")
    jahr_kalenderWoche = result.date.strftime("%y_%W")

    try:
        res_list = read(jahr_kalenderWoche)
        print("did read file")
    except:
        print("couldnt read file")
        res_list = []  # file doesnt exist so we create a new list

    res_list.append(result)

      # write new list with added result to file

    res_list.sort(key=lambda x: x.date)  # compare list items by date and sort them
    print("after sorting result list:")
    for r in res_list:
        print(r.toString())

    update_dictionary(result.id, jahr_kalenderWoche)

    write(res_list, jahr_kalenderWoche)
    # TODO update or create weekly message in matches and results, also needs to be done for edit and delete


def update_dictionary(key, value):
    print("executing result_list.update_dictionary")
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


def edit(message_id: str, result_edit: result_object.result, uhrzeit, datum):
    print("executing result_list.edit")
    kw = read_dictionary(message_id)
    liste = read(kw)

    for r in liste:
        if r.id == message_id:
            print(r.toString())
            result = r
    result.update(result_edit, uhrzeit, datum)

    print(f"result should now be edited: {result.toString()}")
    delete(message_id)  # einmal löschen und neu adden falls KW sich geändert hat
    add(result)

    return result


def delete(message_id: str):
    print("executing result_list.delete")
    kw = read_dictionary(message_id)
    liste = read(kw)

    # for i in range(len(liste) - 1, -1, -1):
    #     if liste[i].id == message_id:
    #         del liste[i]

    for r in list(liste):  # iterate over copy so I can delete element
        if r.id == message_id:
            liste.remove(r)
    write(liste, kw)


def read_dictionary(KW_or_ID):
    print(f"read_dictionary {KW_or_ID}")
    try:
        dictionary = read("dictionary")  # open file and return list
        id_or_kw_return = dictionary[KW_or_ID]
        return id_or_kw_return
    except IOError:
        print(f"file dictionary.pickle didnt exist yet")
        if not os.path.isfile("gurken\\dictionary"):
            new_dictionary = {}  # creating a dictionary because it didnt exist yet
            write(new_dictionary, "gurken\\dictionary")
        else:
            raise IOError(
                "Pickle file couldnt be opened. It seems to exist but it couldnt be opened"
            )


def read(file_name: str):
    print(f" result_list.read gurken\{file_name}.pickle")
    try:
        pickle_data = pickle.load(
            open(f"gurken\\{file_name}.pickle", "rb")
        )  # open file and return whats inside
        return pickle_data
    except IOError:
        print(f"file gurken\{file_name}.pickle does not exist yet")
        raise IOError(
            "Pickle file couldnt be opened. This usually means it doesnt exist"
        )


def write(pickle_data, file_name: str):
    print(f"trying to write to gurken\{file_name}.pickle")
    try:
        pickle.dump(pickle_data, open(f"gurken\\{file_name}.pickle", "wb"))
    except:
        print("Error during pickling object (Possibly unsupported):")


# def readFile(file, KW: str):   #opens or creates file for corresponding KW
