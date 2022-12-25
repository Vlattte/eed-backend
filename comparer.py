#mport getInstruction
import json
import db

def GetInstruction(app, step_id): #app - аппаратура, step_id - номер шага
    instr_file = open("test.json", encoding='utf-8')
    data = json.load(instr_file)

    for i in range(len(data)):
        if data["step_"+str(i)]["step"] == step_id:
            return data["step_"+str(i)]

#[["session_id","1gjolm7fq"],["id",1015],["draggble",false],["rotatable",true],["currentValue",60],["left",249.99999999999997],["top",105.55555555555554]]
def Comparer(app, message): #message - json от фронта, app - аппаратура
    #print(message)
    
    session_id = message[0][1]
    session_id_list = db.get_session_id_list()

    # Если session_id нет в таблице, то создаем запись для него и устанавливаем номер шага = 0
    if session_id not in session_id_list:
        instruction = GetInstruction(app, 0)
        db.write_row(session_id=session_id, 
                     step_num=0, 
                     actions_for_step=instruction['actions_for_step'], 
                     attempts_left=3)

    
    step, left_attempts = db.get_step_attempts(session_id=session_id)
    #print(step, left_attempts)


    instruction = GetInstruction(app, step)
    next_actions = instruction['next_actions']
    before_id = instruction['before_id']
    count_next =  instruction['count_next']

    #print(instruction['next_actions'][0]['annotation'])

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
        steps_num = 4
    
    # По умолчанию считаем, что отдаваемый ответ = False
    return_request = {"validation": False, "next_id": 1017, 
                      "id": message[1][1], "is_fail": False, 
                      "is_finished": False, 'next_actions': next_actions, 
                      'before_id': before_id, 'count_next': count_next}

    #if message["isTraining"]:
    #    return_request["next_id"] = instruction["next_id"]
    #    #TODO next_actions
    

    if instruction["id"] == message[1][1]:  # element id
        if message[2][1]:  # is element draggable
            (message[6][1], instruction["top"])

            if abs(message[5][1] - instruction["left"]) <= 10:
                if abs(message[6][1] - instruction["top"]) <= 10:
                    return_request["validation"] = True
        else:
            if str(message[4][1]) == str(instruction["current_value"]):
                return_request["validation"] = True

    if return_request['validation'] == True:
        print('Правильное действие')
        if step == steps_num:
            print('Карта пройдена')
            return_request['is_finished'] = True
            pass
        else:
            new_instruction = GetInstruction(app, step + 1)
            db.write_row(session_id=session_id, 
                     step_num=step + 1, 
                     actions_for_step=new_instruction['actions_for_step'], 
                     attempts_left=3)

    elif return_request['validation'] == False:
        print('Неправильное действие')
        if left_attempts == 1:
            print('Попытка провалена')
            return_request['is_fail'] = True
            pass
        else:
            #return_request['is_finished'] = True
            db.write_row(session_id=session_id, 
                     step_num=step, 
                     actions_for_step=instruction['actions_for_step'], 
                     attempts_left=left_attempts - 1)
    
    return return_request
