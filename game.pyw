import pygame
import os, sys, math, random
import numpy as np
from PIL import Image
from constants import *
from player import Player

exe = 1
test = 0

class Game:

    def reset(self, respawn=False):
        ''' Resets the game '''
        self.t = 0
        self.y = 0
        self.level = -1
        self.obstacles = []
        self.decorateTop = []
        self.decorateBottom = []
        self.collide = False
        self.win = False
        self.player = Player(self, "Runner", WIDTH/2, HEIGHT*3/4, [8,1,8], ["", "Catch","3"])
        self.thrower = Player(self, "Thrower", WIDTH/2, HEIGHT*.9, 4)
        self.football = Player(self, "Football", WIDTH/2+30, HEIGHT*7/8-30, 8)
        if not test:
            self.decorateTop.append(Player(self, "FieldGoal", WIDTH/2, -1400*2+HEIGHT/2, 1))
        self.decorateTop.append(Player(self, "FieldGoal", WIDTH/2, -self.borders[-2]+360, 1, directions=["2"]))
        self.boat = False
        self.backfield = self.loadImage("backfield.png",1)[0]
        self.textbubble = self.loadImage("TextBubble.png",1)[0]
        self.ymax = 0
        self.lastBiome = "none"
        self.captionTime = 0
        self.progress = 0
        self.lastCaption = False
        self.captionText = ""

    def ui(self):
        ''' Draws the user interface overlay '''
        if self.state == "pause":
            if self.captionTime > 0:
                self.screen.blit(self.textbubble, (0,HEIGHT - 146))
                caption = self.font4.render(self.captionText, True, (0,0,0))
                self.screen.blit(caption, (WIDTH/2-caption.get_width()/2,HEIGHT-120))
        if self.state == "play":
            if self.level == "Arctic" or self.level == "ArcticCoast" or self.level == "Desert" or self.level == "DesertCoast"or self.level == "OceanCoast":
                caption = self.font.render(str(self.getScore())+" Yards", True, (0,0,0))
            else:
                caption = self.font.render(str(self.getScore())+" Yards", True, (255,255,255))
            self.screen.blit(caption, (10,10))
        elif self.state == "gg":
            if self.win:
                caption = self.font2.render("You made it", True, (255,255,255))
                self.screen.blit(caption, (WIDTH/2-caption.get_width()/2,HEIGHT*.1))
                caption = self.font3.render(str(self.getScore()), True, (255,255,255))
                self.screen.blit(caption, (WIDTH/2-caption.get_width()/2,HEIGHT*.3))
                caption = self.font3.render("Yards", True, (255,255,255))
                self.screen.blit(caption, (WIDTH/2-caption.get_width()/2,HEIGHT*.45))
                caption = self.font3.render("Touchdown!", True, (255,255,255))
                self.screen.blit(caption, (WIDTH/2-caption.get_width()/2,HEIGHT*.7))
                caption = self.font.render("[Press Enter to play again]", True, (255,255,255))
                self.screen.blit(caption, (WIDTH/2-caption.get_width()/2,HEIGHT*.9))
            else:
                caption = self.font2.render("You made it", True, (255,255,255))
                self.screen.blit(caption, (WIDTH/2-caption.get_width()/2,HEIGHT*.1))
                caption = self.font3.render(str(self.getScore()), True, (255,255,255))
                self.screen.blit(caption, (WIDTH/2-caption.get_width()/2,HEIGHT*.3))
                caption = self.font3.render("Yards", True, (255,255,255))
                self.screen.blit(caption, (WIDTH/2-caption.get_width()/2,HEIGHT*.45))
                caption = self.font1.render("But can you go even deeper?", True, (255,255,255))
                self.screen.blit(caption, (WIDTH/2-caption.get_width()/2,HEIGHT*.7))
                caption = self.font.render("[Press Enter to try again]", True, (255,255,255))
            self.screen.blit(caption, (WIDTH/2-caption.get_width()/2,HEIGHT*.9))
        elif self.state == "start":
            caption = self.font3.render("Touchdown", True, (255,255,255))
            self.screen.blit(caption, (WIDTH/2-caption.get_width()/2,HEIGHT*.35))
            caption = self.font.render("[Press Enter to begin]", True, (255,255,255))
            self.screen.blit(caption, (WIDTH/2-caption.get_width()/2,HEIGHT*.6))

    def update(self, dt, keys):
        ''' Updates the game by a timestep and redraws graphics '''
        self.t += dt
        self.captionTime -= dt
        if self.state == "pause" and self.captionTime < 0:
            self.state = "play"
            self.player.direction = ""
        oldy = self.y

        if self.state == "play":
            self.y -= dt*SPEED*SCROLL_SPEED/1000
            self.player.move(0,-SCROLL_SPEED,dt)
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.player.move(0,0.75,dt)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.move(1,0,dt)
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.move(-1,0,dt)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player.move(0,-1,dt)
            self.player.correct()
            if self.player.y < -self.borders[-2]:
                if self.lastCaption:
                    self.state = "win"
                else:
                    self.lastCaption = True
                    self.drawCaption("Catch!")

        elif self.state == "rewind":
            if self.y == 0:
                self.thrower.begin(self.t)
                self.football.begin(self.t)
                self.state = "throw"
            else:
                self.y += dt*SPEED*(ZOOM_SPEED*min(1-self.ymax/SPEED_SCALE,SPEED_MAX))/1000
                if self.y > 0:
                    self.y = 0
        elif self.state == "throw":
            if self.y > self.ymax:
                self.y -= dt*SPEED*THROW_SPEED*min(1-self.ymax/SPEED_SCALE,SPEED_MAX)/1000
            self.football.update(dt, THROW_SPEED*min(1-self.ymax/SPEED_SCALE,SPEED_MAX))
            if not self.football.repeat:
                self.state = "gg"
                self.setVolume(0.4)
        elif self.state == "win":
            self.y -= ZOOM_SPEED*dt*SPEED/1000
            self.win = True
            self.ymax = self.y
            if -self.y > self.borders[-2]+1000:
                self.y += self.borders[-2]+2088
                self.state = "win2"
        elif self.state == "win2":
            self.y -= ZOOM_SPEED*dt*SPEED/1000
            if -self.y > 0:
                self.thrower.begin(self.t)
                self.football.begin(self.t)
                self.state = "throw"

        surface = pygame.Surface((WIDTH, HEIGHT))

        surface.fill((50,150,100))
        surface.blit(self.backfield, (0,-self.y+HEIGHT))
        for i in range(len(self.backgrounds)):
            if -self.y + HEIGHT > self.borders[i] and -self.y < self.borders[i+1]+HEIGHT:
                f = int(self.t*FRAME_RATE/2000) % len(self.backgrounds[i])
                bg = self.backgrounds[i][f]
                b0 = self.borders[i+1]
                surface.blit(bg, (0,-b0+HEIGHT-self.y))
                self.level = self.biomes[i]
        
        biome = 0
        for i in range(len(self.backgrounds)):
            if self.lastBiome == "Field":
                if -self.player.y + HEIGHT > self.borders[i] -600 and -self.player.y < self.borders[i+1]+HEIGHT:
                    biome = self.biomes[i]
            elif -self.player.y + HEIGHT > self.borders[i] and -self.player.y < self.borders[i+1]+HEIGHT:
                if self.biomes[i] == "Field":
                    pass
                else:
                    biome = self.biomes[i]
        captions = ["Go deep!", "Deeper!", "Don't stop!", "Even deeper!", "Keep going!", "DEEPER!", "A little More!", "Almost There!","Perfect!"]
        if self.state == "play":
            if self.lastBiome != biome:
                if biome!="Forest" and biome!="Desert" and biome!="Desert" and biome!="OceanCoast" and biome!="Arctic":
                    self.drawCaption(captions[self.progress])
                    self.progress += 1
                self.lastBiome = biome

        if self.state == "play":
            if self.level == "Field" and (int(oldy/400) > int(self.y/400) or oldy == 0):
                self.spawn(self.level)
            elif int((oldy)/700) > int((self.y)/700):
                if not test:
                    if not (self.level == "Forest" or self.level == "ForestCoast" or self.level == "ArcticForestCoast") or not int((oldy)/1400) == int((self.y)/1400):
                        self.spawn(self.level)
                else:
                    if not (self.level == "Forest" or self.level == "ForestCoast" or self.level == "ArcticForestCoast") or not int((oldy-700)/1400) == int((self.y-700)/1400):
                        self.spawn(self.level)

        for sprite in self.decorateBottom:
            sprite.update(dt, SCROLL_SPEED)
            sprite.draw(surface, self.t)

        for ob in self.obstacles:
            if ob.y >= self.player.y:
                continue
            if self.state == "play":
                ob.draw(surface, self.t)
            else:
                ob.draw(surface, 0)

        if self.boat:
            self.boat.update(dt, SCROLL_SPEED)
            self.boat.draw(surface, self.t)
        self.player.draw(surface, self.t)

        for sprite in self.decorateTop:
            sprite.update(dt, SCROLL_SPEED)
            sprite.draw(surface, self.t)

        self.obstacles = sorted(self.obstacles, key=lambda o:o.y)
        for ob in self.obstacles:
            if ob.y < self.player.y:
                continue
            if self.state == "play":
                ob.draw(surface, self.t)
            else:
                ob.draw(surface, 0)

        self.thrower.draw(surface, self.t)
        self.football.draw(surface, self.t)
        for ob in self.obstacles[:]:
            if self.state == "play":
                ob.update(dt, SCROLL_SPEED)
            if ob.remove:
                self.obstacles.remove(ob)

        if self.state == "play" and self.collide:
            if self.lastCaption:
                self.state = "rewind"
                self.ymax = self.y
            else:
                self.lastCaption = True
                self.drawCaption("Catch!")

        self.screen.blit(surface, (0,0))
        if self.state == "gg":
            surface = pygame.Surface((WIDTH, HEIGHT))
            surface.fill((0,0,0))
            surface.set_alpha(170)
            self.screen.blit(surface, (0,0))
        self.ui()

    def keyPressed(self, key):
        ''' Respond to a key press event '''
        if key==pygame.K_SPACE:
            pass
        if key==pygame.K_RETURN:
            if self.state == "start":
                self.state = "play"
                self.stopMusic()
                self.setVolume(1)
                self.playMusic("Keep_Going.wav")
            if self.state == "gg":
                self.reset()
                self.setVolume(1)
                self.state = "play"

    def addBackground(self, name, frames=1):
        bg = self.loadImage(name+".png",frames)
        self.backgrounds.append(bg)
        self.biomes.append(name)
        self.borders.append(self.borders[-1] + bg[0].get_height())

    def spawn(self, level):
        if level == "Field":
            if -self.y/400 <= 5:
                pos = [(0,0), (1,0), (0,1), (1,1)]
                random.shuffle(pos)
                for i in range(min(2,int(-self.y/400)+1)):
                    p = pos[i]
                    x = p[0]*(WIDTH*(random.random()/2+0.5))
                    y = p[1]*(HEIGHT+60)-30 + self.y
                    if p[1] == 0:
                        self.obstacles.append(Player(self, "Guard2", x, y, 8))
                    else:
                        self.obstacles.append(Player(self, "Guard", x, y, 8))
            self.playSound("Feet.wav")
        if level == "City":
            y = int(self.y/350)*350 - HEIGHT*.75+33
            gap = int(random.random()*3)
            for i in range(4):
                x = 200*i-30
                if gap <= i-1:
                    x += 160
                j = int(random.random()*5)+1
                self.obstacles.append(Player(self, "House", x, y, 1, directions=[str(j)]))
            if random.random() > 0.5:
                x = -100
                y = int(self.y/350)*350 - HEIGHT*.17
                flip = False
            else:
                x = WIDTH+100
                y = int(self.y/350)*350 - HEIGHT*.35
                flip = True
            j = int(random.random()*8)+1
            self.obstacles.append(Player(self, "Car", x, y, 1, directions=[str(j)], flip=flip))
        if level == "Forest" or level == "ForestCoast" or level == "ArcticForestCoast":
            x = WIDTH/2
            y = int(self.y/350)*350 - HEIGHT*2 + HEIGHT*.125
            self.decorateBottom.append(Player(self, "RiverWaves", x, y, 1))
            self.decorateBottom.append(Player(self, "RiverBank", x, y, 1))
            x = random.random()*WIDTH*.5 + WIDTH*.25
            self.decorateBottom.append(Player(self, "Log", x, y, 1))
            grid = self.obstacleGrid(7, 5, 0.6)
            for i in range(5):
                for j in range(7):
                    x = WIDTH*(j/7)+WIDTH/12
                    y = int(self.y/350)*350 - HEIGHT/4*i - HEIGHT*.375
                    if grid[j,i]:
                        dx = (random.random()-0.5)*50
                        dy = (random.random()-0.5)*50
                        self.obstacles.append(Player(self, "Tree", x+dx, y+dy, 1))
        if level == "Desert" or level == "DesertCoast" or level == "OceanCoast":
            self.playSound("Wind.wav")
            for i in range(4):
                j = int(random.random()*3)+1
                x = random.random()*WIDTH
                y = int(self.y/350)*350 - (i+random.random()*.45)*HEIGHT/5 - HEIGHT/10
                self.obstacles.append(Player(self, "Cactus", x, y, 1, directions=[str(j)]))
            for i in range(2):
                rand = int(random.random()*3)-1
                x = WIDTH/2*rand + WIDTH/2 + random.random()*WIDTH/2*(1-abs(rand))
                if rand == 0:
                    y = int(self.y/350)*350-HEIGHT
                else:
                    y = int(self.y/350)*350-HEIGHT + random.random()*HEIGHT
                self.obstacles.append(Player(self, "Tumbleweed", x, y))
        if level == "Ocean":
            self.playSound("Waves.wav")
            x = WIDTH/2
            y = int(self.y/350)*350 - HEIGHT/2
            self.decorateBottom.append(Player(self, "Waves", x, y, 1))
            if not self.boat:
                self.boat = Player(self, "Boat", x, y+HEIGHT*.4, 8)
            else:
                for i in range(4):
                    j = int(random.random()*10)+1
                    x = random.random()*WIDTH
                    y = int(self.y/350)*350 - (i+random.random()*.45)*HEIGHT/5 - HEIGHT/10
                    if j >1:
                        if -self.boat.y + self.boat.voyageStart >= 700*8+100:
                            self.obstacles.append(Player(self, "Rock", x, y, 1, directions=["Ice"]))
                        else:
                            self.obstacles.append(Player(self, "Rock", x, y, 1, directions=[""]))
                    else:
                        self.obstacles.append(Player(self, "Squid", x, y, 8, directions=[""]))
        if level == "Arctic" or level == "ArcticCoast":
            for i in range(4):
                j = int(random.random()*10)+1
                x = random.random()*WIDTH
                y = int(self.y/350)*350 - (i+random.random()*.45)*HEIGHT/5 - HEIGHT/10
                self.decorateBottom.append(Player(self, "Icepit", x, y, 1, directions=[""]))
            yvals = [0,1,2,3,4,5,6,7]
            yvals = np.random.choice(yvals, size=4, replace=False)
            for yval in yvals:
                j = int(random.random()*8)+1
                y = int(self.y/350)*350 - HEIGHT*yval/4
                if yval %2 == 0:
                    x = -100 - random.random()*WIDTH/4
                    flip = False
                else:
                    x = WIDTH+100 + random.random()*WIDTH/4
                    y -= HEIGHT/8
                    flip = True
                self.obstacles.append(Player(self, "Penguin", x, y, 1, flip=flip))



    def obstacleGrid(self, x, y, rate=1):
        grid = np.ones((x,y))
        x0 = int(random.random()*x)
        y0 = 0
        grid[x0,y0] = 0
        lastChoice = 42
        for i in range(y-1):
            choices = [-1, 0, 1]
            if lastChoice!= 42:
                choices.remove(-lastChoice)
            if x0 == x-1:
                choices.remove(1)
            elif x0 == 0:
                choices.remove(-1)
            choice = random.choice(choices)
            if i==0:
                choice = 0
            lastChoice = choice
            x1 = x0 + choice
            y1 = y0+1
            grid[x1,y1] = 0
            grid[x1,y0] = 0
            x0, y0 = x1, y1
        return grid*np.random.random(grid.shape) > (1-rate)

    def getScore(self):
        y = -self.player.y
        scoreMax = 43800000
        yMax = self.borders[-2]
        yMin = 3500
        if y < yMin:
            yards = y/40 + 13
        else:
            y = y-yMin
            yMax = yMax - yMin
            yards0 = yMin/40+13
            ratio = y/yMax

            rate = math.pow(2, ratio*np.log2(scoreMax))
            yards = y/40 + ratio*rate + yards0
        if self.win or yards > scoreMax:
            yards = scoreMax
        return int(yards)

    def drawCaption(self, text):
        self.state = "pause"
        self.captionText = text
        self.captionTime = 1000
        self.player.direction = "Catch"

