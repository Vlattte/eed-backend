#mport getInstruction
import json
import db

def GetInstruction(app, step_id): #app - аппаратура, step_id - номер шага
    instr_file = open(app, encoding='utf-8')
    data = json.load(instr_file)

    for i in range(len(data)):
        if data["step_"+str(i)]["step"] == step_id:
            return data["step_"+str(i)]


# надо записать индексы из массива array_actions_for_step, в виде словаря по типу: "index": bool,
# где bool - сделан ли шаг под этим индексом
# в этом шаге может быть написан следующий шаг, значащий следующее положение этого же элемента
def CheckMultipleInstructions(session_id, instruction, message, left_attempts, step, left_steps):
    # код возврата: -1 - ошибка пользователя, 0 - остались еще под шаги, 1 - шаги кончились, все правильно
    return_code = -1

    steps = instruction["actions_for_step"]
    sub_steps = []
    result = db.is_field_exists(session_id, "sub_steps")
    if not result:
        for i in range(steps):
            sub_steps.append({instruction["sub_steps"][i]["name"]: "False"})

        db.write_row(session_id=session_id,
                     step_num=step,
                     actions_for_step=instruction['actions_for_step'],
                     sub_steps=sub_steps,
                     attempts_left=left_attempts)
    else:
         sub_steps = db.get_field_data(session_id, "sub_steps")
         #sub_steps = json.dumps(sub_steps)


    for i in range(steps):
        if instruction["sub_steps"][i]["action_id"] == message[1][1]:
            if instruction["sub_steps"][i]["current_value"] == message[4][1]:
                name = instruction["sub_steps"][i]["name"]

                if sub_steps[i][name] == "False":
                    sub_steps[i][name] = "True"
                    return_code = 0

                    if left_steps == 1:
                        return_code = 1
                    else:
                        db.write_row(session_id=session_id,
                                 step_num=step,
                                 actions_for_step=left_steps-1,
                                 sub_steps=sub_steps,
                                 attempts_left=left_attempts)
    return return_code

def WhatExercise(message):
    is_training = "nan"
    exercise_name = "test.json"

    if message[0][0] == "session_id":
        exercise_name = "test.json"

    # проверяем флаг тренировки
    if message[1][0] == "is_training":
        is_training = message[1][1]

    # id норматива
    if message[2][1] == "ex_id":
        if "ex_id" == 0:
            exercise_name = "test.json"
        #TODO: добавить потом другие нормативы

    return exercise_name, is_training

#[["session_id","1gjolm7fq"],["id",1015],["draggble",false],["rotatable",true],["currentValue",60],["left",249.99999999999997],["top",105.55555555555554]]
def Comparer(message): #message - json от фронта, app - аппаратура
    # по id норматива получаем название соответсвующего файла
    # так же получаем значение флага is_training
    is_zero_step = False
    exercise_name, is_training = WhatExercise(message)
    session_id = message[0][1]
    session_id_list = db.get_session_id_list()


    # Если session_id нет в таблице, то создаем запись для него и устанавливаем номер шага = 0
    if session_id not in session_id_list:
        instruction = GetInstruction(exercise_name, 0)
        sub_steps = {'name': 'nan'}
        is_zero_step = True
        db.write_row(session_id=session_id, 
                     step_num=0,
                     actions_for_step=instruction["count_action"],
                     sub_steps=sub_steps,
                     attempts_left=1,
                     is_training=is_training)



    if is_training != 'nan':
        instruction = GetInstruction(exercise_name, 0)
        return_request = {'next_actions': instruction['next_actions']}

    step, left_attempts, left_steps, is_training = db.get_step_attempts(session_id=session_id)

    instruction = GetInstruction(exercise_name, step)

    # [0][1] - session_id
    # [1][1] - id
    # [2][1] - draggable
    # [3][1] - rotatable (НЕ НУЖЕН)
    # [4][1] - currentValue
    # [5][1] - left
    # [6][1] - top

    # Количество шагов:
    # П302-O: 5 шагов

    steps_num = 0
    if exercise_name == "test.json":
        steps_num = 4

    has_action = False
    # По умолчанию считаем, что отдаваемый ответ = False
    if instruction["count_actions"] > 0:
        has_action = True

    return_request = {"validation": False,
                      "has_action": has_action,
                      "annotation":    instruction["annotation"],
                      "fail": False,
                      "count_action":  instruction["count_action"],
                      "array_actions": instruction["array_actions"],
                      "count_next":    instruction["count_next"],
                      "next_actions":  instruction["next_actions"],
                      "finish": False,
                      "before_id":     instruction["before_id"]}

    #if message["isTraining"]:
    #    return_request["next_id"] = instruction["next_id"]
    #    #TODO next_actions
    
    step_increm = 1
    multiple_res = 1


    if not is_zero_step:
            # multiple == несколько действий за шаг
        if instruction["id"] == "multiple":
            multiple_res = CheckMultipleInstructions(session_id, instruction, message, left_attempts, step, left_steps)
            print("res: " + str(multiple_res))
            if multiple_res != -1:
                return_request["validation"] = True
                step_increm = 0
            if multiple_res == 1:
                step_increm = 1


        elif instruction["id"] == message[1][1]:  # element id
            if message[2][1]:  # is element draggable
                if abs(message[5][1] - instruction["left"]) <= 10:
                    if abs(message[6][1] - instruction["top"]) <= 10:
                        return_request["validation"] = True
            else:
                if str(message[4][1]) == str(instruction["current_value"]):
                    return_request["validation"] = True

        if return_request['validation']:        # если правильное действие
            print('Правильное действие')
            if step == steps_num:                       # если финальный шаг
                print('Карта пройдена')
                return_request['finish'] = True
                pass
            else:
                if multiple_res == 1:
                    new_instruction = GetInstruction(exercise_name, step + 1)
                    sub_steps = {'name': 'nan'}
                    db.write_row(session_id=session_id,
                            step_num=step + step_increm,
                            actions_for_step=new_instruction['actions_for_step'],
                            sub_steps=sub_steps,
                            attempts_left=1)

        elif return_request['validation'] == False:
            print('Неправильное действие')
            if left_attempts == 1:
                print('Попытка провалена')
                return_request['fail'] = True
                pass
            else:
                #return_request['is_finished'] = True
                sub_steps = {'name': 'nan'}
                db.write_row(session_id=session_id, 
                        step_num=step, 
                        actions_for_step=instruction['actions_for_step'],
                        sub_steps=sub_steps,
                        attempts_left=left_attempts - 1)
    
    return return_request
