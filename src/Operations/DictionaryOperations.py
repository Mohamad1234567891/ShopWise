def GetListOfVluesOfAKeyFromDictionaryList(key, list):
    "Takes a key and a list of dictionaries and outputs a list of all values of that key from all the dictionaries combined."
    output = []

    for el in list:
        for k in el:
            if k == key:
                output.append(el[k])

    return output