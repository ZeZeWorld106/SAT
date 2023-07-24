import pygame
import random
import time
import math
import datetime
import numpy as numpy
import os

# 读取当前目录
current_path = os.getcwd()

pygame.init()
check = False

# 屏幕显示相关的属性设定
screen_width = 900
screen_height = 900  
boundsize = 450
dot_size = 5
GREEN = (0, 255, 0)
BLACK = (255, 255, 255)
WHITE = (0, 0, 0)
RED = (255, 0, 0)
screen = pygame.display.set_mode((screen_width, screen_height))
# # 随机点刺激的相关属性设定
dots = []
num_dots = 300
dots_colors = [(55,255,55), (255,55,55)]
# 随机点运动的刺激边界属性设定
circle_x = screen_width / 2
circle_y = screen_height / 2

running = True
# 总共刺激呈现的时间【这里有待改成随机的刺激总时长呈现】
total_time = 600
blue_dot_ratio = 0.5
count = 0
# 随机点减少的初始速率
base_decay = 0.02
prac_change_p = [0.3, 0.4]
change_p = [0.4, 0.5, 0.6]

initialize = 1
# 经历循环的次数（索引设置）
loop_idx = 0
state_window = 0.5
interval = 0.02
num_bin = int(state_window/interval)

# 增加的点
green_dot = pygame.Surface((20, 20))
green_dot.fill(GREEN)
incremental_num = 5
records = {'response':[], 'allaydotnum':[], 'enemydotnum':[], 'killnum':[],'frameidx':[],'basedecay':[],
           'v_allay':[], 'v_enemy':[]}

# Function to create a dot
def create_dot(color, circle_x=circle_x, circle_y=circle_y, boundsize=boundsize):
    radius = numpy.random.uniform(0, boundsize/2)
    angle = numpy.random.uniform(0, math.pi*2)
    x = circle_x + radius * math.cos(angle)
    y = circle_y + radius * math.sin(angle)
    speed = numpy.random.uniform(2, 2.5)
    direction = random.choice([
        [-1, 0], [1, 0], [0, -1], [0, 1], 
        [numpy.sqrt(2)/2, numpy.sqrt(2)/2], [numpy.sqrt(2)/2, -numpy.sqrt(2)/2], 
        [-numpy.sqrt(2)/2, numpy.sqrt(2)/2], [-numpy.sqrt(2)/2, -numpy.sqrt(2)/2]
    ])
    dot = [[x, y], speed, direction, True, color]
    return dot
# 获取信息
# name = inumpyut("enter your name:")
name = 'computer'
# 显示指导语
font = pygame.font.Font(f"{current_path}\Deng.ttf", 24)
start_btn = pygame.Rect(350, 750, 200, 80) 
btn_text = font.render("开始", True, GREEN)
pygame.draw.rect(screen, (70,70,70), start_btn)
start_text = pygame.transform.scale(btn_text, (64, 32))
start_width = start_text.get_width()
start_height = start_text.get_height()
plus_x = start_btn.x + (start_btn.width - start_width) / 2
plus_y = start_btn.y + (start_btn.height - start_height) / 2
screen.blit(start_text, (plus_x, plus_y)) 

guide_text_lines = [
    "尊敬的参与者, 您好!",
    "本实验模拟了我军与敌军的空战缠斗中的均势维持战况。",
    "屏幕上呈现我军和敌军飞机。它们在屏幕内运动和消失。",
    "您扮演我军指挥员,需要根据双方飞机数量判断力量对比",
    "通过操作调节我军飞机数量,努力维持战场平衡。",
    "您的目标是通过操作尽量维持双方力量近似平衡,避免以下两种情况:",
    "1.战场上敌方兵力过多，使得我军尽数歼灭，任务宣告失败。",
    "2.战场上我方兵力过多，使得敌军放弃阵地，任务宣告失败。",
    "此外,战场会出现一些突发状况导致数量突然改变,造成态势突变。",
    " ",
    "你需要通过雷达表盘时刻监控战场态势,以及时应对态势:",
    "当敌方占优时,按【+】增加我军飞机,以支援战场,",
    "当我军占优时,按【-】减少我军飞机,以撤回兵力。",
    "每次操作将增加或减少我军5架飞机。",
    "请以最小的操作数尽可能长地延迟任务时间",
    " ",
    "如没有其他问题,请点击【开始】进行训练。",
    "如有任何问题,请及时提出。",
    "练习环节过后，我们将开始正式实验。",
    "祝您实验顺利!"
]

