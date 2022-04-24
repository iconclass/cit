import json


def CIT_A(obj_json, cit_list):
    obj = json.loads(obj_json)
    cit1 = set(cit_list.split(" "))
    cit2 = set(obj.get("CIT_ID", []))
    if cit1 <= cit2:
        return True


def CIT_O(obj_json, cit_list):
    obj = json.loads(obj_json)
    cit2 = set(obj.get("CIT_ID", []))
    for cit in set(cit_list.split(" ")):
        if cit in cit2:
            return True


def CIT_N(obj_json, cit_list):
    obj = json.loads(obj_json)
    cit2 = set(obj.get("CIT_ID", []))
    for cit in set(cit_list.split(" ")):
        if cit in cit2:
            return False
    return True
