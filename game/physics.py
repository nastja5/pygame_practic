from game.constants import GRAVITY, JUMP_SPEED, START_Y, SCREEN_H, BOSS_MAX_HP

class FishBody:
    def __init__(self):
        self.y = float(START_Y)
        self.speed_y = 0.0

    def update(self, dt):
        self.speed_y += GRAVITY * dt
        self.y += self.speed_y * dt

    def jump(self):
        self.speed_y = JUMP_SPEED

    def reset(self):
        self.y = float(START_Y)
        self.speed_y = 0.0

class SharkBody:
    def __init__(self, height):
        self.height = height
        self.y = 300.0
        self.speed_y = 169.0
        self.hp = BOSS_MAX_HP

    def move(self, dt):
        self.y += self.speed_y * dt
        if self.y + self.height >= SCREEN_H or self.y <= 0:
            self.speed_y = -self.speed_y

    def reset(self):
        self.y = 300.0
        self.speed_y = 250.0
        self.hp = BOSS_MAX_HP