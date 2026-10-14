import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
import json
import requests

SERVER = "http://localhost:8000"

pygame.init()

font = pygame.font.SysFont("arial", 80)
smallFont = pygame.font.SysFont("arial", 50)
tableFont = pygame.font.SysFont("arial", 36)

PIPES_TO_WIN = 10
pipesPassed = 0
pipeCounted = False   # чтобы одну трубу не засчитать несколько раз

gameLevel = 1

POINTS_PER_PIPE = [10, 25, 75]   # очки за трубу на уровнях 1, 2, 3
totalScore = 0                # общий счёт за всю игру
levelStartScore = 0           # счёт на момент начала уровня (для "Try again")

recordSaved = False           # чтобы рекорд сохранялся один раз за игру

paused = False                # пауза включена или нет

errorUntil = 0                # до какого момента (мс) показывать ошибку про имя

topData = []                  # список рекордов, полученный с сервера


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
    btnStartGame.show()

def funcStartGame():
    
    global errorUntil
    if not Nameinput.getText().strip():
        errorUntil = pygame.time.get_ticks() + 2000  # показать ошибку 
        return
    saveNameToVariable()
    startGame()

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

def saveRecord(name, score):
    name = name or "Player"
    try:
        r = requests.post(f"{SERVER}/scores", json={"player": name, "score": score}, timeout=2)
        print("POST /scores ->", r.status_code, r.text)
    except requests.RequestException as e:
        print("Server error, score not saved", e)

serverOk = True

def loadTop():
    global serverOk
    try:
        r = requests.get(f"{SERVER}/scores/top", timeout=2)
        serverOk = True
        return r.json() if r.status_code == 200 else []
    except requests.RequestException:
        serverOk = False
        return []

def funcScore():
    global level, topData
    topData = loadTop()
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
        level = 4              # победа на промежуточном уровне
        btnNextLevel.show()
    else:
        level = 5              # финальный экран с итоговым счётом
        btnNextLevel.hide()
    btnWinExit.show()

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
    global totalScore
    totalScore = levelStartScore       # очки за этот уровень сгорают
    btnRetry.hide()
    btnDieExit.hide()
    startGame()

started = False
def startGame():
    global level, bgIndex, Switchbg, pipesX, fishY, fishSpeedVert, started
    global pipesPassed, pipeCompleted, nowPipe, pipeHitbox, pipeRect, recordSaved
    global levelStartScore
    level = 2
    bgIndex = 0
    
    # выбираем трубу текущего уровня
    nowPipe = pipeImages[gameLevel - 1]
    pipeHitbox = pygame.mask.from_surface(nowPipe)
    pipeRect = nowPipe.get_rect()

    pipesX = float(1000)
    pipeRect.x = 1000
    fishY = float(START_Y)
    fishSpeedVert = 0.0
    Switchbg = pygame.time.get_ticks()
    pipesPassed = 0
    pipeCompleted = False
    btnStartGame.hide()
    Nameinput.hide()
    started = False
    recordSaved = False
    levelStartScore = totalScore
    setPause(False)

screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Press fish")
background_1 = pygame.image.load("back_1.png").convert()
background_2 = pygame.image.load("back_2.png").convert()
dieScreen = pygame.image.load("DieScreen.jpg").convert()
pipeLevel1 = pygame.image.load("pipes/Pipes_Level1.png").convert_alpha()
pipeLevel2 = pygame.image.load("pipes/pipeLevel2.png").convert_alpha()
pipeLevel3 = pygame.image.load("pipes/PipesLeves3.png").convert_alpha()
fish = pygame.image.load("fish.png").convert_alpha()
fish = fish.subsurface(fish.get_bounding_rect()).copy()   # обрезка прозрачных полей
w, h = fish.get_size()
FISH_multiplier = 1.5                                            # во сколько раз увеличить
fish = pygame.transform.scale(fish, (w * FISH_multiplier, h * FISH_multiplier))

pipeImages = [pipeLevel1, pipeLevel2, pipeLevel3]   # труба для каждого уровня
nowPipe = pipeImages[0]
pipeRect = nowPipe.get_rect()

