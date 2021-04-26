import pygame
from constants import *
import random, math
import numpy as np

class Player:
    def __init__(self, game, image, x=0, y=0, frames=1, directions=[""], flip=False):
        self.game = game
        if len(directions) == 1:
            frames = [frames]
        self.images = {d:game.loadImage(image+d+".png", f, flip=flip) for d, f in zip(directions,frames)}
        self.frames = frames[0]
        self.x = x
        self.y = y
        self.type = image
        self.remove = False
        self.t0 = self.game.t
        self.direction = directions[0]
        self.speed = SPEED
        self.imw = self.images[directions[0]][0].get_width()
        self.imh = self.images[directions[0]][0].get_height()
        self.repeat = True
        self.start = True
        self.sound = False
        self.static = False
        if image == "Guard" or image == "Guard2" or image == "Thrower":
            self.number = [int(random.random()*10), int(random.random()*10)]
            self.font = pygame.font.Font("font/LCD_Solid.ttf", 18)
            self.speed = 0.5
            self.dx = self.game.player.x - self.x
            self.dy = self.game.player.y - self.y
            self.static = True
        if image == "Runner":
            self.number = [4,8]
            self.font = pygame.font.Font("font/LCD_Solid.ttf", 18)
        if image == "Thrower":
            self.start = False
            self.repeat = False
        if image == "Football":
            self.start = False
        if image == "House":
            self.static = True
        if image == "Car" or image == "Penguin":
            self.dx = -1 if flip else 1
        if image == "Tumbleweed":
            self.dy = -(self.y - self.game.y - HEIGHT/2)/2
            self.dx = -(self.x-WIDTH/2)/2
        if image == "RiverWaves" or image == "RiverBank" or image == "Tree" or image == "Cactus" or image == "Waves" or self.type=="Rock" or self.type=="Squid" or self.type=="Icepit":
            self.static = True
        if image == "Boat":
            self.static = True
            self.start = False
            self.boarded = False
            self.unboarded = False

    def draw(self, surface, t):
        if self.type == "Runner":
            if self.game.state == "rewind" or self.game.state == "throw":
                self.direction = "Catch"
                self.frames = 1
            elif self.game.state == "play" and self.game.boat and self.game.boat.boarded:
                self.direction = "3"

        if not self.start or (self.game.state != "play" and self.type!="Thrower" and self.type!="Football"):
            i = 0
        elif not self.repeat:
            i = min(int((t-self.t0)*FRAME_RATE/1000), self.frames-1)
        else:
            i = int((t-self.t0)*FRAME_RATE/1000) % self.frames


        surface.blit(self.images[self.direction][i], (self.x-self.imw/2, self.y-self.game.y-self.imh/2))
        if self.type == "Guard" or self.type == "Runner" and (self.direction=="" or self.direction =="3") or self.type == "Thrower":
            num = self.font.render(str(self.number[0])+str(self.number[1]), True, (255,255,255))
            surface.blit(num, (self.x-14,self.y-8-self.game.y))
        elif self.type == "Guard2":
            num = self.font.render(str(self.number[0])+str(self.number[1]), True, (255,255,255))
            surface.blit(num, (self.x-14,self.y-12-self.game.y))


    def move(self, dx, dy, dt):
        self.x += dx*SPEED*dt/1000
        self.y += dy*SPEED*dt/1000

    def correct(self):
        if self.x > WIDTH - 50:
            self.x = WIDTH-50
        if self.x < 50:
            self.x = 50
        if self.y - self.game.y < 100:
            self.y = self.game.y + 100
        if self.y -self.game.y > HEIGHT-80:
            self.y = self.game.y + HEIGHT-80

    def update(self, dt, dy=0):
        if -self.y < -self.game.y - HEIGHT - 100 or -self.y > -self.game.y + HEIGHT:
            if not self.static:
                self.remove = True
        if not self.sound and self.y - self.game.y < HEIGHT + 100 and self.y - self.game.y >-100 and self.x < WIDTH + 100 and self.x > -100:
            self.sound = True
            if self.type == "Penguin":
                self.game.playSound("Slide.wav")
            elif self.type == "RiverWaves":
                self.game.playSound("River.wav")
            elif self.type == "Car":
                self.game.playSound("Car.wav")


        if self.type == "Guard" or self.type == "Guard2":
            d = math.sqrt(self.dx**2+self.dy**2)
            if -self.y < 2850 - HEIGHT:
                self.move(self.dx/d*self.speed, self.dy/d*self.speed-dy*.75, dt)
            else:
                self.frames = 1
            self.collide_player(66, 92, dt)
        if self.type == "Football":
            if self.y > self.game.player.y:
                self.move(-self.dx/self.dy*dy, -dy, dt)
            if self.y <= self.game.player.y:
                self.y = self.game.player.y
                self.repeat = False
        if self.type == "Car" or self.type == "Penguin":
            self.move(self.dx/2, 0, dt)
            self.collide_player(self.imw, self.imh/2, dt)
        if self.type == "House":
            self.collide_player(202, 100, dt, bounce=True)
        if self.type == "RiverWaves":
            self.x = WIDTH*((self.game.t/1000)%1)
        if self.type == "Waves":
            self.x = WIDTH/10*np.sin(self.game.t/500) + WIDTH/2
        if self.type == "Tree":
            self.collide_player(60, 44, dt, bounce=True)
        if self.type == "Cactus" or self.type=="Rock" or self.type=="Squid" or self.type == "Icepit":
            self.collide_player(self.imw, self.imh/2, dt, bounce=True)
        if self.type == "Log":
            self.bridge(100,0)
        if self.type == "Tumbleweed":
            d = math.sqrt(self.dx*self.dx+self.dy*self.dy)*4
            self.move(self.dx/d, self.dy/d, dt)
            self.collide_player(self.imw, self.imh, dt)
        if self.type == "Boat":
            if self.boarded:
                if -self.y + self.voyageStart > 700*10-100:
                    self.boarded = False
                    self.unboarded = True
                else:
                    self.x = self.game.player.x
                    self.y = self.game.player.y
            elif not self.unboarded:
                self.bridge(100,0)
                if self.game.player.y <= self.y:
                    self.boarded = True
                    self.start = True
                    self.voyageStart = self.y
                

    def collide_player(self, w, h, dt, dx0=0, dy0=0, bounce=False):
        dx = self.game.player.x - self.x - dx0
        dy = self.game.player.y - self.y - dy0
        collide = (dx/(w/2+60/2))**2 + (dy/(h/2+86/2))**2
        if collide < 1:
            if bounce:
                if abs(dx) > dy*1.2:
                    self.game.player.move(np.sign(dx),0,dt)
                    return
            self.game.collide = True
            self.speed = 0
            self.frames = 1

    def bridge(self, w, h, dx0=0, dy0=0):
        dx = self.game.player.x - self.x - dx0
        dy = self.game.player.y - self.y - dy0
        collide = abs(dx/(w/2+60/2)) > 1 and abs(dy/(h/2+86/2)) < 1
        if collide:
            self.game.collide = True
            self.speed = 0
            self.frames = 1

    def begin(self, t):
        if not self.start:
            self.t0 = t
            self.start = True
            self.dx = self.game.player.x - self.x
            self.dy = self.game.player.y - self.y