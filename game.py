import pygame
import sys
import random
import math

pygame.init()

# colours
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
GREEN = (50, 150, 0)
RED = (200, 0, 0)
YELLOW = (255, 215, 0)
DGREEN = (55, 128, 16)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)

# setup
sw, sh = 1000, 600  # multiples of 50
fps = 60
font = pygame.font.SysFont(None, 48)
screen = pygame.display.set_mode((sw, sh))
pygame.display.set_caption("Bomerman")
clock = pygame.time.Clock()
full = False

# load bomb image
bombimg = pygame.image.load("bomb_image.png")
bombimg = pygame.transform.scale(bombimg, (150, 150))
bombimgfl = pygame.transform.flip(bombimg, True, False)

# levels in tuples
def level1layout():
    rigid = set()
    rigid.add((9, 6))
    rigid.add((12, 5))
    soft = set()
    soft.add((6, 3)); soft.add((11, 3)); soft.add((6, 7))
    soft.add((11, 7)); soft.add((8, 6)); soft.add((10, 6))
    # clamp to bounds
    goodrig = set()
    for t in rigid:
        x = t[0]; y = t[1]
        if 2 <= x <= 17 and 2 <= y <= 9:
            goodrig.add((x, y))
    goodsoft = set()
    for t in soft:
        x = t[0]; y = t[1]
        if 2 <= x <= 17 and 2 <= y <= 9 and t not in goodrig:
            goodsoft.add((x, y))
    return goodrig, goodsoft

def level2layout():
    rigid = set()
    for col in (4, 10, 15):
        for y in range(3, 9):
            if not (col == 10 and (y == 5 or y == 7)):
                rigid.add((col, y))
    soft = set()
    for t in [(5, 3), (6, 3), (7, 3), (6, 5), (7, 5), (8, 5), (5, 6), (6, 6), (7, 6),
              (8, 4), (9, 4), (11, 4), (10, 5), (12, 5), (13, 5), (11, 7), (12, 7), (13, 7),
              (9, 8), (11, 8), (16, 8)]:
        soft.add(t)
    goodrig = set()
    for x, y in rigid:
        if 2 <= x <= 17 and 2 <= y <= 9:
            goodrig.add((x, y))
    goodsoft = set()
    for x, y in soft:
        if 2 <= x <= 17 and 2 <= y <= 9 and (x, y) not in goodrig:
            goodsoft.add((x, y))
    return goodrig, goodsoft

def level3layout():
    rigid = set()
    for x in range(2, 18):
        for y in range(2, 10):
            if x % 2 == 0 and y % 2 == 0:
                rigid.add((x, y))
    candidates = []
    for x in range(2, 18):
        for y in range(2, 10):
            if (x, y) not in rigid:
                candidates.append((x, y))
    soft = set()
    for x, y in candidates:
        if not (x <= 4 and y <= 4):
            if (x + 2 * y) % 2 == 0:
                soft.add((x, y))
    centerx = (2 + 17) // 2
    centery = (2 + 9) // 2
    for y in range(2, 10):
        if (centerx, y) in soft:
            soft.discard((centerx, y))
    for x in range(2, 18):
        if (x, centery) in soft:
            soft.discard((x, centery))
    for x in range(2, 6):
        for y in range(2, 6):
            if (x, y) in soft:
                soft.discard((x, y))
    goodrig = set()
    for x, y in rigid:
        if 2 <= x <= 17 and 2 <= y <= 9:
            goodrig.add((x, y))
    goodsoft = set()
    for x, y in soft:
        if 2 <= x <= 17 and 2 <= y <= 9 and (x, y) not in goodrig:
            goodsoft.add((x, y))
    return goodrig, goodsoft

levelmap = {1: level1layout, 2: level2layout, 3: level3layout}

def getlev(lv):
    f = levelmap.get(lv, level1layout)
    return f()

