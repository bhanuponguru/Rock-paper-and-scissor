#imports
import pygame
import socket
from _thread import *
import json
import time
from cytolk import tolk
tolk.load()
from cytolk.tolk import speak

pygame.init()
import menu

#a class for game
class game:
    def __init__(self, host="localhost", port=54321):
        self.c=-1 #choice
        self.choices=['rock','paper','scissor'] #list of posible choices
        self.turn=False #tells if it's our turn
        self.start=False #tells if the game is started
        self.winner="" #tells the winner
        self.s=socket.socket()
        self.s.connect((host, port))
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
        m=menu.menu(question,["yes","no"])
        result = m.run()
        if result == "yes": return True
        else: return False
    def loop(self): # a main loop to handle the game
        start_new_thread(self.pump, ()) #a thread to listen and respond for responses
        while 1:
            time.sleep(0.005)
            if not self.start: #display a message if game is not started
                self.message('the game hasnt started yet')
            elif not self.turn: #display a message if it's not our turn
                self.message('please wait, its not your turn yet')
            elif not self.winner == "": #display the winner if announced
                self.message(f'{self.winner} is the winner')
            else:
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
    window=pygame.display.set_mode()
    pygame.display.set_caption("Rock, Paper and scissor")

    m=menu.menu("main menu: use your up and down arrows to navigate through the menu, and press enter to select the focused option.", ["start game","exit"])
    result=m.run()
    if result == "start game":
        g=game() #new game object
        g.loop()
    else:
        pygame.quit()
        quit()

if __name__ == "__main__":
    main()