################################################################################
    
    def __init__(self, name):
        ''' Initialize the game '''
        pygame.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 30'
        pygame.display.set_caption(name)
        self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        icon = self.loadImage("Icon2.png", scale=1)[0]
        icon.set_colorkey((255,0,0))
        pygame.display.set_icon(icon.convert_alpha())
        self.audio = {}
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.playMusic("Ready_To_Play.wav")
        self.setVolume(0.1)
        # self.playSound("Clunk.wav", False)
        # self.playSound("Popcorn.wav", False)

        self.font = pygame.font.Font("font/LCD_Solid.ttf", FONT_SIZE)
        self.font1 = pygame.font.Font("font/LCD_Solid.ttf", int(FONT_SIZE*1.2))
        self.font2 = pygame.font.Font("font/LCD_Solid.ttf", FONT_SIZE*2)
        self.font3 = pygame.font.Font("font/LCD_Solid.ttf", FONT_SIZE*3)
        self.font4 = pygame.font.Font("font/LCD_Solid.ttf", int(FONT_SIZE*2.5))
        self.font0 = pygame.font.Font("font/LCD_Solid.ttf", int(FONT_SIZE*.75))

        self.backgrounds = []
        self.biomes = []
        self.borders = [0]
        if not test:
            self.addBackground("Field")
        for i in range(10):
            self.addBackground("City") # 10
        self.addBackground("ForestCoast")
        for i in range(4):
            self.addBackground("Forest") # 4
        self.addBackground("DesertCoast")
        for i in range(8): # 8
            self.addBackground("Desert")
        self.addBackground("OceanCoast")
        for i in range(10): # 10
            self.addBackground("Ocean")
        self.addBackground("ArcticCoast")
        for i in range(9): # 9
            self.addBackground("Arctic")
        self.addBackground("ArcticForestCoast")
        for i in range(4):
            self.addBackground("Forest") # 4
        for i in range(10):
            self.addBackground("City") # 10
        self.addBackground("Endzone")

        self.state = "start"
        self.reset()
        self.run()

    def run(self):
        ''' Iteratively call update '''
        clock = pygame.time.Clock()
        self.pause = False
        while not self.pause:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.keyPressed(event.key)
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit()
            dt = clock.tick(TIME_STEP)
            self.update(dt, pygame.key.get_pressed())
            pygame.display.update()
    
    def loadImage(self, name, number=1, angle=0, scale=PIXEL_RATIO, flip=False):
        ''' Loads an image or list of images '''
        nameF = name
        if flip:
            nameF = name + "Flip"
        if not hasattr(self, "images"):
            self.images = {}
        elif nameF in self.images:
            return self.images[nameF]
        if exe:
            path = os.path.join(os.path.dirname(sys.executable), 'images')
        else:
            path = os.path.join(os.path.dirname(__file__), 'images')
        sheet = img = pygame.image.load(os.path.join(path, name))
        sheet = pygame.transform.scale(sheet, [scale*sheet.get_width(), scale*sheet.get_height()])
        img = []
        w = sheet.get_width()/number
        h = sheet.get_height()
        for i in range(number):
            img.append(sheet.subsurface((w*i, 0, w, h)))
            img[i] = pygame.transform.rotate(img[i], angle)
            img[i] = pygame.transform.flip(img[i], flip, False)
        self.images[nameF] = img
        return img

    def playMusic(self, name):
        ''' Plays the given background track '''
        if exe:
            path = os.path.join(os.path.dirname(sys.executable), 'audio')
        else:
            path = os.path.join(os.path.dirname(__file__), 'audio')
        pygame.mixer.music.load(os.path.join(path, name))
        pygame.mixer.music.play(-1)

    def stopMusic(self):
        ''' Stops the current background track '''
        pygame.mixer.music.stop()

    def setVolume(self, val):
        ''' Scale volume 0 to 1 '''
        pygame.mixer.music.set_volume(val)
        
    def playSound(self, name, play=True):
        ''' Plays the given sound effect ''' 
        if name in self.audio:
            sound = self.audio[name]
        else:
            if exe:
                path = os.path.join(os.path.dirname(sys.executable), 'audio')
            else:
                path = os.path.join(os.path.dirname(__file__), 'audio')
            sound = pygame.mixer.Sound(os.path.join(path, name))
            self.audio[name] = sound
        if play:
            sound.play()


if __name__ == '__main__':
    game = Game("Touchdown")
