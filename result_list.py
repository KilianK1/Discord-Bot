import result_module
import pickle
import datetime
import sqlite3



#maybe pickle

#in the pickle file I always store a list of results
#when adding a result I first read the list, add the result to the list and then save the new list



def add(result: result_module.result):

    jahr_kalenderWoche = result.date.strftime('%y_%W')
    
    try:
        res_list = read(result, jahr_kalenderWoche)
        print('did read file')
    except:
        print('couldnt read file')
        res_list = [] #file doesnt exist so we create a new list
    
    
    print('\nbefore adding new result:')
    if res_list:
        for r in res_list:
            print(r.toString())
    else:
        print('res_list is empty')
    res_list.append(result)
    
    print('\nafter adding new result:')
    if res_list:
        for r in res_list:
            print(r.toString())
    else:
        print('res_list is empty')
    

    write(res_list, jahr_kalenderWoche) #write new list with added result to file


    res_list.sort(key = lambda x: x.date) #compare list items by date and sort them
    print('after sorting result list:')
    for r in res_list:
        print(r.toString())

    #TODO update or create weekly message in matches and results, also needs to be done for edit and delete


#def edit(message_id: str) or maybe pass entire result object? where do I filter which attributes need to be changed?

#def delete(message_id: str) how do i find the calendar week and the corresponding file without having the datetime object? i dont -> I need to parse the message from discord to figure out where I saved it

def read(result: result_module.result, jahr_kalenderWoche:str):         #read file and append new element to list
    jahr_kalenderWoche = result.date.strftime('%y_%W')
    print(f'trying to read {jahr_kalenderWoche}.pickle')
    res_list = []
    try:
        res_list = pickle.load(open(f"{jahr_kalenderWoche}.pickle", "rb")) #open file and return list
        return res_list
    except IOError:
        print(f"file {jahr_kalenderWoche}.pickle does not exist yet")
        raise IOError('Pickle file couldnt be opened. This usually means it doesnt exist')

def write(res_list, jahr_kalenderWoche: str):
    
    try:
        pickle.dump(res_list, open( f"{jahr_kalenderWoche}.pickle", "wb" ))
    except:
        print("Error during pickling object (Possibly unsupported):")

# def readFile(file, KW: str):   #opens or creates file for corresponding KW