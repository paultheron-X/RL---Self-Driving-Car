import os, sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from matplotlib.pyplot import get
import pygame
import torch
import torch.nn as nn
import numpy as np
from game_utils.car import * 
from game_utils.constants import *
import random
import pickle 
import copy
from collections import *


torch.manual_seed(1000)
class IndividualBrain(nn.Module):
    def __init__(self, screen, track, input_size = NUM_RAYS_GENETIC+1, n_actions = NUM_ACTIONS , hidden_s1 = 15, hidden_s2 = 15) -> None:
        super().__init__()
        self.car = Car_evo(screen, track)
        self.input_size =input_size
        self.n_actions = n_actions
        self.hidden_s1 =hidden_s1
        self.hidden_s2 =hidden_s2
        self.screen = screen
        self.track = track
        
        self.nn = nn.Sequential(
             OrderedDict([
                ('input' , nn.Linear(input_size, hidden_s1)),
                ('relu1' , nn.ReLU()),
                ('hidden' , nn.Linear(hidden_s1, hidden_s2)),
                ('relu2' , nn.ReLU()),
                ('output' , nn.Linear(hidden_s2, n_actions)),
                ('sigm' , nn.Softmax())]
            )
        )
        self.nn.apply(self.init_weights)
        
    def init_weights(self, m):
         if isinstance(m, nn.Linear):
            #torch.nn.init.normal_(m.weight, mean = 0, std =1.5)
            #torch.nn.init.normal_(m.bias, mean = 0, std =1.5)
            torch.nn.init.uniform_(m.weight, a = -3, b =3)
            torch.nn.init.uniform_(m.bias, a = -3, b =3)
            
        
    def forward(self, x):
        res = self.nn(x)
        return res
    
    def cross(self, partner):
        child = IndividualBrain(self.screen, self.track, self.input_size, self.n_actions, self.hidden_s1, self.hidden_s2)
        mother_dic = self.get_dict()
        father_dic = self.get_dict()
        
        child_dic = mother_dic.copy()
        
        key_tab = mother_dic.keys()
        key_tab = [(key.split(".")[0], key.split(".")[1] ) for key in key_tab]
        
        if random.randint(0, 8) == 1:
            mutation_rate = 10
        else:
            mutation_rate = 100000000 # Infinity -> no mutation
        
        mutation_rate = 2
        
        for i, (level, type_) in enumerate(key_tab):
            if type_ == "weight":
                tens_ = child_dic[level + "." + type_].clone()
                for i,elem in enumerate(tens_):
                    for j, num in enumerate(elem):
                        p = random.random()
                        if p > 0.5:
                            tens_[i][j] = mother_dic[level + "." + type_][i][j]
                        else:
                            tens_[i][j] = father_dic[level + "." + type_][i][j]

                    # Mutate
                        if random.randint(0, mutation_rate) == 1:
                            tens_[i][j] += 4*random.random() - 2
        
                child_dic[level + "." + type_] = tens_.clone()
                                
            if type_ == "bias":
                tens_ = child_dic[level + "." + type_].clone()
                for i,elem in enumerate(tens_):
                    p = random.random()
                    tens_[i] = p * mother_dic[level + "." + type_][i] + (1 - p) * father_dic[level + "." + type_][i]
                    if random.randint(0, mutation_rate) == 1:
                        tens_[i] += 4*random.random() - 2
                child_dic[level + "." + type_] = tens_.clone()
        
        for old_key in child_dic.copy().keys():
            child_dic["nn."+old_key] = child_dic.pop(old_key)
        
        child.load_state_dict(child_dic)
        return child
    
    def get_car(self):
        return self.car
    
    def get_dict(self):
        return self.nn.state_dict().copy()

    
