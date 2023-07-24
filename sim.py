# Here is the refactored code
import random
import time
import math
import datetime
import numpy as np
# Game parameters
parameters = {
    "num_dots": 300,
    "total_time": 600,
    "base_decay": 0.005,
    "state_window": 0.5,
    "incremental_num": 5,
    "interval" : 0.02
}

# Colours
colors = {
    "dots_colors": [(55,255,55), (255,55,55)],
}

# Initialize dots
dots = []

# Initialize game variables
running = True
count = 0
initialize = 1
loop_idx = 0
num_bin = int(parameters["state_window"] / parameters["interval"])
max_time = 15 * 60 

# Initialize records
records = {
    'response': [], 'allaydotnum': [], 'enemydotnum': [], 'frameidx': []
}

# Agent
perception_model = 'ideal'
perception_window = 0.2
perception_num_bin =  int(perception_window / parameters["interval"])
plan_model = 'ideal'
action_error_rate = 0.05
plan_bias_rate = 0.1
minimal_response_interval = 0.06
action_num_bin = int(minimal_response_interval / parameters["interval"])
jndr = 0.1 # 最小可觉差比例

# simulation setting
simulations = []
simulation_length = []
simulation_num = 5000

# Function to create a dot
def create_dot(color):
    dot = [True, color]
    return dot

