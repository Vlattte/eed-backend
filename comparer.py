import getInstruction
import json

def GetInstruction(app, step_id): #app - аппаратура, step_id - номер шага
    instr_file = open("test.json")
    data = json.load(instr_file)

    for i in range(len(data)):
        if data["step_"+str(i)]["step"]:
            return data["step_"+str(i)]

#[["session_id","1gjolm7fq"],["id",1015],["draggble",false],["rotatable",true],["currentValue",60],["left",249.99999999999997],["top",105.55555555555554]]
def Comparer(app, message): #message - json от фронта, app - аппаратура
    instruction = GetInstruction(app, 0)

    # [0][1] - session_id (надо придумать)
    # [1][1] - id
    # [2][1] - draggable
    # [3][1] - rotatable (НЕ НУЖЕН)
    # [4][1] - currentValue
    # [5][1] - left
    # [6][1] - top

    # Количество шагов:
    # П302-O: 5 шагов

    steps_num = 0
    if app == "P302O":
        steps_num = 5

    return_request = {"validation": False}

    for i in range(steps_num):
        if message["isTraining"]:
            return_request["next_id"] = instruction["next_id"]
            #TODO next_actions

        if instruction["id"] == message[1][1]:  # element id
            if message[2][1]:  # is element draggable
                if message[5][1] >= instruction["left"] - 5 or message[5][1] <= instruction["left"] + 5:
                    if message[6][1] >= instruction["top"] - 5 or message[6][1] >= instruction["top"] + 5:
                        return_request["validation"] = True
            else:
                if message[4][1] == instruction["currentValue"]:
                    return_request["validation"] = True

        return_request[""]

    return return_request