class Evolution():
    def __init__(self,screen, track, nb_indiv = 250) -> None:
        self.nb_indiv = nb_indiv
        self.list_indiv = [IndividualBrain(screen, track) for i in range(nb_indiv)]
        self.scores = np.zeros(nb_indiv)
        self.dead = np.zeros(nb_indiv)
        self.decision = np.zeros(nb_indiv)  # To check if an agent has scored moved in the last 150 ticks 
        self.last_rew = np.zeros(nb_indiv)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.last_best_car = IndividualBrain(screen, track)
        self.last_best_score = -2
            
    # After having selected the 10% best of the previous gen
    def cross(self, best):
        new_indiv = []
        nb_best = len(best)
        for i in range(self.nb_indiv):
            idx1 = random.randint(0,nb_best-1)
            idx2 = random.randint(0,nb_best-1)
            new_indiv.append(best[idx1].cross(best[idx2]))
        return new_indiv
            
    
    def generate_next_pop(self):
        argm = np.argmax(self.scores)
        valm = self.scores[argm]
        print("     > Scores for this gen are " + str(self.scores))
        print("     > Best score for this gen is " + str(valm))
        print("         > Crossing for new population ")
        best_people =[]
        coef = 0.9
        
        best_people = [copy.copy(elem) for (i,elem) in enumerate(self.list_indiv) if self.scores[i] >= coef * valm]
        
        if self.last_best_score > valm:
            best_people.append(copy.copy(self.last_best_car))
        else:
            self.last_best_score = valm
            self.last_best_car = copy.copy(self.list_indiv[argm])
        
        if len(best_people)<2:
            best_people.append(copy.copy(best_people[0]))
        
        self.list_indiv = self.cross(best_people)
        print("         > Crossing done ")
        self.scores = np.zeros(self.nb_indiv)
        
        self.dead = np.zeros(self.nb_indiv)
        self.decision = np.zeros(self.nb_indiv)
        self.last_rew = np.zeros(self.nb_indiv)
         
    def get_observations(self):
        state_ = []
        terminal_ = []
        for i,elem in enumerate(self.list_indiv):
            if self.dead[i] == 0:
                state, terminal = elem.car.get_observations()
                state_.append(state)
                terminal_.append(terminal)
            else:
                state, terminal = None, 1
                state_.append(state)
                terminal_.append(terminal)
                
        return state_.copy(), terminal_.copy()
    
    def predict_action(self, state):
        recom = []
        for i,elem in enumerate(self.list_indiv):
            if self.dead[i] == 0:
                state_ = torch.from_numpy(state[i]).float()
                action_ = elem.nn(state_.to(self.device)).argmax().unsqueeze(0).unsqueeze(0).cpu()
                recom.append(action_.item())
            else:                    
                recom.append(None)
        return recom
        
    
    def act(self, actions):
        state_ = []
        issue_ = []
        reward_ = []
        action_chosen_ = []
        terminal_ = []
        #print("dec",self.decision)
        for i,elem in enumerate(self.list_indiv):
            if self.decision[i] >= 150: 
                state_.append(None)
                issue_.append(None)
                reward_.append(0)
                action_chosen_.append(None)
                terminal_.append(1)
                self.dead[i]=1
            
            elif self.dead[i] == 0:
                state, issue, reward, action_chosen, terminal = elem.car.act(actions[i])
                state_.append(state)
                issue_.append(issue)
                reward_.append(reward)
                action_chosen_.append(action_chosen)
                terminal_.append(terminal)
                self.scores[i] += reward
                self.dead[i] = terminal
                self.last_rew[i] = reward
                if reward == 0:
                    self.decision[i] +=1
                else:
                    self.decision[i] =0
                
            else:
                state_.append(None)
                issue_.append(None)
                reward_.append(0)
                action_chosen_.append(None)
                terminal_.append(1)
        return state_, issue_, reward_, action_chosen_, terminal_

    def draw(self, screen):
        best_people = [(i,elem) for (i,elem) in enumerate(self.list_indiv)]# if self.scores[i] >= 0.9 * np.max(self.scores)]
        for j, (i,elem) in enumerate(best_people):
            #if self.dead[i] == 0:
                elem.car.draw_car(screen)

    def save(self, name):
        argm = np.argmax(self.scores)
        valm = self.scores[argm]
        if self.last_best_score > valm:
            torch.save(self.last_best_car, name+ "/Deep_evo.pt")  
        else:
            torch.save(self.list_indiv[argm].get_dict(), name+ "/Deep_evo.pt")  
        print("> Ending simulation | Saving game to path " + name + " | Best score saved : " + str(max(self.last_best_score, valm))) 
        

        
            
            