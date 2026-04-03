import pygame
import pytmx
import pyscroll
import random
from typing import Optional, Any
import lewelOne
import lewelTwo
import lewelThree

SCREEN_WIDTH, SCREEN_HEIGHT = 600, 340

# Globalne zmienne silnika
tmx_data: Any = None
map_layer: Any = None
group: Optional[pyscroll.PyscrollGroup] = None
platforms: list = []
traps: list = []
exits: list = []
triggers: list = []
moving_platforms = pygame.sprite.Group()
moving_saws = pygame.sprite.Group()
falling_stones = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
iron_heads = pygame.sprite.Group()
fruits_group = pygame.sprite.Group()
surprise_traps = pygame.sprite.Group()

current_level_module = lewelOne
last_used_spawn = "PlayerSpawn"
score = 0
level_start_score = 0
pending_level_change = None

# --- ZMIENNE STANU I EFEKTÓW ---
boss_timer = 60.0
boss_active = False
show_results = False
transition_active = False
tiles_to_remove = []
fallen_tiles = []
black_tile_surf = pygame.Surface((16, 16))
black_tile_surf.fill((0, 0, 0))

fruits_points_session = 0
time_points_session = 0


# --- KLASY OBIEKTÓW ---

class SurpriseSpikeHead(pygame.sprite.Sprite):
    def __init__(self, obj):
        super().__init__()
        self._layer = 2
        try:
            self.full_image = pygame.image.load("assets/Traps/Spike Head/Idle.png").convert_alpha()
        except (pygame.error, FileNotFoundError):
            self.full_image = pygame.Surface((54, 52))
            self.full_image.fill((200, 0, 0))

        self.transparent_image = pygame.Surface(self.full_image.get_size(), pygame.SRCALPHA)
        self.image = self.transparent_image
        self.rect = self.image.get_rect(topleft=(obj.x, obj.y))
        self.start_pos = pygame.math.Vector2(self.rect.topleft)
        self.tid = str(obj.properties.get('trigger_id', 'SH_Trigger'))
        self.dist = float(obj.properties.get('dist', 80.0))
        self.speed = float(obj.properties.get('speed', 6.0))
        self.is_triggered = False
        self.returning = False
        self.finished = False

    def update(self, *args, **kwargs):
        if self.is_triggered and not self.finished:
            self.image = self.full_image
            if not self.returning:
                self.rect.y -= int(self.speed)
                if self.rect.y <= self.start_pos.y - self.dist:
                    self.returning = True
            else:
                self._layer = 4
                self.rect.y += int(self.speed * 0.4)
                if self.rect.y >= self.start_pos.y:
                    self.rect.y = int(self.start_pos.y)
                    self.is_triggered = False
                    self.returning = False
                    self.finished = True


class Fruit(pygame.sprite.Sprite):
    def __init__(self, obj):
        super().__init__()
        self.fruit_type = obj.properties.get('fruit_type', 'Apple')
        self.points = int(obj.properties.get('points', 1))
        self.frames = []
        try:
            raw_img = pygame.image.load(f"assets/Items/Fruits/{self.fruit_type}.png")
            sheet = raw_img.convert_alpha()
            for i in range(17):
                frame_img = sheet.subsurface((i * 32, 0, 32, 32))
                self.frames.append(pygame.transform.scale_by(frame_img, 1.5))
        except (pygame.error, FileNotFoundError):
            self.frames = [pygame.Surface((48, 48))]
            self.frames[0].fill((0, 255, 0))

        self.collected_frames = []
        try:
            c_raw = pygame.image.load("assets/Items/Fruits/Collected.png")
            c_sheet = c_raw.convert_alpha()
            for i in range(6):
                c_frame = c_sheet.subsurface((i * 32, 0, 32, 32))
                self.collected_frames.append(pygame.transform.scale_by(c_frame, 1.5))
        except (pygame.error, FileNotFoundError):
            pass

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(int(obj.x + 8), int(obj.y + 8)))
        self.anim_index = 0.0
        self.is_collected = False

    def update(self, *args, **kwargs):
        self.anim_index += 0.25
        if not self.is_collected:
            self.image = self.frames[int(self.anim_index % len(self.frames))]
        else:
            idx = int(self.anim_index)
            if idx < len(self.collected_frames):
                self.image = self.collected_frames[idx]
            else:
                self.kill()

    def collect(self):
        if not self.is_collected:
            self.is_collected = True
            self.anim_index = 0.0
            if collect_sfx: collect_sfx.play()
            return self.points
        return 0


