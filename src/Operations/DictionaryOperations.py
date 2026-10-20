"""
This file is part of ShopWise, an open-source multi-region, multi-store
price-comparison and product-search engine.

Copyright (c) 2026 Muhammed Bekiroğlu and the ShopWise contributors.

Original ShopWise repository: https://github.com/Mohamad1234567891/ShopWise

Muhammed Bekiroğlu (ShopWise team leader and top contributor) YouTube channel:
    https://www.youtube.com/@ALShajaraComputerScienceInstit

Licensed under the Mozilla Public License 2.0 with Additional Attribution
Terms — see the LICENSE file.
-------------------------------------------------------------------------------------------------------------------------------

Small dictionary helpers used by the extraction pipeline. GetListOfVluesOfAKeyFromDictionaryList collects every value of a given key from a list of dictionaries.
"""

def GetListOfVluesOfAKeyFromDictionaryList(key, list):
    "Takes a key and a list of dictionaries and outputs a list of all values of that key from all the dictionaries combined."
    output = []

    for el in list:
        for k in el:
            if k == key:
                output.append(el[k])

    return output