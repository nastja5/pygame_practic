import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
import json
import requests
import random

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
tokenIn = ""                # токен после входа
textErrorLogIn = "Input Name"              # текст ошибки входа


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
        errorUntil = pygame.time.get_ticks() + 2000  # показать ошибку
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
        showMessage("Введите имя и пароль!")
        return
    body = {"name": name, "password": password}
    try:
        if register:
            r = requests.post(f"{SERVER}/register", json=body, timeout=2)
            if r.status_code != 201:
                showMessage(r.json().get("detail", "Ошибка регистрации"))
                return
        r = requests.post(f"{SERVER}/login", json=body, timeout=2)
        if r.status_code != 200:
            showMessage(r.json().get("detail", "Ошибка входа"))
            return
    except requests.RequestException:
        showMessage("Сервер недоступен")
        return
    tokenIn = r.json()["token"]
    Passwinput.setText("")
    funcStartGame()          # ваша старая функция: сохранит имя и запустит игру

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
        r = requests.post(f"{SERVER}/scores", json={"player": name, "score": score},
                  headers={"token": tokenIn}, timeout=2)
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
    if gameLevel == 2:
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
    global totalScore
    totalScore = levelStartScore       # очки за этот уровень сгорают
    btnRetry.hide()
    btnDieExit.hide()
    if inBoss:                         # умерли на боссе -> заново босс
        bossFightStart()
    else:                              # иначе обычный уровень с трубами
        startGame()

inBoss = False
started = False
def startGame():
    global level, bgIndex, Switchbg, pipesX, fishY, fishSpeedVert, started, inBoss
    global pipesPassed, pipeCompleted, pipeRect, recordSaved
    global levelStartScore
    level = 2
    bgIndex = 0

    pipesX = float(1000)
    pickPipe()
    fishY = float(START_Y)
    fishSpeedVert = 0.0
    Switchbg = pygame.time.get_ticks()
    pipesPassed = 0
    pipeCompleted = False
    btnStartGame.hide()
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
        options = [p for p in options if p is not nowPipe]   # не повторять подряд
    nowPipe = random.choice(options)
    pipeHitbox = pygame.mask.from_surface(nowPipe)
    pipeRect = nowPipe.get_rect()
    pipeRect.x = round(pipesX)



def bossFightStart():
    global bgIndex, Switchbg, started, level, inBoss
    global pipesPassed, pipeCompleted, pipeRect, recordSaved
    global fishY, fishSpeedVert, SharkSpeed
    global levelStartScore
    global rayState, rayTimer
    global bossHp, ichorTimer, burstLeft, burstTimer
    bgIndex = 0

    level = 7
    inBoss = True

    Switchbg = pygame.time.get_ticks()

    fishY = float(START_Y)
    fishSpeedVert = 0.0
    fishRect.y = START_Y
    sharkRect.x = 800
    sharkRect.y = 300
    SharkSpeed = 5

    # сброс луча
    rayState = "idle"
    rayTimer = 0.0

    bossHp = BOSS_MAX_HP
    ichors.clear()
    ichorTimer = ICHOR_COOLDOWN   # первый залп сразу, как начнёшь играть
    burstLeft = 0
    burstTimer = 0.0

    btnStartGame.hide()
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
    """Акула целится: фиксируем высоту и показываем предупреждающий луч."""
    global rayState, rayTimer, rayRect, rayWarnImg, rayImg, rayMask

    width = max(1, sharkRect.left)               # луч идёт от акулы до левого края
    height = ray.get_height()

    rayWarnImg = pygame.transform.scale(rayFirst, (width, height)) #спрайт луча
    rayImg = pygame.transform.scale(ray, (width, height))
    rayMask = pygame.mask.from_surface(rayImg) #маска для луча

    rayRect = rayImg.get_rect()
    rayRect.right = sharkRect.left
    rayRect.centery = sharkRect.centery          # высота фиксируется в момент выстрела
    
    rayState = "warn"
    rayTimer = 0.0


def fireIchor():
    """Запуск серии выстрелов (очереди)."""
    global burstLeft, burstTimer
    burstLeft = ICHOR_BURST_COUNT
    burstTimer = 0.0


def bossWin():
    global level
    level = 5                  # финальный экран с итоговым счётом
    btnNextLevel.hide()
    btnBossFight.hide()
    btnWinExit.show()





screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Press fish")

BackStart = pygame.image.load("pipes/start.png").convert_alpha()

background_1 = pygame.image.load("back_1.png").convert()
background_2 = pygame.image.load("back_2.png").convert()
dieScreen = pygame.image.load("DieScreen.jpg").convert()

pipeLevel1 = pygame.image.load("pipes/Pipes_Level1.png").convert_alpha()