class Boss(pygame.sprite.Sprite):
    def __init__(self, obj):
        super().__init__()
        try:
            raw_img = pygame.image.load("assets/Main Characters/Icewalker.png")
            self.image = raw_img.convert_alpha()
        except (pygame.error, FileNotFoundError):
            self.image = pygame.Surface((64, 64))
            self.image.fill((0, 0, 255))
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(topleft=(obj.x, obj.y))
        self.pos_vec = pygame.math.Vector2(self.rect.topleft)
        self.start_x = float(obj.x)
        self.speed = float(obj.properties.get('speed', 2.0))
        self.dist = float(obj.properties.get('dist', 250.0))
        self.health, self.direction = 2, 1
        self.hit_stun_timer, self.visible, self.is_dying, self.death_timer = 0, True, False, 0

    def update(self, *args, **kwargs):
        global score, boss_active, boss_timer, transition_active, tiles_to_remove, fruits_points_session, time_points_session
        if self.is_dying:
            if boss_active:
                fruits_points_session = score
                time_points_session = int(boss_timer) * 10
                score += time_points_session
                boss_active = False
            self.death_timer -= 1
            if self.death_timer % 3 == 0: self.visible = not self.visible
            self.image = self.original_image if self.visible else pygame.Surface(self.rect.size, pygame.SRCALPHA)
            if self.death_timer <= 0:
                player.is_dead = True
                player.image = pygame.Surface((0, 0))
                tiles_to_remove.clear()
                for tx in range(0, SCREEN_WIDTH, 16):
                    for ty in range(0, SCREEN_HEIGHT, 16):
                        tiles_to_remove.append((tx, ty))
                random.shuffle(tiles_to_remove)
                transition_active = True
                self.kill()
            return
        if self.hit_stun_timer > 0:
            self.hit_stun_timer -= 1
            if self.hit_stun_timer % 5 == 0: self.visible = not self.visible
            self.image = self.original_image if self.visible else pygame.Surface(self.rect.size, pygame.SRCALPHA)
            if self.hit_stun_timer == 0: self.visible, self.image = True, self.original_image
            return
        self.pos_vec.x += self.speed * self.direction
        if abs(self.pos_vec.x - self.start_x) >= abs(self.dist):
            self.direction *= -1
        self.rect.x = round(self.pos_vec.x)

    def hit(self):
        if self.is_dying: return
        self.health -= 1
        if self.health == 1:
            if boss_hit_sfx: boss_hit_sfx.play()
            self.hit_stun_timer, self.speed = 40, self.speed * 0.5
        elif self.health <= 0:
            if boss_death_sfx: boss_death_sfx.play()
            self.is_dying, self.death_timer = True, 90


