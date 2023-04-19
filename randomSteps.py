import random
import json

# формирует массив рандомных положений и сразу проверяет попало ли в правильное положение
def RandomPrepare(app_id, instruction, app_name):
    # app_name      - получаем название аппаратуры (P302O)
    # file_name     - название файл с id всех элементов
    # id2type_file  - дескриптор файла с id всех элементов
    # id2type_data  - данные из этого файла

    file_name = "init_jsons\id2type_" + app_name + ".json"
    id2type_file = open(file_name, encoding="utf-8")
    id2type_data = json.load(id2type_file)
    sub_steps_num = 0

    # prepare_random_values - массив всех элементов (для выставления их в нужное положение)
    # ^^^^^^^^^ TODO: это кажется лучше поменять ^^^^^^^^^
    # prepare_action_values - массив для подсветки следующих элементов
    # app_el_count - словарь соответствия id аппаратуры и количества подсвеченных элементов на ней

    prepare_random_values = []
    prepare_action_values = []
    app_el_count = {}

    # ID отслеживаемых элементов, чтобы рандомить только их
    instruction_id_list = parse_ids(instruction)

    # цикл по отдельным видам элементов
    for tag in id2type_data:
        # NOTE: УБРАТЬ JUMPER, КОГДА ИХ ДОБАВЯТ ПОЛНОЦЕННО НА ФРОНТЕ
        # эти элементы пока не сделаны, пропускаем
        if tag == "cabel" or tag == "cabel_head" or tag == "jumper" or tag == "mover":
            continue

        # если все возможные положения элементов одинаковы
        # например, для всех тумблеров положения только on и off => all_values == True
        if id2type_data[tag]["all_values"]:
            for id in id2type_data[tag]["ids"]:
                # если ID не в списке отслеживаемых, пропускаем
                if id not in instruction_id_list:
                    continue
                # state_id - зарандомленное положение элемента
                # state - значение элемента на позиции state_id
                # app_id - id упаковки (модуль оборудования, например, ЩКЧН)
                # new_el - буфер, для хранения данных по текущему элементу
                # isRandomStateRight - флаг правильности рандомного положения

                state_id = random.randint(0, id2type_data[tag]["values_arr_size"]-1)
                state = id2type_data[tag]["values"][state_id]
                app_id = id // 1000

                new_el = {"apparat_id": app_id, "next_id": id, "draggable": False, "current_value": state, "tag": tag}
                isRandomStateRight = CheckIsRandomRight(instruction, new_el)

                # если элемент не в том положении, то студент
                # должен будет поставить его в нужное => запоминаем
                if not isRandomStateRight:
                    new_el["current_value"] = id2type_data[tag]["values"].index(state)
                    prepare_action_values.append(new_el)
                    sub_steps_num += 1

                    # запоминаем сколько элементов загорится на каждом блоке
                    if not str(app_id) in app_el_count:
                        app_el_count[str(app_id)] = 1
                    else:
                        app_el_count[str(app_id)] += 1

                new_el["current_value"] = id2type_data[tag]["values"].index(state)
                prepare_random_values.append(new_el)

        else:
            for el in id2type_data[tag]["elements"]:
                id = el["id"]
                if id not in instruction_id_list:
                    continue
                values_count = len(el["values"])

                state_id = random.randint(0,  values_count-1)
                state = el["values"][state_id]
                app_id = id // 1000

                new_el = {"apparat_id": app_id, "next_id": id, "draggable": False, "current_value": state, "tag": tag}
                isRandomStateRight = CheckIsRandomRight(instruction, new_el)

                if not isRandomStateRight:
                    new_el["current_value"] = el["values"].index(state)
                    prepare_action_values.append(new_el)
                    sub_steps_num += 1

                    # запоминаем сколько элементов загорится на каждом блоке
                    if not str(app_id) in app_el_count:
                        app_el_count[str(app_id)] = 1
                    else:
                        app_el_count[str(app_id)] += 1

                new_el["current_value"] = el["values"].index(state)
                prepare_random_values.append(new_el)

    # print(prepare_action_values)
    return prepare_action_values, prepare_random_values, sub_steps_num, app_el_count

# сравнивает соответсвует ли рандомизированное значение с нужным из карты
def CheckIsRandomRight(instruction, new_el):
    isRandomStateRight = False

    # колличество подшагов
    steps = instruction["actions_for_step"]

    # проходимся по всем подшагам
    for i in range(steps):
        # когда найдем шаг связанный с нужным элементом
        # сравниваем соответсвует ли рандомизированное значение с нужным из карты
        if instruction["sub_steps"][i]["action_id"] == new_el["next_id"]:
            if str(instruction["sub_steps"][i]["current_value"]) == str(new_el["current_value"]):
                isRandomStateRight = True

    return isRandomStateRight

# Принимает на вход инструкцию и возвращает массив ID, которые использовались в инструкции.
# Необходима, чтобы рандомить только отслеживаемые в инструкции элементы
def parse_ids(instruction):
    id_mas = []
    for sub_step in instruction['sub_steps']:
        id = sub_step['action_id']
        if id not in id_mas:
            id_mas.append(id)

    return id_mas