# player block
class Block:
    def __init__(self, x, y, size=50, col=BLUE):
        self.size = size
        self.col = col
        self.rect = pygame.Rect(x, y, size, size)
        self.ismoving = False
        self.startpos = self.rect.topleft
        self.targetpos = self.rect.topleft
        self.movedur = 450
        self.movestart = 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.col, self.rect)

    def update(self):
        if self.ismoving:
            now = pygame.time.get_ticks()
            el = now - self.movestart
            prog = min(el / self.movedur, 1)
            nx = int(self.startpos[0] + (self.targetpos[0] - self.startpos[0]) * prog)
            ny = int(self.startpos[1] + (self.targetpos[1] - self.startpos[1]) * prog)
            self.rect.topleft = (nx, ny)
            if prog >= 1:
                self.ismoving = False
                self.rect.topleft = (int(self.targetpos[0]), int(self.targetpos[1]))

    def try_move(self, dx, dy, blocked):
        if self.ismoving:
            return
        newx = self.rect.x + dx * self.size
        newy = self.rect.y + dy * self.size
        gx = newx // self.size
        gy = newy // self.size
        if (gx, gy) not in blocked:
            self.startpos = self.rect.topleft
            self.targetpos = (newx, newy)
            self.ismoving = True
            self.movestart = pygame.time.get_ticks()