Pipes_Level2_N1 = pygame.image.load("pipes/Pipes_Level2_N1.png").convert_alpha()
Pipes_Level2_N2 = pygame.image.load("pipes/Pipes_Level2_N2.png").convert_alpha()
Pipes_Level2_N3 = pygame.image.load("pipes/Pipes_Level2_N3.png").convert_alpha()

Pipes_Level3_N1 = pygame.image.load("pipes/Pipes_Level3_N1.png").convert_alpha()
Pipes_Level3_N2 = pygame.image.load("pipes/Pipes_Level3_N2.png").convert_alpha()
Pipes_Level3_N3 = pygame.image.load("pipes/Pipes_Level3_N3.png").convert_alpha()
Pipes_Level3_N4 = pygame.image.load("pipes/Pipes_Level3_N4.png").convert_alpha()

fish = pygame.image.load("fish.png").convert_alpha()
fish = fish.subsurface(fish.get_bounding_rect()).copy()   # обрезка прозрачных полей
w, h = fish.get_size()
FISH_multiplier = 1.2                                          # во сколько раз увеличить
fish = pygame.transform.scale(fish, (w * FISH_multiplier, h * FISH_multiplier))


#boss

shark = pygame.image.load("pipes/Shark.png").convert_alpha()
shark = shark.subsurface(shark.get_bounding_rect()).copy()
w, h = shark.get_size()


sharkRect = shark.get_rect()
sharkRect.x = 800  # Начальная позиция X
sharkRect.y = 300
SharkSpeed = 5

#луч

ray = pygame.image.load("pipes/ray.png").convert_alpha()
ray = ray.subsurface(ray.get_bounding_rect()).copy()

rayFirst = pygame.image.load("pipes/rayFirst.png").convert_alpha()
rayFirst = rayFirst.subsurface(rayFirst.get_bounding_rect()).copy()

RAY_COOLDOWN = 1.0   # пауза между атаками, сек
RAY_WARN = 2.0       # сколько висит предупреждение, сек
RAY_FIRE = 1.0       # сколько живёт настоящий луч, сек

BOSS_MAX_HP = 100
ICHOR_DAMAGE = 15
ICHOR_COUNT = 5          # всего пуль в залпе
ICHOR_COOLDOWN = 2.0     # секунд между залпами
ICHOR_SPEED = 900        # пикселей в секунду
ICHOR_BURST_COUNT = 5    # сколько пуль в очереди
ICHOR_BURST_DELAY = 0.08 # задержка между пулями в секундах
burstLeft = 0            # сколько пуль осталось выпустить в текущей очереди
burstTimer = 0.0

bossHp = BOSS_MAX_HP
ichors = []              # летящие пули
ichorTimer = 0.0

rayState = "idle"    # "idle" - ждём, "warn" - предупреждение, "fire" - настоящий луч
rayTimer = 0.0
rayRect = pygame.Rect(0, 0, 0, 0)
rayWarnImg = rayFirst
rayImg = ray
rayMask = pygame.mask.from_surface(ray)


#пуля
Ichor = pygame.image.load("pipes/Ichor.png").convert_alpha()
Ichor = Ichor.subsurface(Ichor.get_bounding_rect()).copy()



              #level1        #level2                                                #level3
pipeImages = [[pipeLevel1],[Pipes_Level2_N1, Pipes_Level2_N2, Pipes_Level2_N3]]#,[Pipes_Level3_N1, Pipes_Level3_N2, Pipes_Level3_N3, Pipes_Level3_N4]]
nowPipe = pipeImages[0][0]
pipeRect = nowPipe.get_rect()

# 0 меню, 1 ввод имени, 2 игра, 3 экран смерти, 4 экран победы, 5 финальный экран, 6 таблица рекордов, 7 босс
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

Passwinput = TextBox(screen, 300, 255, 270, 80, placeholderText='Введите пароль', fontSize=25)
btnLogin = Button(screen, 300, 350, 270, 80, inactiveColour="#5A94C6",
                  text="Login", onClick=lambda: funcLogIn(False))
btnRegister = Button(screen, 300, 445, 270, 80, inactiveColour="#5A94C6",
                     text="Register", onClick=lambda: funcLogIn(True))



btnBossFight = Button(screen, 300, 500, 270, 80, inactiveColour="#5A94C6", text="Boss Fight", onClick=bossFightStart)
btnBossFight.hide()





Passwinput.hide()
btnLogin.hide()
btnRegister.hide()

Nameinput = TextBox(screen, 300, 160, 270, 80,placeholderText='Введите имя', fontSize=25)
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
SPEED = 1000

