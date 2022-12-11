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

    print(instruction["id"])
    if instruction["id"] == message[1][1]:
        print(message[1][1])
    else:
        return "BAD ID"

    if instruction["draggable"] == message[2][1]:
        print(message[2][1])
    else:
        return "BAD DRAGGABLE"

    if instruction["currentValue"] == message[4][1]:
        print(message[4][1])
    else:
        return "BAD VALUE"

    return "RIGHT STEP"