# enemy block
class Enemy:
    def __init__(self, x, y, col, radius=20):
        self.x = int(x)
        self.y = int(y)
        self.col = col
        self.radius = radius
        self.nextmove = pygame.time.get_ticks() + random.randint(700, 1200)

    def draw(self, surface):
        pygame.draw.circle(surface, self.col, (self.x, self.y), self.radius)

    def update(self, blocksize, blocked, player_tile, mode, enempos, level):
        now = pygame.time.get_ticks()
        gx = self.x // blocksize
        gy = self.y // blocksize
        cur = (int(gx), int(gy))
        if mode == 'random':
            if level == 2:
                moveint = 2800
            elif level == 3:
                moveint = 2500
            else:
                moveint = 3000
            if now < self.nextmove:
                return
            dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            random.shuffle(dirs)
            for d in dirs:
                nx = gx + d[0]
                ny = gy + d[1]
                if (nx, ny) in blocked:
                    continue
                if (nx, ny) in enempos and (nx, ny) != cur:
                    continue
                try:
                    enempos.discard(cur)
                except Exception:
                    pass
                self.x = int(nx * blocksize + blocksize // 2)
                self.y = int(ny * blocksize + blocksize // 2)
                enempos.add((nx, ny))
                break
            self.nextmove = now + moveint
            return
        # chase mode
        if now < self.nextmove:
            return
        self.nextmove = now + random.randint(1200, 1400)
        px, py = player_tile
        dx = px - gx
        dy = py - gy
        stepx = 0
        stepy = 0
        if abs(dx) > abs(dy):
            stepx = 1 if dx > 0 else -1 if dx < 0 else 0
        else:
            stepy = 1 if dy > 0 else -1 if dy < 0 else 0
        candidates = [(gx + stepx, gy + stepy)]
        if stepx != 0 and stepy == 0:
            candidates.append((gx, gy + (1 if dy > 0 else -1)))
        if stepy != 0 and stepx == 0:
            candidates.append((gx + (1 if dx > 0 else -1), gy))
        moved = False
        for nx, ny in candidates:
            if (nx, ny) not in blocked and ((nx, ny) not in enempos or (nx, ny) == cur):
                try:
                    enempos.discard(cur)
                except Exception:
                    pass
                self.x = int(nx * blocksize + blocksize // 2)
                self.y = int(ny * blocksize + blocksize // 2)
                enempos.add((nx, ny))
                moved = True
                break
        if not moved:
            dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            random.shuffle(dirs)
            for d in dirs:
                nx = gx + d[0]
                ny = gy + d[1]
                if (nx, ny) in blocked:
                    continue
                if (nx, ny) in enempos and (nx, ny) != cur:
                    continue
                try:
                    enempos.discard(cur)
                except Exception:
                    pass
                self.x = int(nx * blocksize + blocksize // 2)
                self.y = int(ny * blocksize + blocksize // 2)
                enempos.add((nx, ny))
                break


# bomb/explosion logic
class Bomb:
    def __init__(self, gx, gy, placed):
        self.gx = gx
        self.gy = gy
        self.placed = placed
        self.expl = False

    def draw(self, surface, blocksize):
        px = int(self.gx * blocksize)
        py = int(self.gy * blocksize)
        w = int(blocksize)
        h = int(blocksize)
        img = pygame.transform.scale(bombimg, (w, h))
        surface.blit(img, (px, py))

class Explosion:
    def __init__(self, tiles, startt, dur=500):
        self.tiles = tiles
        self.startt = startt
        self.dur = dur

    def draw(self, surface, blocksize):
        for tx, ty in self.tiles:
            rect = pygame.Rect(int(tx * blocksize), int(ty * blocksize), int(blocksize), int(blocksize))
            pygame.draw.rect(surface, ORANGE, rect)

    def is_active(self):
        return pygame.time.get_ticks() - self.startt < self.dur


# button logic
class Button:
    def __init__(self, x, y, text, action, col=GREY):
        self.rect = pygame.Rect(x, y, 300, 60)
        self.text = text
        self.action = action
        self.col = col

    def draw(self, surface):
        pygame.draw.rect(surface, self.col, self.rect)
        textsurf = font.render(self.text, True, BLACK)
        surface.blit(textsurf, textsurf.get_rect(center=self.rect.center))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.action()


# UI features

def quit_game():
    pygame.quit()
    sys.exit()


def toggle_full():
    global full, screen
    full = not full
    if full:
        screen = pygame.display.set_mode((sw, sh), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((sw, sh))


def draw_grid(surface, blocksize, rigidint, softint):
    blocked = set()
    maxx = sw // blocksize
    maxy = sh // blocksize
    # Draw border (2-thick) as rigid white
    for x in range(0, maxx):
        for y in range(0, maxy):
            if x <= 1 or x >= maxx - 2 or y <= 1 or y >= maxy - 2:
                pygame.draw.rect(surface, WHITE, (int(x * blocksize), int(y * blocksize), int(blocksize), int(blocksize)))
                blocked.add((x, y))
    for x, y in rigidint:
        pygame.draw.rect(surface, WHITE, (int(x * blocksize), int(y * blocksize), int(blocksize), int(blocksize)))
        blocked.add((x, y))
    for x, y in softint:
        pygame.draw.rect(surface, GREY, (int(x * blocksize), int(y * blocksize), int(blocksize), int(blocksize)))
        blocked.add((x, y))
    for x in range(0, maxx):
        for y in range(0, maxy):
            if (x, y) not in blocked:
                pygame.draw.rect(surface, WHITE, (int(x * blocksize), int(y * blocksize), int(blocksize), int(blocksize)), 1)
    return blocked


def spawn_enemy(blocksize, blocked, playerpos, ecol, enempos):
    maxx = sw // blocksize
    maxy = sh // blocksize
    px = playerpos[0] // blocksize
    py = playerpos[1] // blocksize
    attempts = 0
    while True:
        x = random.randint(0, maxx - 1)
        y = random.randint(0, maxy - 1)
        attempts += 1
        if attempts > 1000:
            return None
        if (x, y) in blocked:
            continue
        if (x, y) in enempos:
            continue
        if abs(x - px) <= 3 and abs(y - py) <= 3:
            continue
        enempos.add((x, y))
        ex = x * blocksize + blocksize // 2
        ey = y * blocksize + blocksize // 2
        return Enemy(ex, ey, ecol)


# death screen

def death_screen_with_score(score):
    buttons = [Button(330, 280, "Return to Menu", main_menu)]
    while True:
        screen.fill(DGREEN)
        title = font.render("You Died", True, WHITE)
        screen.blit(title, title.get_rect(center=((sw // 2) - 20, 70)))
        score_surf = font.render(f"Score: {score}", True, RED)
        screen.blit(score_surf, score_surf.get_rect(center=((sw // 2) - 20, 140)))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            for b in buttons:
                b.handle(event)
        for b in buttons:
            b.draw(screen)
        pygame.display.flip()
        clock.tick(fps)


# main game

def game_screen(level=1, col=RED):
    startx, starty = 2, 2
    block = Block(startx * 50, starty * 50)
    paused = False
    def return_to_menu():
        nonlocal running
        running = False
        main_menu()
    pausebuttons = [Button(330, 280, "Back to Menu", return_to_menu)]

    enemies = []
    enempos = set()
    blocksize = block.size
    # Enemy settings per level colour
    if col == RED:
        maxe = 1; ecol = GREEN
    elif col == GREEN:
        maxe = 5; ecol = RED
    elif col == YELLOW:
        maxe = 3; ecol = RED
    else:
        maxe = 1; ecol = RED

    rigidint, softint = getlev(level)
    softint = set(softint)
    score = 0
    activebomb = None
    explosions = []

    blocked_preview = draw_grid(screen, blocksize, rigidint, softint)
    if maxe > 0:
        e = spawn_enemy(blocksize, blocked_preview, block.rect.topleft, ecol, enempos)
        if e:
            enemies.append(e)
    lastspawn = pygame.time.get_ticks()
    spawndelay = random.randint(5000, 10000)
    chase = False
    modetimer = pygame.time.get_ticks()
    running = True

    while running:
        screen.fill(col)
        blocked = draw_grid(screen, blocksize, rigidint, softint)
        now = pygame.time.get_ticks()
        mode_text = ""
        if level == 3:
            elapsed = now - modetimer
            if not chase:
                if elapsed >= 30000:
                    chase = True; modetimer = now; elapsed = 0
                mode_text = f"Random for: {max(0, (30000 - elapsed)//1000)}"
            else:
                if elapsed >= 10000:
                    chase = False; modetimer = now; elapsed = 0
                mode_text = f"Chasing for: {max(0, (10000 - elapsed)//1000)}"
        else:
            chase = False
        score_surf = font.render(f"Score: {score}", True, RED)
        screen.blit(score_surf, (10, 10))
        if maxe > 1 and len(enemies) < maxe:
            if now - lastspawn >= spawndelay:
                newe = spawn_enemy(blocksize, blocked, block.rect.topleft, ecol, enempos)
                if newe:
                    enemies.append(newe)
                    lastspawn = now
                    spawndelay = random.randint(5000, 10000)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = not paused
            elif paused:
                for b in pausebuttons:
                    b.handle(event)
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if activebomb is None:
                        gx = block.rect.x // blocksize
                        gy = block.rect.y // blocksize
                        activebomb = Bomb(gx, gy, pygame.time.get_ticks())
                if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                    toggle_full()
        if not paused:
            keys = pygame.key.get_pressed()
            if not block.ismoving:
                if keys[pygame.K_LEFT]: block.try_move(-1, 0, blocked)
                elif keys[pygame.K_RIGHT]: block.try_move(1, 0, blocked)
                elif keys[pygame.K_UP]: block.try_move(0, -1, blocked)
                elif keys[pygame.K_DOWN]: block.try_move(0, 1, blocked)
        block.update()
        if activebomb is not None:
            if pygame.time.get_ticks() - activebomb.placed >= 2500:
                bx, by = activebomb.gx, activebomb.gy
                expl = [(bx, by)]
                dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                for d in dirs:
                    for r in (1, 2):
                        tx = bx + d[0] * r
                        ty = by + d[1] * r
                        if tx < 0 or tx >= sw // blocksize or ty < 0 or ty >= sh // blocksize:
                            break
                        if (tx, ty) in rigidint:
                            break
                        expl.append((tx, ty))
                        if (tx, ty) in softint:
                            break
                explosions.append(Explosion(expl, pygame.time.get_ticks()))
                activebomb = None
                removed = []
                for tx, ty in expl:
                    if (tx, ty) in softint:
                        softint.discard((tx, ty))
                    if (tx, ty) in enempos:
                        removed.append((tx, ty)); enempos.discard((tx, ty))
                if removed:
                    removed_count = 0
                    newlist = []
                    for e in enemies:
                        et = (e.x // blocksize, e.y // blocksize)
                        if et in removed:
                            removed_count += 1
                            continue
                        newlist.append(e)
                    enemies = newlist
                    if level == 3:
                        score += 150 * removed_count
                    else:
                        score += 100 * removed_count
                    if level == 1 and removed_count > 0:
                        run_screen(f"You Win - Score: {score}", [Button(330, 280, "Return to Menu", main_menu)])
                        return
                player_tile = (block.rect.x // blocksize, block.rect.y // blocksize)
                if player_tile in expl:
                    running = False
                    death_screen_with_score(score)
                    return
        explosions = [ex for ex in explosions if ex.is_active()]
        if activebomb is not None:
            activebomb.draw(screen, blocksize)
        for ex in explosions:
            ex.draw(screen, blocksize)
        enempos = set((e.x // blocksize, e.y // blocksize) for e in enemies)
        for e in enemies[:]:
            e.update(blocksize, blocked, (block.rect.x // blocksize, block.rect.y // blocksize), 'chase' if chase else 'random', enempos, level)
            pt = (block.rect.x // blocksize, block.rect.y // blocksize)
            et = (e.x // blocksize, e.y // blocksize)
            if pt == et:
                running = False
                death_screen_with_score(score)
                return
        if paused:
            screen.fill((30, 30, 30))
            ptext = font.render("Paused - Press ESC to Resume", True, WHITE)
            screen.blit(ptext, ptext.get_rect(center=(sw // 2, sh // 2 - 100)))
            for b in pausebuttons: b.draw(screen)
        else:
            block.draw(screen)
            for e in enemies: e.draw(screen)
            if level == 3:
                mode_surf = font.render(mode_text, True, BLACK)
                screen.blit(mode_surf, (sw - 300, 20))
        pygame.display.flip(); clock.tick(fps)


# run screen/menus

def run_screen(title, buttons, include_bombs=False):
    while True:
        screen.fill(DGREEN)
        t = font.render(title, True, WHITE)
        screen.blit(t, t.get_rect(center=((sw // 2) - 20, 70)))
        if include_bombs:
            screen.blit(bombimg, (50, sh // 2 - 80))
            screen.blit(bombimgfl, (sw - 200, sh // 2 - 80))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit_game()
            for b in buttons: b.handle(event)
        for b in buttons: b.draw(screen)
        pygame.display.flip(); clock.tick(fps)


def main_menu():
    buttons = [Button(330, 150, "Level Selection", level_selection), Button(330, 230, "Settings", settings_menu), Button(330, 310, "Quit", quit_game)]
    run_screen("Bomerman", buttons, include_bombs=True)

def level_selection():
    buttons = [Button(330, 150, "Level 1", lambda: game_screen(level=1, col=RED)), Button(330, 230, "Level 2", lambda: game_screen(level=2, col=YELLOW)), Button(330, 310, "Level 3", lambda: game_screen(level=3, col=GREEN)), Button(330, 390, "Back to Menu", main_menu)]
    run_screen("Select Level", buttons)

def settings_menu():
    buttons = [Button(330, 200, "Toggle Fullscreen", toggle_full), Button(330, 280, "Back to Menu", main_menu)]
    run_screen("Settings", buttons)

main_menu()