#столкновение
pipeHitbox = pygame.mask.from_surface(nowPipe) #!!!!!!!!!!1переименовать в хитбокс
fishMask = pygame.mask.from_surface(fish)
sharkMask = pygame.mask.from_surface(shark)
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
                fishSpeedVert = JUMP_SPEED


    # ---------- обновление: уровни с трубами ----------
    if level == 2 and started and not paused:
        # труба
        pipesX -= SPEED * dt #viena skorost
        if pipeRect.right < 0:
            pipesX = float(1000)
            pipeCompleted = False
            pickPipe()          # новая случайная труба
        pipeRect.x = round(pipesX)

        # рыбка
        fishSpeedVert += GRAVITY * dt
        fishY += fishSpeedVert * dt
        fishRect.y = round(fishY)

        # выход за экран fish
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

    # ---------- обновление: босс ----------
    if level == 7 and started and not paused:
        # акула
        sharkRect.y += SharkSpeed
        if sharkRect.bottom >= 600 or sharkRect.top <= 0:
            SharkSpeed = -SharkSpeed

        # рыбка
        fishSpeedVert += GRAVITY * dt
        fishY += fishSpeedVert * dt
        fishRect.y = round(fishY)

        # выход за экран fish
        if fishRect.bottom > 600 or fishRect.top < 0:
            print("граница экрана", fishRect, fishSpeedVert)
            level = 3

        # луч
        rayTimer += dt
        if rayState == "idle":
            if rayTimer >= RAY_COOLDOWN:
                startRayWarning()                # idle -> warn
        elif rayState == "warn":
            if rayTimer >= RAY_WARN:
                rayState = "fire"                # warn -> fire
                rayTimer = 0.0
        elif rayState == "fire":
            offset = (rayRect.x - fishRect.x, rayRect.y - fishRect.y)
            if fishMask.overlap(rayMask, offset):
                level = 3                        # попал под настоящий луч
            if rayTimer >= RAY_FIRE:
                rayState = "idle"                # fire -> idle
                rayTimer = 0.0

        ichorTimer += dt
        if ichorTimer >= ICHOR_COOLDOWN:
            ichorTimer -= ICHOR_COOLDOWN
            fireIchor()

        # Выпуск пуль очередью друг за другом
        if burstLeft > 0:
            burstTimer += dt
            if burstTimer >= ICHOR_BURST_DELAY:
                burstTimer = 0.0
                r = Ichor.get_rect()
                r.left = fishRect.right
                r.centery = fishRect.centery
                ichors.append({"x": float(r.x), "rect": r})
                burstLeft -= 1

        for b in ichors[:]:
            b["x"] += ICHOR_SPEED * dt
            b["rect"].x = round(b["x"])
            if b["rect"].left > 1000:          # улетела за экран
                ichors.remove(b)
                continue
            offset = (sharkRect.x - b["rect"].x, sharkRect.y - b["rect"].y)
            if ichorMask.overlap(sharkMask, offset):   # попала в акулу
                ichors.remove(b)
                bossHp -= ICHOR_DAMAGE
                if bossHp <= 0:
                    bossHp = 0
                    bossWin()
                    break

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
        screen.blit(BackStart, (0, 0))
    elif level == 1:

        screen.blit(background_2, (0, 0))
        if pygame.time.get_ticks() < errorUntil:
            errText = smallFont.render(textErrorLogIn, True, (255, 60, 60))
            screen.blit(errText, errText.get_rect(center=(500, 100)))


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
        #screen.blit(winText, winText.get_rect(center=(500, 120)))

        pointsText = font.render(f"punkti: {totalScore}", True, (255, 255, 255))
        #screen.blit(pointsText, pointsText.get_rect(center=(500, 220)))

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



    elif level == 7:
        screen.blit(background_1, (0, 0))
        # луч рисуем до акулы, чтобы акула была сверху
        if rayState == "warn":
            screen.blit(rayWarnImg, rayRect)
        elif rayState == "fire":
            screen.blit(rayImg, rayRect)
        screen.blit(shark, sharkRect)
        for b in ichors:
            screen.blit(Ichor, b["rect"])

        # полоска HP босса
        pygame.draw.rect(screen, (60, 60, 60), (550, 20, 400, 25))
        pygame.draw.rect(screen, (220, 40, 40), (550, 20, 400 * bossHp / BOSS_MAX_HP, 25))
        pygame.draw.rect(screen, (255, 255, 255), (550, 20, 400, 25), 2)

        screen.blit(fish, fishRect)
        scoreText = font.render(str(totalScore), True, (255, 255, 255))
        screen.blit(scoreText, (20, 20))
        if paused:
            pauseText = font.render("pause", True, (255, 255, 255))
            screen.blit(pauseText, pauseText.get_rect(center=(500, 150)))


    pygame_widgets.update(events)
    pygame.display.flip()

pygame.quit()

add new Pipes png and they can change random, add token and password to login and register, add boss fight with shark and ray attack

#чтобы активировать сервер:
#1. открыть терминал
#2. перейти в папку с проектом
#3. выполнить команду: .venv/bin/python -m uvicorn api.main:app --reload