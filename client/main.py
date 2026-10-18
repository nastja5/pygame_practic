import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
import random
import threading

from pathlib import Path
from game.constants import *
from game.physics import FishBody, SharkBody
from game.ray import RayAttack
from game.scoring import pipe_points, ichor_points
from client import api_client

pygame.init()


screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Press fish") 

ASSETS = Path(__file__).parent / "assets"

font = pygame.font.SysFont("arial", 80)
smallFont = pygame.font.SysFont("arial", 50)
tableFont = pygame.font.SysFont("arial", 36)


pipesPassed = 0
gameLevel = 1
totalScore = 0
levelStartScore = 0
level3StartScore = 0

recordSaved = False
paused = False
errorUntil = 0
topData = []
tokenIn = ""
textErrorLogIn = "Input Name"


class Fish:
    def __init__(self, x):
        self.image = pygame.image.load(ASSETS / "fish.png").convert_alpha()
        self.image = self.image.subsurface(self.image.get_bounding_rect()).copy()
        width, height = self.image.get_size()
        self.image = pygame.transform.scale(
            self.image, (int(width * 1.2), int(height * 1.2)))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.body = FishBody()
        self.rect.y = round(self.body.y)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.body.update(dt)
        self.rect.y = round(self.body.y)

    def jump(self):
        self.body.jump()

    def reset(self):
        self.body.reset()
        self.rect.y = round(self.body.y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

FishObj = Fish(150)

class Shark:
    def __init__ (self, x, y):

        self.image = pygame.image.load(ASSETS / "Shark.png").convert_alpha()
        self.image = self.image.subsurface(self.image.get_bounding_rect()).copy()
        w, h = self.image.get_size()

        self.rect = self.image.get_rect()
        self.rect.x = x

        self.body = SharkBody(self.rect.height)
        self.rect.y = round(self.body.y)
        self.mask = pygame.mask.from_surface(self.image)
        
    def moving(self, dt):
        self.body.move(dt)
        self.rect.y = round(self.body.y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def reset(self):
        self.body.reset()
        self.rect.y = round(self.body.y)
        
SharkObj = Shark(800, 300)

def funcStart():
    global level, gameLevel, totalScore, errorUntil
    level = 1
    gameLevel = 1
    errorUntil = 0
    totalScore = 0
    btnStart.hide()
    btnScore.hide()
    btnExit.hide()
    Nameinput.show()
    Passwinput.show()
    btnLogin.show()
    btnRegister.show()

def funcStartGame():
    global errorUntil
    if not Nameinput.getText().strip():
        errorUntil = pygame.time.get_ticks() + 2000
        return
    saveNameToVariable()
    startGame()

def showMessage(text):
    global textErrorLogIn, errorUntil
    textErrorLogIn = str(text)
    errorUntil = pygame.time.get_ticks() + 2500

def funcLogIn(register):
    global tokenIn
    name = Nameinput.getText().strip()
    password = Passwinput.getText()
    if not name or not password:
        showMessage("Input name or password")
        return
    token, error = api_client.login(name, password, register)
    if error:
        showMessage(error)
        return
    tokenIn = token
    Passwinput.setText("")
    funcStartGame()

def saveNameToVariable():
    global savedName
    savedName = Nameinput.getText().strip()
    Nameinput.setText("")

serverOk = True
def funcScore():
    global level, topData, serverOk
    topData, serverOk = api_client.load_top()
    level = 6
    btnStart.hide()
    btnScore.hide()
    btnExit.hide()
    btnBack.show()

def funcBack():
    global level
    level = 0
    btnBack.hide()
    btnStart.show()
    btnScore.show()
    btnExit.show()

def showWinScreen():
    global level
    if gameLevel < len(pipeImages):
        level = 4           
        btnNextLevel.show()
    else:
        level = 5      
        btnNextLevel.hide()
    btnWinExit.show()
    if gameLevel == 3:
        btnBossFight.show()

def funcNextLevel():
    global gameLevel
    gameLevel += 1
    btnNextLevel.hide()
    btnWinExit.hide()
    startGame()

def setPause(value):
    global paused
    paused = value
    if paused:
        btnResume.show()
        btnPauseExit.show()
    else:
        btnResume.hide()
        btnPauseExit.hide()

def funcRetry():
    global totalScore, gameLevel
    btnRetry.hide()
    btnDieExit.hide()
    if inBoss:                         
        gameLevel = 3
        totalScore = level3StartScore
        startGame()
    else:                         
        totalScore = levelStartScore
        startGame()

inBoss = False
started = False
def startGame():
    global level, bgIndex, Switchbg, pipesX, started, inBoss
    global pipesPassed, pipeCompleted, pipeRect, recordSaved
    global levelStartScore, level3StartScore
    level = 2
    bgIndex = 0

    levelStartScore = totalScore
    if gameLevel == 3:
        level3StartScore = totalScore

    FishObj.reset()

    pipesX = float(1000)
    pickPipe()
    
    Switchbg = pygame.time.get_ticks()
    pipesPassed = 0
    pipeCompleted = False

    Nameinput.hide()
    Passwinput.hide()
    btnLogin.hide()
    btnRegister.hide()
    started = False
    inBoss = False
    recordSaved = False
    levelStartScore = totalScore
    setPause(False)

def pickPipe(levelNum=None):
    global nowPipe, pipeHitbox, pipeRect
    if levelNum is None:
        levelNum = gameLevel
    options = pipeImages[levelNum - 1]
    if len(options) > 1:
        options = [p for p in options if p is not nowPipe]   
    nowPipe = random.choice(options)
    pipeHitbox = pygame.mask.from_surface(nowPipe)
    pipeRect = nowPipe.get_rect()
    pipeRect.x = round(pipesX)

def bossFightStart():
    global bgIndex, Switchbg, started, level, inBoss
    global pipesPassed, pipeCompleted, pipeRect, recordSaved
    global levelStartScore
    global ichorTimer, burstLeft, burstTimer

    bgIndex = 0
    level = 7
    inBoss = True

    Switchbg = pygame.time.get_ticks()

    SharkObj.rect.x = 800

    SharkObj.reset()
    FishObj.reset()

    rayAttack.reset()

    ichors.clear()
    ichorTimer = ICHOR_COOLDOWN
    burstLeft = 0
    burstTimer = 0.0

    Nameinput.hide()
    Passwinput.hide()
    btnLogin.hide()
    btnRegister.hide()
    btnWinExit.hide()
    btnBossFight.hide()
    btnRetry.hide()
    btnDieExit.hide()
    started = False
    recordSaved = False
    levelStartScore = totalScore
    setPause(False)


def startRayWarning():
    global rayRect, rayWarnImg, rayImg, rayMask

    width = max(1, SharkObj.rect.left)               
    height = ray.get_height()

    rayWarnImg = pygame.transform.scale(rayFirst, (width, height))
    rayImg = pygame.transform.scale(ray, (width, height))
    rayMask = pygame.mask.from_surface(rayImg)

    rayRect = rayImg.get_rect()
    rayRect.right = SharkObj.rect.left
    rayRect.centery = SharkObj.rect.centery          
    
def fireIchor():
    global burstLeft, burstTimer
    burstLeft = ICHOR_BURST_COUNT
    burstTimer = 0.0

def bossWin():
    global level
    level = 5
    btnNextLevel.hide()
    btnBossFight.hide()
    btnWinExit.show()

def update_fish(dt):
    global level
    
    FishObj.update(dt)

    if FishObj.rect.bottom > 600 or FishObj.rect.top < 0:
        print("screen edge", FishObj.rect, FishObj.body.speed_y)
        level = 3  



BackStart = pygame.image.load(ASSETS / "pipes/start.png").convert_alpha()
icon = pygame.image.load(ASSETS / "pipes/Icon.png") 
icon = icon.subsurface(icon.get_bounding_rect()).copy()
pygame.display.set_icon(icon)

background_1 = pygame.image.load(ASSETS / "back_1.png").convert()
background_2 = pygame.image.load(ASSETS / "back_2.png").convert()
dieScreen = pygame.image.load(ASSETS / "DieScreen.jpg").convert()
dieScreen = pygame.transform.scale(dieScreen, (SCREEN_W, SCREEN_H))

pipeLevel1 = pygame.image.load(ASSETS / "pipes/Pipes_Level1.png").convert_alpha()

Pipes_Level2_N1 = pygame.image.load(ASSETS / "pipes/Pipes_Level2_N1.png").convert_alpha()
Pipes_Level2_N2 = pygame.image.load(ASSETS / "pipes/Pipes_Level2_N2.png").convert_alpha()
Pipes_Level2_N3 = pygame.image.load(ASSETS / "pipes/Pipes_Level2_N3.png").convert_alpha()

Pipes_Level3_N1 = pygame.image.load(ASSETS / "pipes/Pipes_Level3_N1.png").convert_alpha()
Pipes_Level3_N2 = pygame.image.load(ASSETS / "pipes/Pipes_Level3_N2.png").convert_alpha()
Pipes_Level3_N3 = pygame.image.load(ASSETS / "pipes/Pipes_Level3_N3.png").convert_alpha()
Pipes_Level3_N4 = pygame.image.load(ASSETS / "pipes/Pipes_Level3_N4.png").convert_alpha()


ray = pygame.image.load(ASSETS / "pipes/ray.png").convert_alpha()
ray = ray.subsurface(ray.get_bounding_rect()).copy()
rayFirst = pygame.image.load(ASSETS / "pipes/rayFirst.png").convert_alpha()
rayFirst = rayFirst.subsurface(rayFirst.get_bounding_rect()).copy()

burstLeft = 0
burstTimer = 0.0

ichors = []
ichorTimer = 0.0

rayAttack = RayAttack()
rayRect = pygame.Rect(0, 0, 0, 0)
rayWarnImg = rayFirst
rayImg = ray
rayMask = pygame.mask.from_surface(ray)

Ichor = pygame.image.load(ASSETS / "pipes/Ichor.png").convert_alpha()
Ichor = Ichor.subsurface(Ichor.get_bounding_rect()).copy()



              #level1        #level2                                                #level3
pipeImages = [[pipeLevel1],[Pipes_Level2_N1, Pipes_Level2_N2, Pipes_Level2_N3],[Pipes_Level3_N1, Pipes_Level3_N2, Pipes_Level3_N3, Pipes_Level3_N4]]
nowPipe = pipeImages[0][0]
pipeRect = nowPipe.get_rect()

# 0 menu, 1 ievad name/parole, 2 speles sakums, 3 die, 4 win, 5 beigums ekrans, 6 record tabula, 7 boss
level = 0
backgrounds = [background_1, background_2] #add more backgrounds if needed
bgIndex = 0
Switchbg = 0
SWITCH_DELAY = 1000 #for background switching in milliseconds

btnStart = Button(screen, 417, 339, 150, 50, inactiveColour="#F8D96CF2", text="Start", onClick=funcStart)
btnScore = Button(screen, 417, 424, 150, 50, inactiveColour="#F8D96CF2", text="Score", onClick=funcScore)
btnExit = Button(screen, 417, 502, 150, 50, inactiveColour="#F8D96CF2", text="Exit", onClick=quit)

btnBack = Button(screen, 350, 500, 270, 80, inactiveColour="#80B9EB39", text="Back", onClick=funcBack)
btnBack.hide()

btnNextLevel = Button(screen, 350, 300, 270, 80, inactiveColour="#80B9EB39", text="Next level", onClick=funcNextLevel)
btnWinExit = Button(screen, 350, 400, 270, 80, inactiveColour="#80B9EB39", text="Exit", onClick=quit)
btnNextLevel.hide()
btnWinExit.hide()

btnResume = Button(screen, 350, 250, 270, 80, inactiveColour="#80B9EB39", text="Continue", onClick=lambda: setPause(False))
btnPauseExit = Button(screen, 350, 350, 270, 80, inactiveColour="#80B9EB39", text="Exit", onClick=quit)
btnResume.hide()
btnPauseExit.hide()

btnRetry = Button(screen, 300, 300, 270, 80, inactiveColour="#0078D7", text="Try again", onClick=funcRetry)
btnDieExit = Button(screen, 300, 500, 270, 80, inactiveColour="#0078D7", text="Exit", onClick=quit)
btnRetry.hide()
btnDieExit.hide()

Passwinput = TextBox(screen, 350, 255, 270, 80, placeholderText='Enter Pasword', fontSize=25)

btnLogin = Button(screen, 350, 350, 270, 80, inactiveColour="#80B9EB39",
                  text="Login", onClick=lambda: funcLogIn(False))
btnRegister = Button(screen, 350, 445, 270, 80, inactiveColour="#80B9EB39",
                     text="Register", onClick=lambda: funcLogIn(True))

btnBossFight = Button(screen, 350, 300, 270, 80, inactiveColour="#80B9EB39", text="Boss Fight", onClick=bossFightStart)
btnBossFight.hide()
Passwinput.hide()
btnLogin.hide()
btnRegister.hide()

Nameinput = TextBox(screen, 350, 160, 270, 80,placeholderText='Enter Name:', fontSize=25)

savedName = ""
Nameinput.hide()


clock = pygame.time.Clock()

pipesX = float(1000)

pressSpaceText = smallFont.render("Press Space to start", "#0C162F", True)

pipeHitbox = pygame.mask.from_surface(nowPipe)

ichorMask = pygame.mask.from_surface(Ichor)


running = True
while running:
    dt = clock.tick(60) / 1000.0

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and level in (2, 7):
                setPause(not paused)
            elif event.key == pygame.K_SPACE and level in (2, 7) and not paused:
                started = True
                FishObj.jump()


    if level == 2 and started and not paused:
        pipesX -= PIPE_SPEED * dt 
        if pipeRect.right < 0:
            pipesX = float(1000)
            pipeCompleted = False
            pickPipe()          
        pipeRect.x = round(pipesX)

        update_fish(dt)

        offset = (pipeRect.x - FishObj.rect.x, pipeRect.y - FishObj.rect.y)
        if FishObj.mask.overlap(pipeHitbox, offset):
            print("pipe", FishObj.rect, pipeRect)
            level = 3

        if level == 2 and not pipeCompleted and pipeRect.right < FishObj.rect.right:
            pipeCompleted = True
            pipesPassed += 1
            totalScore += pipe_points(gameLevel)
            if pipesPassed >= PIPES_TO_WIN:
                showWinScreen()

    if level == 7 and started and not paused:
        SharkObj.moving(dt)
        update_fish(dt)

        if rayAttack.update(dt) == "warn":
            startRayWarning()

        if rayAttack.state == "fire":
            offset = (rayRect.x - FishObj.rect.x, rayRect.y - FishObj.rect.y)
            if FishObj.mask.overlap(rayMask, offset):
                level = 3
        ichorTimer += dt

        if ichorTimer >= ICHOR_COOLDOWN:
            ichorTimer -= ICHOR_COOLDOWN
            fireIchor()

        if burstLeft > 0:
            burstTimer += dt
            if burstTimer >= ICHOR_BURST_DELAY:
                burstTimer = 0.0
                r = Ichor.get_rect()
                r.left = FishObj.rect.right
                r.centery = FishObj.rect.centery
                ichors.append({"x": float(r.x), "rect": r})
                burstLeft -= 1

        for b in ichors[:]:
            b["x"] += ICHOR_SPEED * dt
            b["rect"].x = round(b["x"])
            if b["rect"].left > 1000:       
                ichors.remove(b)
                continue
            offset = (SharkObj.rect.x - b["rect"].x, SharkObj.rect.y - b["rect"].y)
            if ichorMask.overlap(SharkObj.mask, offset):   
                ichors.remove(b)
                SharkObj.body.hp -= ICHOR_DAMAGE
                totalScore += ichor_points(b["rect"].centery,SharkObj.rect.centery,SharkObj.rect.height,)
                if SharkObj.body.hp <= 0:
                    SharkObj.body.hp = 0
                    bossWin()
                    break

    if level in (3,5) and not recordSaved:
        bossBeaten = (level == 5 and inBoss)
        threading.Thread(target=lambda: api_client.save_score(tokenIn, totalScore, bossBeaten), daemon=True).start()
        recordSaved = True
        if level == 3:
            btnRetry.show()
            btnDieExit.show()

    if level == 0:
        screen.blit(background_1, (0, 0))
        screen.blit(BackStart, (0, 0))
    elif level == 1:
        screen.blit(background_2, (0, 0))
        if pygame.time.get_ticks() < errorUntil:
            errText = smallFont.render(textErrorLogIn, True, "#0C162F")
            screen.blit(errText, errText.get_rect(center=(500, 100)))

    elif level == 2:
        now = pygame.time.get_ticks()
        if not paused and now - Switchbg >= SWITCH_DELAY:
            bgIndex = (bgIndex + 1) % len(backgrounds)
            Switchbg = now
        screen.blit(backgrounds[bgIndex], (0, 0))
        screen.blit(nowPipe, pipeRect)

        FishObj.draw(screen)

        scoreText = font.render(str(totalScore), True,"#0C162F")
        screen.blit(scoreText, (20, 20))

        if not started and not paused:
            screen.blit(pressSpaceText, pressSpaceText.get_rect(center=(500, 150)))
        if paused:
            pauseText = font.render("pause", True ,"#0C162F")
            screen.blit(pauseText, pauseText.get_rect(center=(500, 150)))

    elif level == 3:
        screen.blit(dieScreen, (0, 0))
    elif level == 4:
        screen.blit(background_1, (0, 0))

        winText = font.render("win", True,"#0C162F")
        pointsText = font.render(f"points: {totalScore}", True,"#0C162F")
        
    elif level == 5:
        screen.blit(background_1, (0, 0))

        if inBoss:
            winText = font.render("You win!", True, "#0C162F")
            screen.blit(winText, winText.get_rect(center=(500, 150)))
            
            totalText = smallFont.render(f"All points: {totalScore}", True, "#0C162F")
            screen.blit(totalText, totalText.get_rect(center=(500, 250)))

        else:
            totalText = font.render(f"All points: {totalScore}", True, "#0C162F")
            screen.blit(totalText, totalText.get_rect(center=(500, 250)))

    elif level == 6:
        screen.blit(background_1, (0, 0))
        title = smallFont.render("TOP 10", True,"#0C162F")
        screen.blit(title, title.get_rect(center=(500, 40)))

        if not topData:
            msg = "No records yet" if serverOk else "Server offline"
            empty = tableFont.render(msg, True,"#0C162F")
            screen.blit(empty, empty.get_rect(center=(500, 250)))
        for i, row in enumerate(topData):
            line = tableFont.render(f"{i + 1}. {row['player']} - {row['score']}", True,"#0C162F")
            screen.blit(line, (300, 90 + i * 40))

    elif level == 7:

        screen.blit(background_1, (0, 0))
        SharkObj.draw(screen)

        if rayAttack.state == "warn":
            screen.blit(rayWarnImg, rayRect)
        elif rayAttack.state == "fire":
            screen.blit(rayImg, rayRect)
        for b in ichors:
            screen.blit(Ichor, b["rect"])

        pygame.draw.rect(screen, (60, 60, 60), (550, 20, 400, 25))
        pygame.draw.rect(screen, (220, 40, 40), (550, 20, 400 * SharkObj.body.hp / BOSS_MAX_HP, 25))
        pygame.draw.rect(screen, (255, 255, 255), (550, 20, 400, 25), 2)

        FishObj.draw(screen)
        scoreText = font.render(str(totalScore), True,"#0C162F")
        screen.blit(scoreText, (20, 20))

        if not started and not paused:
            screen.blit(pressSpaceText, pressSpaceText.get_rect(center=(500, 150)))
        
        if paused:
            pauseText = font.render("pause", True,"#0C162F")
            screen.blit(pauseText, pauseText.get_rect(center=(500, 150)))


    pygame_widgets.update(events)
    pygame.display.flip()

pygame.quit()