import pygame
from cytolk.tolk import speak

class menu:
    def __init__(self, title, choices):
        self.title = title
        self.choices = choices
        self.index=0
    def run(self):
        running=True
        speak(self.title)
        while  running:
            for  event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.index > 0:
                        self.index-=1
                        speak(self.choices[self.index])
                    if event.key == pygame.K_DOWN and self.index < len(self.choices) - 1:
                        self.index+=1
                        speak(self.choices[self.index])
                    if event.key == pygame.K_SPACE: speak(self.title)
                    if event.key == pygame.K_RETURN: return self.choices[self.index]