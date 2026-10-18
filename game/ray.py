from game.constants import RAY_COOLDOWN, RAY_WARN, RAY_FIRE

class RayAttack:
    def __init__(self):
        self.state = "idle"
        self.timer = 0.0

    def reset(self):
        self.state = "idle"
        self.timer = 0.0

    def update(self, dt):
        self.timer += dt
        if self.state == "idle" and self.timer >= RAY_COOLDOWN:
            self.state = "warn"
            self.timer = 0.0
            return "warn"
        if self.state == "warn" and self.timer >= RAY_WARN:
            self.state = "fire"
            self.timer = 0.0
        elif self.state == "fire" and self.timer >= RAY_FIRE:
            self.state = "idle"
            self.timer = 0.0
        return None