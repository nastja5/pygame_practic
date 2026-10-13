import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
import json
pygame.init()

def funcStart():
    global level
    level = 1
    btnStart.hide()
    btnScore.hide()
    btnExit.hide()
    Nameinput.show()
    btnStartGame.show()

def saveNameToVariable():
    global savedName
    savedName = Nameinput.getText().strip()
    if not savedName:
        return
    namesArray.append(savedName)
    saveNamesJson()
    Nameinput.setText("")

def loadNamesJson():
    try:
        with open("templates/names.json", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def saveNamesJson():
    with open("templates/names.json", "w", encoding="utf-8") as f:
        json.dump(namesArray, f, ensure_ascii=False, indent=2)

def startGame():
    global level, bgIndex, lastSwitch #?
    level = 2
    bgIndex = 0
    lastSwitch = pygame.time.get_ticks() #?
    btnStartGame.hide()
    Nameinput.hide()

screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Press fish")
background_1 = pygame.image.load("back_1.png").convert()
background_2 = pygame.image.load("back_2.png").convert()
dieScreen = pygame.image.load("DieScreen.jpg").convert()

level = 0              # 0 меню, 1 ввод имени, 2 игра, 3 экран смерти
backgrounds = [background_1, background_2] #add more backgrounds if needed
bgIndex = 0
lastSwitch = 0
SWITCH_DELAY = 1000 

btnStart = Button(screen, 300, 500, 270, 80, text="Start", onClick=funcStart)
btnScore = Button(screen, 300, 300, 270, 80, text="Score")
btnExit = Button(screen, 300, 400, 270, 80, text="Exit", onClick=quit)
btnStartGame = Button(screen, 300, 200, 270, 80, text="Start",
                      onClick=lambda: (saveNameToVariable(), startGame()))

Nameinput = TextBox(screen, 500, 300, 270, 80, fontSize=50)
namesArray = loadNamesJson()
savedName = ""
Nameinput.hide()
btnStartGame.hide()

running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if level == 2:
                    level = 3

    if level == 0:
        screen.blit(background_1, (0, 0))
    elif level == 1:
        screen.blit(background_2, (0, 0))
    elif level == 2:                  #?
        now = pygame.time.get_ticks()
        if now - lastSwitch >= SWITCH_DELAY:
            bgIndex = (bgIndex + 1) % len(backgrounds)
            lastSwitch = now
        screen.blit(backgrounds[bgIndex], (0, 0))
    elif level == 3:
        screen.blit(dieScreen, (0, 0))

    pygame_widgets.update(events)
    pygame.display.flip()

pygame.quit()