class IronHead(pygame.sprite.Sprite):
    def __init__(self, obj):
        super().__init__()
        try:
            raw_img = pygame.image.load("assets/Traps/Rock Head/Blink (42x42).png")
            sheet = raw_img.convert_alpha()
            self.frames = [sheet.subsurface((i * 42, 0, 42, 42)) for i in range(4)]
        except (pygame.error, FileNotFoundError):
            self.frames = [pygame.Surface((42, 42))]
            self.frames[0].fill((150, 150, 150))
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(obj.x, obj.y))
        self.spawn_pos = pygame.math.Vector2(self.rect.topleft)
        self.tid = str(obj.properties.get('trigger_id', '0'))
        self.fall_speed, self.respawn_time = float(obj.properties.get('speed', 6.0)), 500
        self.is_falling, self.is_waiting_respawn, self.is_triggered, self.respawn_timer, self.anim_index, self.freeze_timer = False, False, False, 0, 0.0, 0

    def update(self, *args, **kwargs):
        if self.freeze_timer > 0:
            self.freeze_timer -= 1
            if self.freeze_timer == 0: self.start_respawn()
            return
        if not self.is_waiting_respawn and not self.is_falling:
            self.anim_index += 0.05
            self.image = self.frames[int(self.anim_index % len(self.frames))]
        if self.is_falling:
            self.rect.y += int(self.fall_speed)
            if self.rect.y > SCREEN_HEIGHT + 100: self.start_respawn()
        if self.is_waiting_respawn:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0: self.respawn()

    def start_respawn(self):
        self.is_falling, self.is_waiting_respawn, self.respawn_timer, self.rect.y = False, True, self.respawn_time, -2000

    def respawn(self):
        self.is_waiting_respawn, self.is_triggered = False, False
        self.rect.topleft = (int(self.spawn_pos.x), int(self.spawn_pos.y))