# Main game loop
for i in range(simulation_num):
    if i % 100 == 0:
        print(f'simulation #{i}')
    running = True
    records = {'response': [], 'allaydotnum': [], 'enemydotnum': [], 'frameidx': []}
    loop_idx = 0
    delta_t = int(random.uniform(2, 4) * (1/parameters['interval']))
    t_change = 0
    dots = []
    initialize = 1
    while running:
        #=======================================
        #   stimuli change in every frame
        #=======================================
        # 生成一堆点
        if initialize:
            for i in range(parameters["num_dots"] - len(dots)):
                color = colors["dots_colors"][int(np.random.choice([0,1]))]
                dots.append(create_dot(color))
            initialize = 0
        # check the way out loop
        allay = [_ for _ in dots if _[-1]==colors['dots_colors'][0]]
        enemy = [_ for _ in dots if _[-1]==colors['dots_colors'][1]]
        if loop_idx < num_bin * max_time:
            if len(dots) == 0 or len(allay) == 0 or len(enemy) == 0:
                simulations.append(records)
                simulation_length.append(loop_idx)
                running = False
        else:
            simulations.append(records)
            simulation_length.append(loop_idx)
            running = False
        # 到时间后随机产生一个变化
        if loop_idx > t_change + delta_t:
            change_type = random.choice(["increase", "decrease"])
            change_direction = random.choice(["maintain", "reverse"])
            change_amount = random.choice([0.2, 0.4, 0.5, 0.6, 0.7, 0.8])
            if len(dots) < parameters["num_dots"]/2:
                change_type = "increase"
            elif len(dots) > parameters["num_dots"]*1.5:
                change_type = "decrease"
            num_change = int(len(dots) * change_amount)
            allay_dots = [dot for dot in dots if dot[-1] == colors["dots_colors"][0]]
            enemy_dots = [dot for dot in dots if dot[-1] == colors["dots_colors"][1]]
            if change_type == "increase":
                if change_direction == "maintain":
                    for i in range(num_change):
                        color = colors["dots_colors"][int(np.random.choice([0,1]))]
                        dots.append(create_dot(color))
                elif change_direction == "reverse":
                    diff = len(allay_dots) - len(enemy_dots)
                    if diff != 0:
                        color = colors["dots_colors"][0] if diff < 0 else colors["dots_colors"][1]
                        for i in range(2 * abs(diff)):
                            dots.append(create_dot(color))
            elif change_type == "decrease":
                if change_direction == "maintain":
                    for i in range(num_change):
                        dots.pop(0)
                elif change_direction == "reverse":
                    diff = len(allay_dots) - len(enemy_dots)
                    if diff != 0:
                        color = colors["dots_colors"][0] if diff > 0 else colors["dots_colors"][1]
                        for i in range(2 * abs(diff)):
                            dot = next((dot for dot in dots if dot[-1] == color), None)
                            if dot:
                                dots.remove(dot)
            t_change = loop_idx
            delta_t = int(random.uniform(2, 4) * (1/parameters['interval']))
        # 
        records['frameidx'].append(loop_idx)
        # every state_window check the state
        if loop_idx % num_bin == 0:
            # compare number of colored dots
            dotcolors = [ _[-1] for _ in dots ]
            num_0 = len([ _ for _ in dotcolors if _ ==colors['dots_colors'][0] ])
            num_1 = len([ _ for _ in dotcolors if _ ==colors['dots_colors'][1] ])
            cur_diff = np.abs(num_0 - num_1)
            # determine the loser color
            if num_0 == num_1:
                loser_color = colors['dots_colors'][int(np.random.rand() < 0.5)] # if less than 0.5 -> 1;
            else:
                loser_color = colors['dots_colors'][int(num_0 > num_1)] # if num_0 bigger than num_1 then 1 
            # define kill number
            loser_dots = [dot for dot in dots if dot[-1]==loser_color]
            kill_num = math.ceil(parameters["base_decay"]*len(loser_dots))
        # base_decay
        parameters["base_decay"] = np.max([0.005, 0.1*kill_num/(len(dots)+1e-10)])
        # kill
        delta_bin = round(num_bin/(kill_num + 1e-10))
        if loop_idx % delta_bin == 0:
            loser_dots = [dot for dot in dots if dot[-1]==loser_color]
            if len(loser_dots)==0:
                simulations.append(records)
                simulation_length.append(loop_idx)
                running = False
            else:
                loser_dots[0][0] = False

        # remove the killed dots
        dots = [dot for dot in dots if dot[0]]

        response_pressed = False
        #=======================================
        # Agent percept and action in every frame
        #=======================================
        # 每 200ms 产生一个估计，并以此形成计划
        if 'action_timepoints' not in globals():
                action_timepoints = []
        if 'actions'not in globals():
            actions = []
        if loop_idx % perception_num_bin == 0:
            # number perception
            if perception_model == 'ideal':
                num_a_dots = len([dot for dot in dots if dot[-1]==colors['dots_colors'][0]])
                num_e_dots = len([dot for dot in dots if dot[-1]==colors['dots_colors'][1]])
                diff = num_a_dots - num_e_dots
            elif perception_model == 'noisy':
                num_a_dots = len([dot for dot in dots if dot[-1]==colors['dots_colors'][0]]) 
                num_e_dots = len([dot for dot in dots if dot[-1]==colors['dots_colors'][1]])
                diff = (num_a_dots + np.sqrt(jndr*num_a_dots)*np.random.randn(1)) - (num_e_dots + np.sqrt(jndr*num_e_dots)*np.random.randn(1))
            # plan based on diff
            action, action_num = 0, 0
            if abs(diff) > jndr*len(dots):
                if plan_model == 'ideal':
                    action = np.sign(-diff)
                    action_num = int(np.abs(diff)/parameters['incremental_num'])
                if plan_model == 'noisy':
                    # 按键以 action error rate 出错
                    action = np.sign(-diff) if random.uniform(0,1) < (1 - action_error_rate) else - np.sign(-diff)
                    # 按键次数以 plan_bias_rate 为方差的高斯随机偏离
                    action_num = int(np.abs(diff)/parameters['incremental_num'] * ( 1 + np.sqrt(plan_bias_rate) * np.random.randn(1)))
            # 
            if len(action_timepoints) != 0:
                # 如果新计划与旧计划有重叠，则删除重叠部分
                new_plan_timepoint =  [_ for _ in range(loop_idx, loop_idx + action_num * action_num_bin)]
                if set(action_timepoints) & set(new_plan_timepoint):
                    action_timepoints = sorted(list(set(action_timepoints) - (set(action_timepoints) & set(new_plan_timepoint))))
            if len(actions) != 0:
                actions = actions[0:len(action_timepoints)]
            for i in range(action_num):
                change_idx = int(loop_idx + action_num_bin * i)
                action_timepoints.append(change_idx)
                actions.append(action)
        # excute the action plan
        tp_check = True
        while (len(action_timepoints) and tp_check):
            if loop_idx > action_timepoints[0]:
                action_timepoints.pop(0)
                actions.pop(0)
            else:
                tp_check = False
        if len(action_timepoints):
            if loop_idx == action_timepoints[0]:
                response_pressed = True
                # 扔掉开头的timeponit
                t_response = action_timepoints.pop(0)
                # 读取对应的action
                response = actions.pop(0)
                records['response'].append(response)
                if response > 0:
                    for i in range(parameters['incremental_num']):
                        color = colors['dots_colors'][0]
                        dots.append([True, color])
                else:
                    allay_dots = [_ for _ in dots if _[-1]==colors['dots_colors'][0]]
                    if len(allay_dots) < parameters['incremental_num']:
                        pass
                    else:
                        for i in range(parameters['incremental_num']):
                            allay_dots[i][0] = False
                            dots = [dot for dot in dots if dot[0]] 
        # response_pressed 为false 则记成0 
        if not response_pressed:
            records['response'].append(0)

        # after action check the dots
        allay = [_ for _ in dots if _[-1]==colors['dots_colors'][0]]
        enemy = [_ for _ in dots if _[-1]==colors['dots_colors'][1]]
        records['allaydotnum'].append(len(allay)) 
        records['enemydotnum'].append(len(enemy))
        loop_idx += 1
    
max_length = np.max(simulation_length)
for sim_sample in simulations:
    for key, data in sim_sample.items():
        if key == 'frameidx':
            while len(data) < max_length:
                data.append(data[-1]+1)
        else:
            while len(data) < max_length:
                data.append(0)

np.save('./simulation.npy', np.array(simulations))