# 0 меню, 1 ввод имени, 2 игра, 3 экран смерти, 4 экран победы, 5 финальный экран, 6 таблица рекордов
level = 0
backgrounds = [background_1, background_2] #add more backgrounds if needed
bgIndex = 0
Switchbg = 0
SWITCH_DELAY = 1000 #for background switching in milliseconds
#обьединить все кнопки эксит в одну

btnStart = Button(screen, 300, 500, 270, 80, inactiveColour="#5A94C6", text="Start", onClick=funcStart)
btnScore = Button(screen, 300, 300, 270, 80, inactiveColour="#5A94C6", text="Score", onClick=funcScore)
btnExit = Button(screen, 300, 400, 270, 80, inactiveColour="#5A94C6", text="Exit", onClick=quit)
btnStartGame = Button(screen, 300, 200, 270, 80, inactiveColour="#5A94C6", text="Start", onClick=funcStartGame)

# кнопка возврата из таблицы рекордов
btnBack = Button(screen, 300, 500, 270, 80, inactiveColour="#5A94C6", text="Back", onClick=funcBack)
btnBack.hide()

# кнопки экрана победы
btnNextLevel = Button(screen, 300, 300, 270, 80, inactiveColour="#5A94C6", text="Next level", onClick=funcNextLevel)
btnWinExit = Button(screen, 300, 400, 270, 80, inactiveColour="#5A94C6", text="Exit", onClick=quit)
btnNextLevel.hide()
btnWinExit.hide()

# кнопки паузы
btnResume = Button(screen, 300, 250, 270, 80, inactiveColour="#5A94C6", text="Continue", onClick=lambda: setPause(False))
btnPauseExit = Button(screen, 300, 350, 270, 80, inactiveColour="#5A94C6", text="Exit", onClick=quit)
btnResume.hide()
btnPauseExit.hide()


btnRetry = Button(screen, 300, 300, 270, 80, inactiveColour="#5A94C6", text="Try again", onClick=funcRetry)
btnDieExit = Button(screen, 300, 400, 270, 80, inactiveColour="#5A94C6", text="Exit", onClick=quit)
btnRetry.hide()
btnDieExit.hide()

Nameinput = TextBox(screen, 500, 300, 270, 80, fontSize=50)
namesArray = loadNamesJson()
savedName = ""
Nameinput.hide()
btnStartGame.hide()


clock = pygame.time.Clock()

pipesX = float(1000)
fishRect = fish.get_rect()
FISH_X = 150
START_Y = 300
fishRect.x = FISH_X
fishY = float(START_Y)
fishSpeedVert = 0.0
GRAVITY = 1800          
JUMP_SPEED = -550       
SPEED = 1500

#столкновение 
pipeHitbox = pygame.mask.from_surface(nowPipe)
fishMask = pygame.mask.from_surface(fish)


