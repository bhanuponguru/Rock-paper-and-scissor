import pygame
import socket
import json
from _thread import *
from cytolk import tolk
tolk.load()
from cytolk.tolk import speak

class game:
    def __init__(self):
        pygame.init()
        self.screen=pygame.display.set_mode()
        pygame.display.set_caption("Rock, paper and scissor")
        self.selected_choice=-1
        self.choices=['rock','paper','scissor']
        self.winner=""
        self.turn=False
        self.started=False
        self.s=socket.socket()
        self.connected=False
    def connection_loop(self):
        if not self.connected:
            speak('connecting...')
            self.s.connect(('localhost', 54321))
            self.connected=True
        while 1:
            
    def message_loop(self, message):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    speak(message)
    def make_packet(self, data):
        packet=json.dumps(data)
        return packet.encode()
    def get_data(self, packet):
        data=json.loads(packet.decode())
        return data
    def main_loop(self):
        start_new_thread(self.connection_loop, ())
        while 1:
            if self.started and self.selected_choice < 0:
                index=0
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_DOWN:
                            if index < 2: index+=1
                            speak(self.choices[index])
                        if event.key == pygame.K_UP:
                            if index > 0: index-=1
                            speak(self.choices[index])
                        if event.type == pygame.K_RETURN:
                            self.selected_choice=index
                            packet=make_packet({'action':'choice','choice':self.selected_choice})
                            self.s.sendall(packet)
            if self.started and not self.turn:
                self.message_loop("please wait, it's not your turn yet")
            if not self.started:
                self.message_loop("the game has not started yet")

def main():
    g=game()
    g.main_loop()

if __name__ == "__main__": main()