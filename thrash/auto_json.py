import json
import os

with open(os.path.abspath(r"norm\ex_1.1.json"), 'r', encoding='utf-8') as f:
    json_file = json.load(f)


actions = json_file['step_0']['next_actions']

sub_steps = []

for i, action in enumerate(actions, start=1):
    temp_dict = dict()

    temp_dict['name'] = f'sub_step_{i}'
    temp_dict['action_id'] = action['next_id']
    temp_dict['current_value'] = action['current_value']
    temp_dict['before_id'] = action['next_id']
    temp_dict['tag'] = action['tag']

    sub_steps.append(temp_dict)

print(sub_steps)