class MovingSaw(pygame.sprite.Sprite):
    def __init__(self, obj):
        super().__init__()
        try:
            raw_img = pygame.image.load("assets/Traps/Saw/On (38x38).png")
            sheet = raw_img.convert_alpha()
            self.frames = [sheet.subsurface((i * 38, 0, 38, 38)) for i in range(8)]
        except (pygame.error, FileNotFoundError):
            self.frames = [pygame.Surface((38, 38))]
            self.frames[0].fill((255, 0, 0))
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(int(obj.x + obj.width // 2), int(obj.y + obj.height // 2)))
        self.pos_vec, self.start_pos = pygame.math.Vector2(self.rect.topleft), pygame.math.Vector2(self.rect.topleft)
        self.axis, self.dist, self.speed, self.anim_speed, self.direction, self.frame_index = obj.properties.get('axis',
                                                                                                                 'y'), float(
            obj.properties.get('dist', 100)), float(obj.properties.get('speed', 2.0)), float(
            obj.properties.get('anim_speed', 0.2)), 1, 0.0

    def update(self, *args, **kwargs):
        self.frame_index += self.anim_speed
        if self.frame_index >= len(self.frames): self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        if self.axis == 'y':
            self.pos_vec.y += self.speed * self.direction
            if abs(self.pos_vec.y - self.start_pos.y) >= abs(self.dist): self.direction *= -1
        else:
            self.pos_vec.x += self.speed * self.direction
            if abs(self.pos_vec.x - self.start_pos.x) >= abs(self.dist): self.direction *= -1
        self.rect.topleft = (round(self.pos_vec.x), round(self.pos_vec.y))


class FallingStone(pygame.sprite.Sprite):
    def __init__(self, obj):
        super().__init__()
        self.image = obj.image if obj.image else pygame.Surface((obj.width, obj.height))
        if not obj.image: self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(obj.x, obj.y))
        self.pos_vec, self.name = pygame.math.Vector2(self.rect.topleft), obj.name
        self.activated_by, self.instant_death, self.on_impact = obj.properties.get('activated_by',
                                                                                   ''), obj.properties.get(
            'instant_death', True), obj.properties.get('on_impact', 'stop')
        self.velocity, self.gravity, self.is_falling = 0.0, 0.5, False

    def update(self, *args, **kwargs):
        if self.is_falling:
            self.velocity += self.gravity
            self.pos_vec.y += self.velocity
            self.rect.y = round(self.pos_vec.y)
            for p in platforms:
                if self.rect.colliderect(p):
                    if self.on_impact == "destroy":
                        self.kill()
                    else:
                        self.rect.bottom = p.top
                        self.is_falling = False
                        self.velocity = 0.0
                        self.pos_vec.y = float(self.rect.y)


class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, obj):
        super().__init__()
        self.image = pygame.Surface((obj.width, obj.height), pygame.SRCALPHA)
        if obj.image:
            tw = obj.image.get_width()
            for x in range(0, int(obj.width), tw): self.image.blit(obj.image, (x, 0))
        else:
            self.image.fill((150, 75, 0))
        self.rect, self.pos_vec = self.image.get_rect(topleft=(obj.x, obj.y)), pygame.math.Vector2(obj.x, obj.y)
        self.start_pos = pygame.math.Vector2(obj.x, obj.y)
        self.axis, self.dist, self.speed = obj.properties.get('axis', 'x'), obj.properties.get('dist',
                                                                                               100), obj.properties.get(
            'speed', 1.0)
        self.direction, self.vel = 1, pygame.math.Vector2(0, 0)

    def update(self, *args, **kwargs):
        old_x, old_y = self.rect.x, self.rect.y
        if self.axis == 'x':
            self.pos_vec.x += self.speed * self.direction
            if abs(self.pos_vec.x - self.start_pos.x) >= abs(self.dist): self.direction *= -1
        else:
            self.pos_vec.y += self.speed * self.direction
            if abs(self.pos_vec.y - self.start_pos.y) >= abs(self.dist): self.direction *= -1
        self.rect.topleft, self.vel = (round(self.pos_vec.x), round(self.pos_vec.y)), pygame.math.Vector2(
            self.rect.x - old_x, self.rect.y - old_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        raw_img = pygame.image.load("assets/Main Characters/Ninja Frog/Idle (32x32).png").convert_alpha()
        self.idle_img = raw_img.subsurface((0, 0, 32, 32))
        raw_dj = pygame.image.load("assets/Main Characters/Ninja Frog/Double Jump (32x32).png").convert_alpha()
        self.dj_frames = [raw_dj.subsurface((i * 32, 0, 32, 32)) for i in range(6)]
        self.image, self.rect = self.idle_img, self.idle_img.get_rect(topleft=pos)
        self.position, self.velocity = pygame.math.Vector2(pos), pygame.math.Vector2(0, 0)
        self.gravity, self.jump_speed = 0.8, -11
        self.on_ground, self.can_double_jump, self.facing_right, self.is_doing_flip, self.flip_index, self.is_dead = False, False, True, False, 0.0, False

    def get_input(self):
        if self.is_dead: self.velocity.x = 0; return
        keys = pygame.key.get_pressed()
        self.velocity.x = -4 if keys[pygame.K_LEFT] else 4 if keys[pygame.K_RIGHT] else 0
        if self.velocity.x < 0:
            self.facing_right = False
        elif self.velocity.x > 0:
            self.facing_right = True

    def handle_jump(self):
        if self.is_dead: return
        if self.on_ground:
            self.velocity.y, self.on_ground, self.can_double_jump, self.is_doing_flip = self.jump_speed, False, True, False
            if jump_sfx: jump_sfx.stop(); jump_sfx.play()
        elif self.can_double_jump:
            self.velocity.y, self.can_double_jump, self.is_doing_flip, self.flip_index = self.jump_speed, False, True, 0.0
            if jump_sfx: jump_sfx.stop(); jump_sfx.play()

    def update(self, *args, **kwargs):
        self.get_input()
        if self.is_doing_flip:
            self.flip_index += 0.2
            if self.flip_index >= len(self.dj_frames):
                self.is_doing_flip, self.image = False, self.idle_img
            else:
                self.image = self.dj_frames[int(self.flip_index)]
        else:
            self.image = self.idle_img
        if not self.facing_right: self.image = pygame.transform.flip(self.image, True, False)


# --- FUNKCJE POMOCNICZE ---

def draw_ui():
    score_surface = gui_font.render(f"SCORE: {score}", True, (255, 255, 255))
    rect_ui = score_surface.get_rect(topright=(SCREEN_WIDTH - 20, 20))
    shadow_ui = gui_font.render(f"SCORE: {score}", True, (0, 0, 0))
    screen.blit(shadow_ui, (rect_ui.x + 2, rect_ui.y + 2))
    screen.blit(score_surface, rect_ui)
    if boss_active:
        t_surf = gui_font.render(f"TIME: {int(boss_timer)}", True, (255, 255, 255))
        screen.blit(t_surf, (SCREEN_WIDTH // 2 - t_surf.get_width() // 2, 20))


def draw_end_screen():
    screen.fill((0, 0, 0))
    t_surf = gui_font.render("CONGRATULATIONS !!", True, (255, 215, 0))
    screen.blit(t_surf, (SCREEN_WIDTH // 2 - t_surf.get_width() // 2, 40))
    f_txt = gui_font.render(f"FRUITS - {fruits_points_session} pkt", True, (200, 200, 200))
    t_txt = gui_font.render(f"FIGHT  - {time_points_session} pkt", True, (200, 200, 200))
    tot_txt = gui_font.render(f"TOTAL POINTS - {score} pkt", True, (255, 255, 255))
    screen.blit(f_txt, (SCREEN_WIDTH // 2 - 80, 110))
    screen.blit(t_txt, (SCREEN_WIDTH // 2 - 80, 140))
    pygame.draw.line(screen, (255, 255, 255), (SCREEN_WIDTH // 2 - 110, 180), (SCREEN_WIDTH // 2 + 110, 180), 2)
    screen.blit(tot_txt, (SCREEN_WIDTH // 2 - tot_txt.get_width() // 2, 210))
    res_col = (0, 255, 0) if pygame.time.get_ticks() % 1000 < 600 else (0, 100, 0)
    res_txt = gui_font.render("> PRESS SPACE TO RESTART <", True, res_col)
    screen.blit(res_txt, (SCREEN_WIDTH // 2 - res_txt.get_width() // 2, 280))


def trigger_death():
    global score, boss_active
    player.is_dead, score, boss_active = True, level_start_score, False
    player.velocity = pygame.math.Vector2(0, 0)
    if death_sfx: death_sfx.play()
    group.draw(screen)
    pygame.display.flip()
    pygame.time.delay(1000)
    player.is_dead = False
    load_level(current_level_module, spawn_name=last_used_spawn)


def load_level(level_module: Any, spawn_name: str = "PlayerSpawn"):
    global tmx_data, map_layer, group, platforms, traps, exits, triggers, current_level_module, last_used_spawn, boss_active, boss_timer
    current_level_module, last_used_spawn = level_module, spawn_name
    platforms.clear()
    traps.clear()
    exits.clear()
    triggers.clear()
    moving_platforms.empty()
    moving_saws.empty()
    falling_stones.empty()
    boss_group.empty()
    iron_heads.empty()
    fruits_group.empty()
    surprise_traps.empty()

    tmx_data = pytmx.util_pygame.load_pygame(level_module.MAP_PATH)
    map_data = pyscroll.data.TiledMapData(tmx_data)
    map_layer = pyscroll.BufferedRenderer(map_data, (SCREEN_WIDTH, SCREEN_HEIGHT), clamp_camera=True)
    group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=3)

    found_pos = None
    for name in [spawn_name, "SpawnPlayer2", "PlayerSpawn", "FinalSpawn"]:
        for obj in tmx_data.objects:
            if str(obj.name) == name: found_pos, last_used_spawn = (obj.x, obj.y), name; break
        if found_pos: break

    player.position, player.rect.topleft, player.velocity = pygame.math.Vector2(found_pos or (100, 100)), (
    int(found_pos[0]), int(found_pos[1])) if found_pos else (100, 100), pygame.math.Vector2(0, 0)

    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for tx, ty, gid in layer:
                if not gid: continue
                r = pygame.Rect(tx * 16, ty * 16, 16, 16)
                if layer.name in level_module.TRAP_LAYERS:
                    traps.append(r)
                elif layer.name in level_module.GROUND_LAYERS:
                    platforms.append(r)
        elif isinstance(layer, pytmx.TiledObjectGroup):
            for obj in layer:
                obj_tp = str(getattr(obj, 'class_', getattr(obj, 'type', ""))).lower()
                if "wyjscie" in str(obj.name).lower() or obj_tp == "exit":
                    exits.append({'rect': pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height)),
                                  'name': str(obj.name)})
                elif obj_tp == "movingplat":
                    moving_platforms.add(MovingPlatform(obj)); group.add(moving_platforms.sprites()[-1])
                elif obj_tp == "movingsaw" or obj.name == "saw":
                    moving_saws.add(MovingSaw(obj)); group.add(moving_saws.sprites()[-1])
                elif obj_tp == "fallingstone":
                    falling_stones.add(FallingStone(obj)); group.add(falling_stones.sprites()[-1])
                elif obj.name == "BossAnchor":
                    iron_heads.add(IronHead(obj)); group.add(iron_heads.sprites()[-1])
                elif obj.name == "BossSpawn":
                    boss_group.add(Boss(obj)); group.add(boss_group.sprites()[-1])
                elif obj.name == "SpikedHead" or obj_tp == "surprise":
                    surprise_traps.add(SurpriseSpikeHead(obj)); group.add(surprise_traps.sprites()[-1])
                elif obj_tp == "fruit":
                    fruits_group.add(Fruit(obj)); group.add(fruits_group.sprites()[-1])
                elif obj_tp == "trigger" or "Trigger" in str(obj.name):
                    triggers.append({
                        'rect': pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height)),
                        'name': str(obj.name),
                        'tid': str(obj.properties.get('trigger_id', ''))
                    })

    boss_active, boss_timer = (True, 60.0) if len(boss_group) > 0 else (False, 0.0)
    group.add(player)


def check_collisions():
    global score, pending_level_change
    if not tmx_data: return
    mw = int(tmx_data.width * 16)
    mh = tmx_data.height * 16

    player.position.x += player.velocity.x
    player.rect.x = round(player.position.x)

    # 1. NAPRAWA BŁĘDU INT/FLOAT (Zamiast linii 441)
    if player.rect.left < 0:
        player.rect.left = 0
    limit_prawy = int(mw) - player.rect.width
    if player.rect.left > limit_prawy:
        player.rect.left = limit_prawy

    for p in platforms:
        if player.rect.colliderect(p):
            if player.velocity.x > 0:
                player.rect.right = p.left
            else:
                player.rect.left = p.right
    player.position.x = float(player.rect.x)

    player.velocity.y += player.gravity
    player.position.y += player.velocity.y
    player.rect.y = round(player.position.y)
    player.on_ground = False
    if player.rect.top > mh + 50: trigger_death(); return

    for plat in moving_platforms:
        if player.rect.inflate(0, 4).colliderect(plat.rect) and player.velocity.y >= 0:
            player.rect.bottom, player.velocity.y, player.on_ground = plat.rect.top, 0, True
            player.position.x += plat.vel.x
            player.rect.x = round(player.position.x)

    for p in platforms:
        if player.rect.colliderect(p):
            if player.velocity.y > 0:
                player.rect.bottom, player.velocity.y, player.on_ground = p.top, 0, True
            else:
                player.rect.top, player.velocity.y = p.bottom, 0
    player.position.y = float(player.rect.y)

    death_hit = player.rect.inflate(-12, -12)
    for s in moving_saws:
        if death_hit.colliderect(s.rect): trigger_death(); return
    for t in traps:
        if death_hit.colliderect(t): trigger_death(); return
    for sh in surprise_traps:
        if death_hit.colliderect(sh.rect): trigger_death(); return

    #  ZABIJANIE PRZEZ FALLING STONE (Level 1)
    for stone in falling_stones:
        if death_hit.colliderect(stone.rect) and stone.is_falling and stone.velocity > 0:
            trigger_death()
            return

    hits = pygame.sprite.spritecollide(player, fruits_group, False)
    for f in hits:
        if not f.is_collected: score += f.collect()

    for b in boss_group:
        if b.is_dying: continue
        if player.rect.inflate(-10, -10).colliderect(b.rect.inflate(-10, -10)): trigger_death(); return
        for ih in pygame.sprite.spritecollide(b, iron_heads, False):
            if ih.is_falling and ih.freeze_timer == 0: b.hit(); ih.is_falling, ih.freeze_timer = False, 15

    # --- LOGIKA TRIGGERÓW ---
    for trig in triggers:
        if player.rect.colliderect(trig['rect']):
            t_name = str(trig.get('name', ''))
            t_id = str(trig.get('tid', ''))

            # Aktywacja spadania
            for s in falling_stones:
                if s.activated_by == t_name and t_name != '':
                    s.is_falling = True

            # IronHead (Level 3)
            if t_name == "IronTrigger" or t_id == "trigger1":
                for ih in iron_heads:
                    if not ih.is_triggered:
                        if ih.tid == t_id or ih.tid == t_name or ih.tid == "trigger1":
                            ih.is_falling = True
                            ih.is_triggered = True

            # SpikedHead (Level 2)
            if t_name == "SH_Trigger":
                for sh in surprise_traps:
                    if not sh.is_triggered: sh.is_triggered = True

    for ex_obj in exits:
        if player.rect.colliderect(ex_obj['rect']):
            if ex_obj['name'] == "wyjscie_level1":
                pending_level_change = (lewelTwo, "SpawnPlayer2")
            elif ex_obj['name'] == "wyjscie_level2":
                pending_level_change = (lewelThree, "FinalSpawn")
            elif ex_obj['name'] == "wyjscie_level3":
                pending_level_change = (lewelOne, "PlayerSpawn")
            return


# --- START ---
pygame.init()
pygame.mixer.init()
pygame.font.init()
gui_font = pygame.font.SysFont("Arial", 24, bold=True)
try:
    jump_sfx = pygame.mixer.Sound("assets/Sounds/jump.wav")
    death_sfx = pygame.mixer.Sound("assets/Sounds/death.mp3")
    boss_hit_sfx = pygame.mixer.Sound("assets/Sounds/hit.mp3")
    boss_death_sfx = pygame.mixer.Sound("assets/Sounds/monster_death.mp3")
    collect_sfx = pygame.mixer.Sound("assets/Sounds/retro_collect.mp3")
    pygame.mixer.music.load("assets/Sounds/music.mp3")
    pygame.mixer.music.play(-1)
except pygame.error as error_msg:
    print(f"Ostrzeżenie: Nie udało się załadować wszystkich dźwięków ({error_msg})")
    jump_sfx = death_sfx = boss_hit_sfx = boss_death_sfx = collect_sfx = None

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock, player = pygame.time.Clock(), Player((0, 0))
load_level(lewelOne)

while True:
    dt_sec = clock.tick(60) / 1000.0
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: pygame.quit(); exit()
        if ev.type == pygame.KEYDOWN:
            if show_results:
                if ev.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    score = level_start_score = 0
                    show_results = transition_active = player.is_dead = False
                    fallen_tiles.clear()
                    player.velocity = pygame.math.Vector2(0, 0)
                    player.image = player.idle_img
                    load_level(lewelOne)
            elif ev.key in [pygame.K_SPACE, pygame.K_UP]:
                player.handle_jump()

    if boss_active:
        boss_timer -= dt_sec
        if boss_timer <= 0: trigger_death()

    if show_results:
        draw_end_screen()
    elif group:
        moving_platforms.update()
        moving_saws.update()
        falling_stones.update()
        boss_group.update()
        iron_heads.update()
        fruits_group.update()
        surprise_traps.update()
        group.update()
        check_collisions()
        group.center(player.rect.center)
        group.draw(screen)

        if transition_active:
            for _ in range(5):
                if tiles_to_remove:
                    fallen_tiles.append(tiles_to_remove.pop())
                else:
                    transition_active, show_results = False, True

        for pt in fallen_tiles: screen.blit(black_tile_surf, pt)
        if not transition_active: draw_ui()

    if isinstance(pending_level_change, tuple):
        level_start_score = score
        load_level(pending_level_change[0], spawn_name=pending_level_change[1])
        pending_level_change = None

    pygame.display.flip()