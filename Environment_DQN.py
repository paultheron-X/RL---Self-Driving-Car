import pygame
from pygame.locals import *
from game_utils.utils_track import *
from game_utils.car import *
from game_utils.constants import *
from game_utils.geometry import *
from qlearning.DeepQN import DQNAgent
import time


successes, failures = pygame.init()
print("{0} successes and {1} failures".format(successes, failures))

# Game intialisation
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

track = Track(screen)
driver = Car(screen, track)

agent = DQNAgent(state_space = NUM_RAYS+1, 
                 action_space = NUM_ACTIONS, 
                 dropout = 0,  
                 hidden_size= 256,
                 pretrained = False, 
                 lr = 0.001, 
                 gamma=0.99, 
                 max_mem_size = 30000, 
                 exploration_rate = 1, 
                 exploration_decay = .9995, 
                 exploration_min = 0.1,  
                 batch_size = 512)

# Animation Loop
game_reward = []
current_reward = 0
counter = 0
countersuper = 0

while True:
    clock.tick()
    screen.fill(BLACK)
    
    driver.replace(True)
    counter = 0
    state, terminal = driver.get_observations()
    current_reward = 0
    issue = state.copy()
    while not terminal:
        t1 = time.time()
        countersuper +=1
        
        #if countersuper % 5 ==0:
        for event in pygame.event.get():                # handle keybord events
            if event.type == pygame.QUIT:
                agent.save("results/NN")
                quit()  
            elif event.type == pygame.KEYDOWN:
                driver.modify(event)
    
        recom_action = agent.act(issue)
    
        old_state, issue, reward, action_chosen, terminal = driver.act(recom_action)
        
        
        '''if terminal or current_reward==-1:
            print(reward)'''
    
        if reward == 0:  # To kill cars that haven't been rewarded in last 100 games
            counter += 1
            if counter > 1000:
                terminal = True
                reward = REWARD_WALL
        else:
            counter = 0
        
        countersuper +=1
        
        '''print("\nnumber", countersuper)
        print("old_state",old_state)
        print("issue", issue)
        print("reward", reward)
        print("action", action_chosen)
        print("terminal", terminal )'''
        
        agent.remember(old_state, action_chosen, reward, issue, terminal)
        
        
        agent.driving_lessons()
        
        track.draw_track()
        driver.draw_car(screen)
        #driver.print_car()
        pygame.display.update()


        current_reward += reward
        t2 = time.time()
    
    # >>> The car has crashed  
   # print("kill")
    game_reward.append(current_reward)
    ind = len(game_reward)
    if ind % REPLACE_TARGET == 0 and ind > REPLACE_TARGET:
            agent.update_params()
    if ind % 10 ==0:                    # print current learning infos every 10 games
        avg = np.mean(game_reward[max(ind-100, 0):ind])
        print("> Game Numer : " + str(ind) + " | Last Game Reward = " + str(current_reward) + " | Average R on 100 last games : " + str(avg) + " | Exploration rate : " + str(agent.get_exploration()) + " | Current FPS : " + str(round(1/(t2-t1))))