for i, line in enumerate(guide_text_lines):
    guide_text = font.render(line, True, GREEN)
    if i in [6,7,11,12,13,18]:
        guide_text = font.render(line, True, RED)  
    guide_text_width = guide_text.get_width()
    guide_text_height = guide_text.get_height()
    guide_text_x = (screen_width- guide_text_width) / 2
    guide_text_y = 180 + i * guide_text_height
    screen.blit(guide_text, (guide_text_x, guide_text_y))

      
is_start = False
while not is_start:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_btn.collidepoint(event.pos):
                is_start = True
    pygame.display.update()



# 练习环节
is_practice = True
prac_idx_change = 0
prac_t_change = time.time()
prac_delta_t = random.uniform(4, 6)
prac_idx = 1
accident = True
prac_dots_num = 25
while is_practice:
    if accident:
      accident_order = [("increase", "maintain"), ("increase", "reverse"), ("decrease", "maintain"), ("decrease", "reverse")]
      random.shuffle(accident_order)
      accident = False
      records = {'response':[], 'allaydotnum':[], 'enemydotnum':[], 'killnum':[],'frameidx':[],'basedecay':[],
           'v_allay':[], 'v_enemy':[]}
      prac_begin = time.time()
    if prac_idx_change <= 3:
      if time.time() - prac_t_change > prac_delta_t:
        change_type = accident_order[prac_idx_change][0]
        change_direction = accident_order[prac_idx_change][1]
        change_amount = random.choice(prac_change_p)
        prac_idx_change += 1
        # 
        if len(dots) < prac_dots_num/2:
            change_type = "increase"
        elif len(dots) > prac_dots_num*1.5:
            change_type = "decrease"
        num_change = int(len(dots) * change_amount)
        #  
        allay_dots = [dot for dot in dots if dot[4] == dots_colors[0]]
        enemy_dots = [dot for dot in dots if dot[4] == dots_colors[1]]
        if change_type == "increase":
            if change_direction == "maintain":
                for i in range(num_change):
                    color = dots_colors[int(numpy.random.choice([0,1]))]
                    dots.append(create_dot(color))
            elif change_direction == "reverse":
                diff = len(allay_dots) - len(enemy_dots)
                if diff != 0:
                    color = dots_colors[1] if diff > 0 else dots_colors[0]
                    for i in range(2 * abs(diff)):
                        dots.append(create_dot(color))
                else:
                  color = dots_colors[int(random.choice([0,1]))]
                  for i in range(num_change):
                        dots.append(create_dot(color))
        elif change_type == "decrease":
            if change_direction == "maintain":
                for i in range(num_change):
                    dots.pop(0)
            elif change_direction == "reverse":
                diff = len(allay_dots) - len(enemy_dots)
                if 2 * abs(diff) < numpy.min([len(allay_dots), len(enemy_dots)]):
                  if diff != 0:
                      color = dots_colors[1] if diff < 0 else dots_colors[0]
                      for i in range(2 * abs(diff)):
                          dot = next((dot for dot in dots if dot[4] == color), None)
                          if dot:  dots.remove(dot)
                  else: 
                    num_change =  numpy.min([num_change, 0.5*len(enemy_dots)])
                    color = dots_colors[int(random.choice([0,1]))]
                    for i in range(num_change):
                          dot = next((dot for dot in dots if dot[4] == color), None)
                          if dot:  dots.remove(dot)
                else:
                  num_change =  numpy.min([num_change, diff])
                  # 多的减
                  color = dots_colors[1] if diff < 0 else dots_colors[0]
                  for i in range(num_change):
                    dot = next((dot for dot in dots if dot[4] == color), None)
                    if dot:  dots.remove(dot)
                  # 少的补
                  color = dots_colors[1] if diff > 0 else dots_colors[0]
                  for i in range(num_change):
                    dots.append(create_dot(color))         
        prac_t_change =  time.time() 
        prac_delta_t = random.uniform(4, 6)
            
      records['frameidx'].append(loop_idx)
      response_pressed = False
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
          response_pressed = True
          if increase_btn.collidepoint(event.pos):
            # pygame.draw.rect(screen, (0, 255, 255), increase_btn)
            records['response'].append(1)
            for i in range(incremental_num):
              radius = numpy.random.uniform(0, boundsize/2)
              angle = numpy.random.uniform(0, math.pi*2)

              x = circle_x + radius * math.cos(angle)
              y = circle_y + radius * math.sin(angle)
              
              speed = numpy.random.uniform(2, 3)
              direction = random.choice([[-1, 0], [1, 0], [0, -1], [0, 1], [numpy.sqrt(2)/2, numpy.sqrt(2)/2], [numpy.sqrt(2)/2, -numpy.sqrt(2)/2], [-numpy.sqrt(2)/2, numpy.sqrt(2)/2], [-numpy.sqrt(2)/2, -numpy.sqrt(2)/2]])
              color = dots_colors[0]
              dots.append([[x, y], speed, direction, True, color])
          if decrease_btn.collidepoint(event.pos):
            # pygame.draw.rect(screen, (0, 255, 255), decrease_btn)
            records['response'].append(-1)
            allay_dots = [_ for _ in dots if _[4]==dots_colors[0]]
            if len(allay_dots) < incremental_num:
              for i in range(len(allay_dots)):
                allay_dots[i][3] = False
            else:
              for i in range(incremental_num):
                allay_dots[i][3] = False
              dots = [dot for dot in dots if dot[3]]
          pygame.display.update()
      # 如果没有按键，response 记录 0    
      if not response_pressed:
        records['response'].append(0)
      # 更新点的位置、速度（大小 方向）
      for dot in dots:
        # location predition 
        temp_x = dot[0][0] + dot[1] * dot[2][0]
        temp_y = dot[0][1] + dot[1] * dot[2][1]
        # check if the loction in next frame go beyond the boundary, then reverse the direction
        if not ((temp_x-circle_x)**2 + (temp_y-circle_y)**2 <= (boundsize/2)**2):
          direction_randomness = 0.25*numpy.random.randn(2) 
          dot[2] = [-_+direction_randomness[i] for i, _ in enumerate(dot[2])] 
        # update the loction
        dot[0][0] += dot[1] * dot[2][0] 
        dot[0][1] += dot[1] * dot[2][1]
        # # velocity 
        velocity_randomness = float(0.15*(numpy.random.rand(1)-0.5))
        dot[1] = numpy.clip(dot[1]+velocity_randomness, 1.5, 3.5)
      # 如果initialize=1， 随机初始化点数
      if initialize:
        for i in range(prac_dots_num - len(dots)):
                
          radius = numpy.random.uniform(0, boundsize/2)
          angle = numpy.random.uniform(0, math.pi*2)
          
          x = circle_x + radius * math.cos(angle)
          y = circle_y + radius * math.sin(angle)
          
          speed = numpy.random.uniform(2, 2.5)
          direction = random.choice([[-1, 0], [1, 0], [0, -1], [0, 1], [numpy.sqrt(2)/2, numpy.sqrt(2)/2], [numpy.sqrt(2)/2, -numpy.sqrt(2)/2], [-numpy.sqrt(2)/2, numpy.sqrt(2)/2], [-numpy.sqrt(2)/2, -numpy.sqrt(2)/2]])
          color = dots_colors[int(numpy.random.choice([0,1]))]
          
          dots.append([[x, y], speed, direction, True, color])
        initialize = 0
      # every state_window check the state
      if loop_idx % num_bin == 0:
        # compare number of colored dots
        dotcolors = [ _[-1] for _ in dots ]
        num_0 = len([ _ for _ in dotcolors if _ ==dots_colors[0] ])
        num_1 = len([ _ for _ in dotcolors if _ ==dots_colors[1] ])
        cur_diff = numpy.abs(num_0 - num_1)
        # determine the loser color
        if num_0 == num_1:
            loser_color = dots_colors[int(numpy.random.rand() < 0.5)] # if less than 0.5 -> 1;
        else:
            loser_color = dots_colors[int(num_0 > num_1)] # if num_0 bigger than num_1 then 1 
        # define kill number
        loser_dots = [dot for dot in dots if dot[4]==loser_color]
        kill_num = math.ceil(base_decay*len(loser_dots))
        # base_decay += 0.005*(loop_idx//num_bin)
        base_decay = numpy.max([0.005, 0.1*kill_num/(len(dots)+1e-10)])
        # incremental_num = int(numpy.log(0.3*kill_num+1))
        
      # kill
      delta_bin = round(num_bin/(kill_num + 1e-10))
      if loop_idx % delta_bin == 0:
        # random the order of loser dots
        loser_dots = [dot for dot in dots if dot[4]==loser_color]
        loser_dots[0][3] = False
        # remove the killed dots
        dots = [dot for dot in dots if dot[3]]
      # background
      screen.fill((0,0,0))
      # 搜集双方点信息
      allay_dots = ([ _ for _ in dots if _[-1] ==dots_colors[0] ])
      enemy_dots = ([ _ for _ in dots if _[-1] ==dots_colors[1] ])
      # 记录有关属性
      records['allaydotnum'].append(len(allay_dots))
      records['enemydotnum'].append(len(enemy_dots))
      records['killnum'].append(kill_num)
      records['basedecay'].append(base_decay)
      # # 如果点数为 0 则 记录 速度均值标准差为 nan
      if len(allay_dots) ==0 or len(enemy_dots) ==0:
        records['v_allay'].append((numpy.nan, numpy.nan))
        records['v_enemy'].append((numpy.nan, numpy.nan))
      else:
        records['v_allay'].append((numpy.mean([dot[1] for dot in allay_dots]), numpy.std([dot[1] for dot in allay_dots])))
        records['v_enemy'].append((numpy.mean([dot[1] for dot in enemy_dots]), numpy.std([dot[1] for dot in enemy_dots])))
      # 检查当前点数，如果任意一方为 0 则转入练习结束界面
      if len(dots) == 0 or len(allay_dots)==0 or len(enemy_dots) == 0:
        prac_idx_change = 999
      # draw dots
      for i, dot in enumerate(dots):    
        pygame.draw.circle(screen, dot[4], dot[0], dot_size)  
      # 反馈当前已经坚持的时间：
      font = pygame.font.Font(f"{current_path}\Deng.ttf", 32)

      sustain_time = round((time.time() - prac_begin) * 100)/100
      feedback_text = font.render(f'已坚持 {sustain_time} 秒', True, (255, 255, 255))
      screen.blit(feedback_text, (screen_width/2-100, 125))
      
      # 反馈当前 numbers， 如果 check=1 
      if check:
        font = pygame.font.Font(None, 32)
        text = font.render("#Red: " + str(num_1) + '\\n' + "#Blue:"+str(num_0)+"idxchange"+str(prac_idx_change)+'loop'+str(loop_idx), True, (255,255,255))
        screen.blit(text, (10, 10))
      # 屏幕交互相关设计   
      # 1. 初始化按钮对象
      if records['response'][-1] == 0:
        button_color1 = (110, 110, 110)
        button_color2 = (60, 60 ,60)
      elif records['response'][-1] == 1:
        button_color1 = (255, 255, 0)
        button_color2 = (60, 60 ,60)
      elif records['response'][-1] == -1:
        button_color1 = (110, 110, 110)
        button_color2 = (255, 255, 0)
      increase_btn = pygame.Rect(350, 700, 100, 50)
      decrease_btn = pygame.Rect(450, 700, 100, 50)
      # 2. 在屏幕上绘制两个按钮 
      pygame.draw.rect(screen, button_color1, increase_btn)
      pygame.draw.rect(screen, button_color2, decrease_btn)
      # 3. 按钮的意义说明
      # 3.1 按钮的icon尺寸设计
      font = pygame.font.Font(None, 48)
      plus_text = font.render("+", True, (255, 255, 255))
      minus_text = font.render("-", True, (255, 255, 255))
      plus_text = pygame.transform.scale(plus_text, (32, 32))
      minus_text = pygame.transform.scale(minus_text,(32, 32))
      
      plus_width = plus_text.get_width()
      plus_height = plus_text.get_height()
      
      minus_width = plus_text.get_width()
      minus_height = plus_text.get_height()
      
      plus_x = increase_btn.x + (increase_btn.width - plus_width) / 2
      plus_y = increase_btn.y + (increase_btn.height - plus_height) / 2

      minus_x = decrease_btn.x + (decrease_btn.width - minus_width) / 2
      minus_y = decrease_btn.y + (decrease_btn.height - minus_height) / 2

      screen.blit(plus_text, (plus_x, plus_y)) 
      screen.blit(minus_text, (minus_x, minus_y))
      pygame.display.update()
      pygame.display.flip()
      time.sleep(interval)
      
      loop_idx += 1
    else:
      filename = f'{current_path}/RD_{name}_prac{prac_idx}_record{datetime.datetime.now().strftime("%Y%m%d%H%M")}.npy'
      if not os.path.exists(filename):
        numpy.save(filename, numpy.array([records]))
        print(f'==========saved {filename}=============')
      screen.fill((0,0,0))
      font = pygame.font.Font(f"{current_path}\Deng.ttf", 24)
      enter_game_btn = pygame.Rect(250, 750, 200, 80) 
      enter_game_btn_text = font.render("正式实验", True, GREEN)
      pygame.draw.rect(screen, (70,70,70), enter_game_btn)
      enter_game_text = pygame.transform.scale(enter_game_btn_text, (64, 32))
      enter_game_text_width = enter_game_text.get_width()
      enter_game_text_height = enter_game_text.get_height()
      enter_plus_x = enter_game_btn.x + (enter_game_btn.width - enter_game_text_width) / 2
      enter_plus_y = enter_game_btn.y + (enter_game_btn.height - enter_game_text_height) / 2
      screen.blit(enter_game_btn_text, (enter_plus_x, enter_plus_y))

      restart_prac_btn = pygame.Rect(500, 750, 200, 80) 
      restart_prac_btn_text = font.render("重新练习", True, GREEN)
      pygame.draw.rect(screen, (70,70,70), restart_prac_btn)
      restart_prac_text = pygame.transform.scale(restart_prac_btn_text, (64, 32))
      restart_prac_text_width = restart_prac_text.get_width()
      restart_prac_text_height = restart_prac_text.get_height()
      restart_plus_x = restart_prac_btn.x + (restart_prac_btn.width - restart_prac_text_width) / 2
      restart_plus_y = restart_prac_btn.y + (restart_prac_btn.height - restart_prac_text_height) / 2
      screen.blit(restart_prac_btn_text, (restart_plus_x, restart_plus_y)) 
          
      
      practice_ending_announcement = "练习结束，您可以选择开始正式实验或重新开始练习。"
      important_char_C1 = font.render(practice_ending_announcement, True, RED)
      practice_ending_announcement_width = important_char_C1.get_width()
      practice_ending_announcement_height = important_char_C1.get_height()
      practice_ending_announcement_x = (screen_width - practice_ending_announcement_width) / 2
      practice_ending_announcement_y = (screen_height - practice_ending_announcement_height) / 2
      screen.blit(important_char_C1, (practice_ending_announcement_x, practice_ending_announcement_y))   
      
      # pygame.display.flip()
      
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
          if enter_game_btn.collidepoint(event.pos):
            is_practice = False
            initialize = 1 
            loop_idx = 0
          if restart_prac_btn.collidepoint(event.pos):
            initialize = 1
            prac_idx += 1
            accident = True
            prac_idx_change = 0
            loop_idx = 0
            prac_t_change = time.time()
            prac_delta_t = random.uniform(1, 4)
      time.sleep(interval)
      pygame.display.update()      
      

