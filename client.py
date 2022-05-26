#imports
import pygame
import socket
from _thread import *
import json
import time
from cytolk import tolk
tolk.load()
from cytolk.tolk import speak

#a class for game
class game:
    def __init__(self):
        pygame.init()
        self.window=pygame.display.set_mode()
        pygame.display.set_caption("Rock, Paper and syzer")
        self.c=-1 #choice
        self.choices=['rock','paper','syzer'] #list of posible choices
        self.turn=False #tells if it's our turn
        self.start=False #tells if the game is started
        self.winner="" #tells the winner
        self.s=socket.socket()
        self.s.connect(('localhost', 54321))
    def pump(self): #din't know what to call this, a method to handle requests/responses
        while 1:
            data=self.s.recv(1024).decode()
            if data != '': # not empty data
                packet=json.loads(data) #load the json data in to a dict
                if packet['action'] == 'turn': #if action is to make it our turn
                    self.turn=True #it's our turn
                if packet['action'] == 'start': #if start in data
                    self.start=True #game has started
                if packet['action'] == 'winner': #if winner is announced
                    self.winner=packet['winner'] #set the game winner as winner sent by server
    def message(self, message): #a function to display any message
        time.sleep(0.005)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit()
            if event.type == pygame.KEYDOWN:
                if event.key >= pygame.K_RIGHT and event.key <= pygame.K_UP: speak(message)
                if event.key == pygame.K_RETURN: return True
    def query(self, question): #a yes or no query function
        index=0
        opts=['yes','no']
        speak(question)
        while 1:
            time.sleep(0.005)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE: speak(question)
                    if event.key == pygame.K_UP:
                        index=0
                        speak(opts[index])
                    if event.key == pygame.K_DOWN:
                        index=1
                        speak(opts[index])
                    if event.key == pygame.K_RETURN:
                        if index == 0: return True
                        else: return False
    def loop(self): # a main loop to handle the game
        start_new_thread(self.pump, ()) #a thread to listen and respond for responses
        while 1:
            time.sleep(0.005)
            while not self.start: #display a message if game is not started
                self.message('the game hasnt started yet')
            while not self.turn: #display a message if it's not our turn
                self.message('please wait, its not your turn yet')
            while not self.winner == "": #display the winner if announced
                self.message(f'{self.winner} is the winner')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.s.close()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key >= pygame.K_1 and event.key <= pygame.K_3 and self.c < 0:
                        c=event.key - pygame.K_1
                        q=self.query(f'you chose {self.choices[c]}. do you want to confirm?')
                        if q:
                            self.c=c
                            #send our choice to server
                            packet={"action":"choice","choice":self.c}
                            packet=json.dumps(packet)
                            packet=packet.encode()
                            self.s.sendall(packet)
                        
            

def main():
    g=game() #new game object
    g.loop()

if __name__ == "__main__":
    main()