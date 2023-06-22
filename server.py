#imports
import socket
import threading
from _thread import *
import json

#a thread to handle clients
class client(threading.Thread):
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.s=conn
        self.addr=addr
        self.c=-1 #choice
        self.id=None #game id
        self.turn=False #tells if it is current player's turn or not
        self.disconnected=False #will bee true if client disconnects
    def run(self): #replacing threading's run method
        print(f'new connection: {self.addr}\n')
        while 1:
            try:
                data = self.s.recv(1024).decode()
                if data != '':
                    packet=json.loads(data)
                    if packet['action'] == 'choice':
                        print(packet['choice'], '\n')
                        self.c=packet['choice']
                        self.turn=False
                if data == '':
                    self.disconnect()
                    break
            except socket.error as e:
                print(e)
                self.disconnect()
                break
    def disconnect(self):
        self.s.close()
        self.disconnected=True
        print(f'disconnected: {self.addr}')

#a class to conduct a game between 2 players
class game:
    def __init__(self, player1, id):
        self.player1=player1
        self.player2=None
        self.id=id
        self.completed=False #weather game is completed or not
        self.player1.id=self.id #set player1 id to current game id
        self.player1.turn=True #player1 plays first
    def loop(self): #a loop for the game
        self.evaluate()
        if not self.player2.turn and not self.player1.turn:
            self.player2.s.sendall(b'{"action":"turn"}')
            self.player2.turn=True
    def evaluate(self): #a function to return the winner if game is completed
        if self.player1.c >= 0 and self.player2.c >= 0 and not self.completed:
            self.completed=True #game will bee completed when both the player have a choice
            #evaluate the winner based on numerical value of choice
            #for example, when player1 chose rock and player2 chose paper, then player1.c = 0 and player2.c = 1. we know that in this case paper is the winner. value of paper is 1. value of rock is 0. when we subtract player1.c and player2.c, we get -one. same works with paper and scissor too.
            #and when player2 chose rock and player1 chose scissor, we know rock is the winner. that means player1.c = 2 and player2.c = 0. so player1 - player2 must give 2.
            if self.player1.c - self.player2.c == -1 or self.player1.c - self.player2.c == 2:
                #send the winner to both the players.
                self.player1.s.sendall(b'{"action":"winner","winner":"player2"}')
                self.player2.s.sendall(b'{"action":"winner","winner":"player2"}')
            #same logic, but in opposit way.
            elif self.player1.c - self.player2.c == 1 or self.player1.c - self.player2.c == -2:
                self.player1.s.sendall(b'{"action":"winner","winner":"player1"}')
                self.player2.s.sendall(b'{"action":"winner","winner":"player1"}')
            else: #if no one is the winner
                self.player1.s.sendall(b'{"action":"winner","winner":"no one"}')
                self.player2.s.sendall(b'{"action":"winner","winner":"no one"}')


#a main class for server which handles all games and client connections.
class server:
    def __init__(self, port=54321):
        self.s=socket.socket()
        self.s.bind(('', port))
        self.clients=[] #list of clients
        self.games=[] #list of games.
        #an index which will bee increased at each game creation. this will bee asigned as the id of the newly created game.
        self.index=0
        #if single client is connected to newly created game, before it is appended to games list, it will bee stored in wgame (waiting game) for second client to connect. when second client also connects, wgame will bee freed and game will bee appended to self.games.
        self.wgame=None
        #listen for connections
        self.s.listen()
    def gameloop(self): #a loop to handle all games.
        while 1:
            if self.wgame:
                if self.wgame.player1.disconnected:
                    self.wgame.player1=None
                    self.wgame=None
            for g in self.games: #each and every instance of the game
                g.loop() #loop the game
                if g.player1.disconnected or g.player2.disconnected: #if any player has disconnected
                    g.player1=None
                    g.player2=None
                    self.games.remove(g)
    def loop(self): #main server loop
        start_new_thread(self.gameloop, ()) #a thread to handle game loop
        while 1:
            conn, addr = self.s.accept() #accept connection
            c=client(conn, addr) #new client thread
            if self.wgame: #if there is a waiting game
                self.wgame.player2=c #set this player as second player
                self.wgame.player2.id=self.wgame.id #set game id of this player
                #send start message to both the players
                self.wgame.player1.s.sendall(b'{"action":"start"}')
                self.wgame.player2.s.sendall(b'{"action":"start"}')
                #send player1 saying it's his/her turn
                self.wgame.player1.s.sendall(b'{"action":"turn"}')
                #append the game to self.games
                self.games.append(self.wgame)
                #clear waiting game
                self.wgame=None
            else: #there are no waiting games
                self.index+=1 #increase the index
                g=game(c, self.index) #create a new game
                self.wgame=g #set this game as waiting game
            self.clients.append(c) #append current client to clients list
            c.start() #start this thread for handling this client


if __name__ == "__main__":
    s=server() #new server instance
    start_new_thread(s.loop, ()) #thread to handle server
    while 1: #a loop to accept server admin's commands
        cmd=input('enter a command\n') #input a command
        #process admin's commands
        if cmd == 'quit':
            break
            quit()