# 主实验
records = {'response':[], 'allaydotnum':[], 'enemydotnum':[], 'killnum':[],'frameidx':[],'basedecay':[],
           'v_allay':[], 'v_enemy':[]}      
idx_change = 0
t_change = time.time()
delta_t = random.uniform(2, 4)
task_begin = time.time()
while running:
    if time.time() - t_change > delta_t:
      idx_change += 1
      change_type = random.choice(["increase", "decrease"])
      change_direction = random.choice(["maintain", "reverse"])
      change_amount = random.choice(change_p)
      if len(dots) < num_dots/2:
          change_type = "increase"
      elif len(dots) > num_dots*1.5:
          change_type = "decrease"
      num_change = int(len(dots) * change_amount)
      allay_dots = [dot for dot in dots if dot[4] == dots_colors[0]]
      enemy_dots = [dot for dot in dots if dot[4] == dots_colors[1]]
      if change_type == "increase":
          if change_direction == "maintain":
              for i in range(num_change):
                  color = dots_colors[int(numpy.random.choice([0,1]))]
                  dots.append(create_dot(color))
          elif change_direction == "reverse":
              diff = len(allay_dots) - len(enemy_dots)


              if diff != 0:
                  color = dots_colors[1] if diff > 0 else dots_colors[0]
                  for i in range(2 * abs(diff)):
                      dots.append(create_dot(color))
              else:
                color = dots_colors[int(random.choice([0,1]))]
                for i in range(num_change):
                      dots.append(create_dot(color))
      elif change_type == "decrease":
          if change_direction == "maintain":
              for i in range(num_change):
                  dots.pop(0)
          elif change_direction == "reverse":
              diff = len(allay_dots) - len(enemy_dots)
              if 2 * abs(diff) < numpy.min([len(allay_dots), len(enemy_dots)]):
                if diff != 0:
                    color = dots_colors[0] if diff < 0 else dots_colors[1]
                    for i in range(2 * abs(diff)):
                        dot = next((dot for dot in dots if dot[4] == color), None)
                        if dot:  dots.remove(dot)
                else: 
                  num_change =  numpy.min([num_change, 0.5*len(enemy_dots)])
                  color = dots_colors[int(random.choice([0,1]))]
                  for i in range(num_change):
                        dot = next((dot for dot in dots if dot[4] == color), None)
                        if dot:  dots.remove(dot)
              else:
                num_change =  numpy.min([num_change, diff])
                # 多的减
                color = dots_colors[1] if diff < 0 else dots_colors[0]
                for i in range(num_change):
                  dot = next((dot for dot in dots if dot[4] == color), None)
                  if dot:  dots.remove(dot)
                # 少的补
                color = dots_colors[1] if diff > 0 else dots_colors[0]
                for i in range(num_change):
                  dots.append(create_dot(color))
      t_change =  time.time() 
      delta_t = random.uniform(2, 4)
          
    records['frameidx'].append(loop_idx)
    response_pressed = False
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      if event.type == pygame.MOUSEBUTTONDOWN:
        response_pressed = True
        if increase_btn.collidepoint(event.pos):
          # pygame.draw.rect(screen, (0, 255, 255), increase_btn)
          records['response'].append(1)
          for i in range(incremental_num):
            radius = numpy.random.uniform(0, boundsize/2)
            angle = numpy.random.uniform(0, math.pi*2)

            x = circle_x + radius * math.cos(angle)
            y = circle_y + radius * math.sin(angle)
            
            speed = numpy.random.uniform(2, 3)
            direction = random.choice([[-1, 0], [1, 0], [0, -1], [0, 1], [numpy.sqrt(2)/2, numpy.sqrt(2)/2], [numpy.sqrt(2)/2, -numpy.sqrt(2)/2], [-numpy.sqrt(2)/2, numpy.sqrt(2)/2], [-numpy.sqrt(2)/2, -numpy.sqrt(2)/2]])
            color = dots_colors[0]
            dots.append([[x, y], speed, direction, True, color])
        if decrease_btn.collidepoint(event.pos):
          # pygame.draw.rect(screen, (0, 255, 255), decrease_btn)
          records['response'].append(-1)
          allay_dots = [_ for _ in dots if _[4]==dots_colors[0]]
          if len(allay_dots) < incremental_num:
            pass
          else:
            for i in range(incremental_num):
              allay_dots[i][3] = False
            dots = [dot for dot in dots if dot[3]]
        pygame.display.update()
        
    if not response_pressed:
      records['response'].append(0)
      
    for dot in dots:
      # location predition 
      temp_x = dot[0][0] + dot[1] * dot[2][0]
      temp_y = dot[0][1] + dot[1] * dot[2][1]
      # check if the loction in next frame go beyond the boundary, then reverse the direction
      if not ((temp_x-circle_x)**2 + (temp_y-circle_y)**2 <= (boundsize/2)**2):
        direction_randomness = 0.25*numpy.random.randn(2) 
        dot[2] = [-_+direction_randomness[i] for i, _ in enumerate(dot[2])] 
      # update the loction
      dot[0][0] += dot[1] * dot[2][0] 
      dot[0][1] += dot[1] * dot[2][1]
      # # velocity 
      velocity_randomness = float(0.15*(numpy.random.rand(1)-0.5))
      dot[1] = numpy.clip(dot[1]+velocity_randomness, 1.5, 3.5)

    if initialize:
      for i in range(num_dots - len(dots)):
              
        radius = numpy.random.uniform(0, boundsize/2)
        angle = numpy.random.uniform(0, math.pi*2)
        
        x = circle_x + radius * math.cos(angle)
        y = circle_y + radius * math.sin(angle)
        
        speed = numpy.random.uniform(2, 2.5)
        direction = random.choice([[-1, 0], [1, 0], [0, -1], [0, 1], [numpy.sqrt(2)/2, numpy.sqrt(2)/2], [numpy.sqrt(2)/2, -numpy.sqrt(2)/2], [-numpy.sqrt(2)/2, numpy.sqrt(2)/2], [-numpy.sqrt(2)/2, -numpy.sqrt(2)/2]])
        color = dots_colors[int(numpy.random.choice([0,1]))]
        
        dots.append([[x, y], speed, direction, True, color])
      initialize = 0
    # every state_window check the state
    if loop_idx % num_bin == 0:
      # compare number of colored dots
      dotcolors = [ _[-1] for _ in dots ]
      num_0 = len([ _ for _ in dotcolors if _ ==dots_colors[0] ])
      num_1 = len([ _ for _ in dotcolors if _ ==dots_colors[1] ])
      cur_diff = numpy.abs(num_0 - num_1)
      # determine the loser color
      if num_0 == num_1:
          loser_color = dots_colors[int(numpy.random.rand() < 0.5)] # if less than 0.5 -> 1;
      else:
          loser_color = dots_colors[int(num_0 > num_1)] # if num_0 bigger than num_1 then 1 
      # define kill number
      loser_dots = [dot for dot in dots if dot[4]==loser_color]
      kill_num = math.ceil(base_decay*len(loser_dots))
      # base_decay += 0.005*(loop_idx//num_bin)
      base_decay = numpy.max([0.005, 0.1*kill_num/(len(dots)+1e-10)])
      # incremental_num = int(numpy.log(0.3*kill_num+1))
      
    # kill
    delta_bin = round(num_bin/(kill_num + 1e-10))
    if loop_idx % delta_bin == 0:
      # random the order of loser dots
      loser_dots = [dot for dot in dots if dot[4]==loser_color]
      loser_dots[0][3] = False
      # remove the killed dots
      dots = [dot for dot in dots if dot[3]]
    # background
    screen.fill((0,0,0))
    allay_dots = ([ _ for _ in dots if _[-1] ==dots_colors[0] ])
    enemy_dots = ([ _ for _ in dots if _[-1] ==dots_colors[1] ])
    records['allaydotnum'].append(len(allay_dots))
    records['enemydotnum'].append(len(enemy_dots))
    records['killnum'].append(kill_num)
    records['basedecay'].append(base_decay)
    if len(allay_dots) ==0 or len(enemy_dots) ==0:
      records['v_allay'].append((numpy.nan, numpy.nan))
      records['v_enemy'].append((numpy.nan, numpy.nan))
    else:
      records['v_allay'].append((numpy.mean([dot[1] for dot in allay_dots]), numpy.std([dot[1] for dot in allay_dots])))
      records['v_enemy'].append((numpy.mean([dot[1] for dot in enemy_dots]), numpy.std([dot[1] for dot in enemy_dots])))
    if len(dots) == 0 or len(allay_dots)==0 or len(enemy_dots) == 0:
      numpy.save(f'{current_path}/RD_{name}_record{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.numpyy', numpy.array([records]))
      print('==========saved!=============')
      break
    # draw dots
    for i, dot in enumerate(dots):    
      pygame.draw.circle(screen, dot[4], dot[0], dot_size)  
     
    # 反馈当前已经坚持的时间：
    font = pygame.font.Font(f"{current_path}\Deng.ttf", 32)
    sustain_time = round((time.time() - task_begin) * 100)/100
    feedback_text = font.render(f'已坚持 {sustain_time} 秒', True, (255, 255, 255))
    screen.blit(feedback_text, (screen_width/2-100, 125))
    # feedback numbers
    if check:
      font = pygame.font.Font(None, 32)
      text = font.render("#Red: " + str(num_1) + '\\n' + "#Blue:"+str(num_0)+"idxchange"+str(idx_change)+'loop'+str(loop_idx), True, (255,255,255))
      # text = font.render("#Red: " + str(len([ _ for _ in dotcolors if _ ==dots_colors[1] ])) + '\\n' + "#Blue:"+str(len([ _ for _ in dotcolors if _ ==dots_colors[0] ]))+"killsnum"+str(kill_num)+'loop'+str(loop_idx), True, (255,255,255))

      screen.blit(text, (10, 10))
      # 屏幕交互相关设计   
    # 1. 初始化按钮对象
    if records['response'][-1] == 0:
      button_color1 = (110, 110, 110)
      button_color2 = (60, 60 ,60)
    elif records['response'][-1] == 1:
      button_color1 = (255, 255, 0)
      button_color2 = (60, 60 ,60)
    elif records['response'][-1] == -1:
      button_color1 = (110, 110, 110)
      button_color2 = (255, 255, 0)
    increase_btn = pygame.Rect(350, 700, 100, 50)
    decrease_btn = pygame.Rect(450, 700, 100, 50)
    # 2. 在屏幕上绘制两个按钮 
    pygame.draw.rect(screen, button_color1, increase_btn)
    pygame.draw.rect(screen, button_color2, decrease_btn)
    # 3. 按钮的意义说明
    # 3.1 按钮的icon尺寸设计
    font = pygame.font.Font(None, 48)
    plus_text = font.render("+", True, (255, 255, 255))
    minus_text = font.render("-", True, (255, 255, 255))
    plus_text = pygame.transform.scale(plus_text, (32, 32))
    minus_text = pygame.transform.scale(minus_text,(32, 32))
    
    plus_width = plus_text.get_width()
    plus_height = plus_text.get_height()
    
    minus_width = plus_text.get_width()
    minus_height = plus_text.get_height()
    
    plus_x = increase_btn.x + (increase_btn.width - plus_width) / 2
    plus_y = increase_btn.y + (increase_btn.height - plus_height) / 2

    minus_x = decrease_btn.x + (decrease_btn.width - minus_width) / 2
    minus_y = decrease_btn.y + (decrease_btn.height - minus_height) / 2

    screen.blit(plus_text, (plus_x, plus_y)) 
    screen.blit(minus_text, (minus_x, minus_y)) 
    
    pygame.display.update()
    pygame.display.flip()
    time.sleep(interval)
    
    loop_idx += 1
    
    # totoal time control
    if count >= total_time:
        numpy.save(f'{current_path}/RD_{name}_record{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.numpyy', numpy.array([records]))
        print('==========saved!=============')
        break
    
pygame.quit()