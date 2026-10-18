from game.constants import POINTS_PER_PIPE, BOSS_MAX_POINTS, BOSS_MIN_POINTS

def pipe_points(game_level):
    return POINTS_PER_PIPE[game_level - 1]

def ichor_points(bullet_center_y, shark_center_y, shark_height):
    max_dist = shark_height / 2
    if max_dist == 0:
        return BOSS_MAX_POINTS
    k = min(abs(bullet_center_y - shark_center_y) / max_dist, 1.0)
    return round(BOSS_MAX_POINTS - k * (BOSS_MAX_POINTS - BOSS_MIN_POINTS))