import result_object
import pickle
import datetime
import sqlite3


# in the pickle file I always store a list of results
# when adding a result I first read the list, add the result to the list and then save the new list


def add(result: result_object.result):
    jahr_kalenderWoche = result.date.strftime("%y_%W")

    try:
        res_list = read(jahr_kalenderWoche)
        print("did read file")
    except:
        print("couldnt read file")
        res_list = []  # file doesnt exist so we create a new list

    # print("\nbefore adding new result:")
    # if res_list:
    #     for r in res_list:
    #         print(r.toString())
    # else:
    #     print("res_list is empty")
    res_list.append(result)

    # print("\nafter adding new result:")
    # if res_list:
    #     for r in res_list:
    #         print(r.toString())
    # else:
    #     print("res_list is empty")

    write(res_list, jahr_kalenderWoche)  # write new list with added result to file

    res_list.sort(key=lambda x: x.date)  # compare list items by date and sort them
    print("after sorting result list:")
    for r in res_list:
        print(r.toString())

    update_dictionary(result.id, jahr_kalenderWoche)
    # TODO update or create weekly message in matches and results, also needs to be done for edit and delete


def update_dictionary(key, value):
    
    try:
        dictionary = read("dictionary")  # open file and return dictionary
    except IOError:
        raise IOError(
            "Pickle file couldnt be opened. This usually means it doesnt exist"
        )
    dictionary[key] =  value
    try:
        write(dictionary, "dictionary")
    except:
        print("Error during pickling object (Possibly unsupported):")

def edit(message_id: str, result_edit: result_object.result, uhrzeit, datum): #or maybe pass entire result object? where do I filter which attributes need to be changed?
    
    kw = read_dictionary(message_id)
    liste = read(kw)

    for r in liste:
        if (r.id == message_id):
            result = r
    
    
    result.update(result_edit, uhrzeit, datum) #check which values need to be changed and edit
    return result


# def delete(message_id: str) how do i find the calendar week and the corresponding file without having the datetime object? i dont -> I need to save it in an additional file


def read_dictionary(KW_or_ID):
    try:
        dictionary = read("dictionary")  # open file and return list
        print(dictionary)
        id_or_kw_return = dictionary[KW_or_ID]
        return id_or_kw_return
    except IOError:
        print(f"file dictionary.pickle does not exist yet")
        raise IOError(
            "Pickle file couldnt be opened. This usually means it doesnt exist"
        )


def read(file_name: str):
    print(f"trying to read {file_name}.pickle")
    try:
        pickle_data = pickle.load(
            open(f"{file_name}.pickle", "rb")
        )  # open file and return whats inside
        return pickle_data
    except IOError:
        print(f"file {file_name}.pickle does not exist yet")
        raise IOError(
            "Pickle file couldnt be opened. This usually means it doesnt exist"
        )


def write(pickle_data, file_name: str):
    try:
        pickle.dump(pickle_data, open(f"{file_name}.pickle", "wb"))
    except:
        print("Error during pickling object (Possibly unsupported):")


# def readFile(file, KW: str):   #opens or creates file for corresponding KW