running = True
while running:
    dt = clock.tick(60) / 1000.0

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and level == 2:
                setPause(not paused)                 # Esc: включить/выключить паузу
            elif event.key == pygame.K_SPACE and level == 2 and not paused:
                started = True
                fishSpeedVert = JUMP_SPEED

    if level == 2 and started and not paused:
        # труба
        pipesX -= SPEED * dt #viena skorost
        if pipeRect.right < 0:
            pipesX = float(1000)
            pipeCompleted = False
        pipeRect.x = round(pipesX)

        # рыбка
        fishSpeedVert += GRAVITY * dt
        fishY += fishSpeedVert * dt
        fishRect.y = round(fishY)

        # выход за экран
        if fishRect.bottom > 600 or fishRect.top < 0:
            print("граница экрана", fishRect, fishSpeedVert)
            level = 3

        # столкновение с трубой (по пикселям)
        offset = (pipeRect.x - fishRect.x, pipeRect.y - fishRect.y)
        if fishMask.overlap(pipeHitbox, offset):
            print("труба", fishRect, pipeRect)
            level = 3

        # подсчёт пройденных труб
        if level == 2 and not pipeCompleted and pipeRect.right < fishRect.right:
            pipeCompleted = True
            pipesPassed += 1
            totalScore += POINTS_PER_PIPE[gameLevel - 1]
            if pipesPassed >= PIPES_TO_WIN:
                showWinScreen()

    # сохраняем рекорд один раз: при смерти (3), победе на уровне (4) или конце игры (5)
    if level in (3, 4, 5) and not recordSaved:
        saveRecord(savedName, totalScore)
        recordSaved = True
        if level == 3:
            btnRetry.show()
            btnDieExit.show()

    # --- отрисовка: только рисуем, ничего не считаем ---
    if level == 0:
        screen.blit(background_1, (0, 0))
    elif level == 1:
        screen.blit(background_2, (0, 0))

        if pygame.time.get_ticks() < errorUntil:
            errText = smallFont.render("Введите имя!", True, (255, 60, 60))
            screen.blit(errText, errText.get_rect(center=(500, 450)))
            
    elif level == 2:
        now = pygame.time.get_ticks()
        if not paused and now - Switchbg >= SWITCH_DELAY:
            bgIndex = (bgIndex + 1) % len(backgrounds)
            Switchbg = now
        screen.blit(backgrounds[bgIndex], (0, 0))
        screen.blit(nowPipe, pipeRect)
        screen.blit(fish, fishRect)
        scoreText = font.render(str(totalScore), True, (255, 255, 255))
        screen.blit(scoreText, (20, 20))
        if paused:
            pauseText = font.render("pause", True, (255, 255, 255))
            screen.blit(pauseText, pauseText.get_rect(center=(500, 150)))
    elif level == 3:
        screen.blit(dieScreen, (0, 0))
    elif level == 4:
        screen.blit(background_1, (0, 0))
        winText = font.render("win", True, (255, 255, 255))
        screen.blit(winText, winText.get_rect(center=(500, 120)))
        pointsText = font.render(f"punkti: {totalScore}", True, (255, 255, 255))
        screen.blit(pointsText, pointsText.get_rect(center=(500, 220)))
    elif level == 5:
        screen.blit(background_1, (0, 0))
        winText = font.render("spele beigt", True, (255, 255, 255))
        screen.blit(winText, winText.get_rect(center=(500, 120)))
        totalText = font.render(f"all punkti: {totalScore}", True, (255, 255, 255))
        screen.blit(totalText, totalText.get_rect(center=(500, 250)))
    elif level == 6:
        screen.blit(background_1, (0, 0))
        title = smallFont.render("TOP 10", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(500, 40)))
        if not topData:
            msg = "No records yet" if serverOk else "Server offline"
            empty = tableFont.render(msg, True, (255, 255, 255))
            screen.blit(empty, empty.get_rect(center=(500, 250)))
        for i, row in enumerate(topData):
            line = tableFont.render(f"{i + 1}. {row['player']} - {row['score']}", True, (255, 255, 255))
            screen.blit(line, (300, 90 + i * 40))


    pygame_widgets.update(events)
    pygame.display.flip()

pygame.quit()


#чтобы активировать сервер:
#1. открыть терминал#чтобы активировать сервер:
#1. открыть терминал
#2. перейти в папку с проектом
#3. выполнить команду: source .venv/bin/activate
#uvicorn server:app --reload
#2. перейти в папку с проектом
#3. выполнить команду: source .venv/bin/activate
#uvicorn server:app --reload#чтобы активировать сервер:
#1. открыть терминал
#2. перейти в папку с проектом
#3. выполнить команду: source .venv/bin/activate
#uvicorn server:app --reload#чтобы активировать сервер:
#1. открыть терминал
#2. перейти в папку с проектом
#3. выполнить команду: source .venv/bin/activate
#uvicorn server:app --reload#чтобы активировать сервер:
#1. открыть терминал
#2. перейти в папку с проектом
#3. выполнить команду: source .venv/bin/activate
#uvicorn server:app --reload#чтобы активировать сервер:
#1. открыть терминал
#2. перейти в папку с проектом
#3. выполнить команду: source .venv/bin/activate
#uvicorn server:app --reload