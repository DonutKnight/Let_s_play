import pygame
import pytmx
import pyscroll
from typing import Optional, Any
import lewelOne
import lewelTwo


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
current_level_module = lewelOne
last_used_spawn = "PlayerSpawn"


class MovingSaw(pygame.sprite.Sprite):
    def __init__(self, obj):
        super().__init__()

        try:
            sprite_sheet = pygame.image.load("assets/Traps/Saw/On (38x38).png").convert_alpha()
            self.frames = []
            for i in range(8):
                frame = pygame.Surface.subsurface(sprite_sheet, (i * 38, 0, 38, 38))
                self.frames.append(frame)
        except Exception as e:
            print(f"BŁĄD: Nie znaleziono pliku piły! {e}")
            self.frames = [pygame.Surface((38, 38))]
            self.frames[0].fill((255, 0, 0))

        self.image = self.frames[0]
        # Ustawiamy ŚRODEK piły na pozycji obiektu z Tiled (używamy szerokości obiektu jako kotwicy)
        self.rect = self.image.get_rect(center=(obj.x + obj.width // 2, obj.y + obj.height // 2))

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.start_pos = pygame.math.Vector2(self.rect.topleft)

        self.axis = obj.properties.get('axis', 'y')
        self.dist = float(obj.properties.get('dist', 100))
        self.speed = float(obj.properties.get('speed', 2.0))
        self.anim_speed = float(obj.properties.get('anim_speed', 0.2))

        self.direction = 1
        self.frame_index = 0.0

    def update(self, *args, **kwargs):
        # Animacja kręcenia się
        self.frame_index += self.anim_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

        # Ruch wahadłowy (Góra/Dół lub Lewo/Prawo)
        if self.axis == 'y':
            self.pos.y += self.speed * self.direction
            if abs(self.pos.y - self.start_pos.y) >= abs(self.dist):
                self.direction *= -1
        else:
            self.pos.x += self.speed * self.direction
            if abs(self.pos.x - self.start_pos.x) >= abs(self.dist):
                self.direction *= -1

        self.rect.topleft = (round(self.pos.x), round(self.pos.y))


class FallingStone(pygame.sprite.Sprite):
    def __init__(self, obj):
        super().__init__()
        self.image = obj.image if obj.image else pygame.Surface((obj.width, obj.height))
        if not obj.image: self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(obj.x, obj.y))
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.name = obj.name
        self.activated_by = obj.properties.get('activated_by', '')
        self.instant_death = obj.properties.get('instant_death', True)
        self.on_impact = obj.properties.get('on_impact', 'stop')
        self.velocity, self.gravity, self.is_falling = 0.0, 0.5, False

    def update(self, *args, **kwargs):
        if self.is_falling:
            self.velocity += self.gravity
            self.pos.y += self.velocity
            self.rect.y = round(self.pos.y)
            for p in platforms:
                if self.rect.colliderect(p):
                    if self.on_impact == "destroy":
                        self.kill()
                    else:
                        self.rect.bottom = p.top
                        self.is_falling, self.velocity = False, 0.0
                        self.pos.y = float(self.rect.y)


class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, obj):
        super().__init__()
        self.image = pygame.Surface((obj.width, obj.height), pygame.SRCALPHA)
        if obj.image:
            tw = obj.image.get_width()
            for x in range(0, int(obj.width), tw): self.image.blit(obj.image, (x, 0))
        else:
            self.image.fill((150, 75, 0))
        self.rect = self.image.get_rect(topleft=(obj.x, obj.y))
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.start_pos = pygame.math.Vector2(obj.x, obj.y)
        self.axis, self.dist, self.speed = obj.properties.get('axis', 'x'), obj.properties.get('dist',
                                                                                               100), obj.properties.get(
            'speed', 1.0)
        self.direction, self.vel = 1, pygame.math.Vector2(0, 0)

    def update(self, *args, **kwargs):
        old_x, old_y = self.rect.x, self.rect.y
        if self.axis == 'x':
            self.pos.x += self.speed * self.direction
            if abs(self.pos.x - self.start_pos.x) >= abs(self.dist): self.direction *= -1
        else:
            self.pos.y += self.speed * self.direction
            if abs(self.pos.y - self.start_pos.y) >= abs(self.dist): self.direction *= -1
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.vel.x, self.vel.y = self.rect.x - old_x, self.rect.y - old_y


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        sheet = pygame.image.load("assets/Main Characters/Ninja Frog/Idle (32x32).png").convert_alpha()
        self.idle_img = pygame.Surface.subsurface(sheet, (0, 0, 32, 32))
        dj_sheet = pygame.image.load("assets/Main Characters/Ninja Frog/Double Jump (32x32).png").convert_alpha()
        self.dj_frames = [pygame.Surface.subsurface(dj_sheet, (i * 32, 0, 32, 32)) for i in range(6)]
        self.image, self.rect = self.idle_img, self.idle_img.get_rect(topleft=pos)
        self.position, self.velocity = pygame.math.Vector2(pos), pygame.math.Vector2(0, 0)
        self.gravity, self.jump_speed = 0.8, -11
        self.on_ground, self.can_double_jump, self.facing_right = False, False, True
        self.is_doing_flip, self.flip_index = False, 0.0
        self.is_dead = False

    def get_input(self):
        if self.is_dead:
            self.velocity.x = 0
            return
        keys = pygame.key.get_pressed()
        self.velocity.x = -4 if keys[pygame.K_LEFT] else 4 if keys[pygame.K_RIGHT] else 0
        if self.velocity.x < 0:
            self.facing_right = False
        elif self.velocity.x > 0:
            self.facing_right = True

    def handle_jump(self):
        if self.is_dead: return
        if self.on_ground:
            self.velocity.y, self.on_ground, self.can_double_jump = self.jump_speed, False, True
            self.is_doing_flip = False
            jump_sfx.stop()
            jump_sfx.play()
        elif self.can_double_jump:
            self.velocity.y, self.can_double_jump, self.is_doing_flip, self.flip_index = self.jump_speed, False, True, 0.0
            jump_sfx.stop()
            jump_sfx.play()

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


def trigger_death():
    player.is_dead = True
    player.velocity = pygame.math.Vector2(0, 0)
    death_sfx.play()
    group.draw(screen)
    pygame.display.flip()
    waiting_time = int(death_sfx.get_length() * 1000)
    pygame.time.delay(waiting_time)
    player.is_dead = False
    load_level(current_level_module, spawn_name=last_used_spawn)


def load_level(level_module: Any, spawn_name: str = "PlayerSpawn"):
    global tmx_data, map_layer, group, platforms, traps, exits, triggers, current_level_module, last_used_spawn
    current_level_module = level_module
    last_used_spawn = spawn_name
    platforms, traps, exits, triggers = [], [], [], []
    moving_platforms.empty()
    moving_saws.empty()
    falling_stones.empty()

    tmx_data = pytmx.util_pygame.load_pygame(level_module.MAP_PATH)
    map_data = pyscroll.data.TiledMapData(tmx_data)
    map_layer = pyscroll.BufferedRenderer(map_data, (SCREEN_WIDTH, SCREEN_HEIGHT), clamp_camera=True)
    group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=3)

    possible_names = [spawn_name, "SpawnPlayer2", "PlayerSpawn", "start"]
    found_pos = None
    for name in possible_names:
        for obj in tmx_data.objects:
            obj_cl = str(getattr(obj, 'class_', getattr(obj, 'type', "")))
            if str(obj.name) == name or obj_cl == name:
                found_pos = (obj.x, obj.y)
                last_used_spawn = name
                break
        if found_pos: break

    if not found_pos: found_pos = (100, 100)
    player.position = pygame.math.Vector2(found_pos)
    player.rect.topleft = (int(found_pos[0]), int(found_pos[1]))
    player.velocity = pygame.math.Vector2(0, 0)

    for layer in tmx_data.visible_layers:
        raw_class = getattr(layer, 'class_', getattr(layer, 'type', ""))
        l_class = str(raw_class).lower() if raw_class else ""
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if not gid: continue
                r = pygame.Rect(x * 16, y * 16, 16, 16)
                if layer.name in level_module.TRAP_LAYERS or l_class == "spikes":
                    traps.append(r)
                elif layer.name in level_module.GROUND_LAYERS or l_class == "safe":
                    platforms.append(r)
        elif isinstance(layer, pytmx.TiledObjectGroup):
            for obj in layer:
                obj_tp = str(getattr(obj, 'class_', getattr(obj, 'type', ""))).lower()
                if obj_tp == "exit" or "wyjscie" in str(obj.name).lower():
                    exits.append({'rect': pygame.Rect(obj.x, obj.y, obj.width, obj.height), 'name': str(obj.name)})
                elif obj_tp == "movingplat":
                    p = MovingPlatform(obj)
                    moving_platforms.add(p)
                    group.add(p)
                elif obj_tp == "movingsaw" or obj.name == "saw":
                    s = MovingSaw(obj)
                    moving_saws.add(s)
                    group.add(s)
                elif obj_tp == "fallingstone":
                    s = FallingStone(obj)
                    falling_stones.add(s)
                    group.add(s)
                elif obj_tp == "trigger":
                    triggers.append({'rect': pygame.Rect(obj.x, obj.y, obj.width, obj.height), 'name': obj.name})
                elif obj_tp in ["spikes", "trap"]:
                    traps.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

    group.add(player)
    group.center(player.rect.center)


def check_collisions():
    if tmx_data is None: return
    mw, mh = tmx_data.width * 16, tmx_data.height * 16

    player.position.x += player.velocity.x
    player.rect.x = round(player.position.x)
    if player.rect.left < 0:
        player.rect.left = 0
    elif player.rect.right > mw:
        player.rect.right = mw
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

    if player.rect.top > mh + 50:
        trigger_death()
        return

    for plat in moving_platforms:
        foot = player.rect.copy()
        foot.y += 2
        if foot.colliderect(plat.rect) and player.velocity.y >= 0 and player.rect.bottom <= plat.rect.top + 20:
            player.rect.bottom, player.velocity.y, player.on_ground = plat.rect.top, 0, True
            player.can_double_jump = False
            player.position += plat.vel
            player.rect.x = round(player.position.x)

    for p in platforms:
        if player.rect.colliderect(p):
            if player.velocity.y > 0:
                player.rect.bottom, player.velocity.y, player.on_ground = p.top, 0, True
            else:
                player.rect.top, player.velocity.y = p.bottom, 0
    player.position.y = float(player.rect.y)

    death_hit = player.rect.inflate(-12, -12)
    # Kolizja z piłami
    for s in moving_saws:
        if death_hit.colliderect(s.rect):
            trigger_death()
            return

    # Kolizja z pułapkami statycznymi
    for t in traps:
        if death_hit.colliderect(t):
            trigger_death()
            return

    for trig in triggers:
        if player.rect.colliderect(trig['rect']):
            for s in falling_stones:
                if s.activated_by == trig['name']: s.is_falling = True
    for s in falling_stones:
        if player.rect.colliderect(s.rect) and s.instant_death:
            trigger_death()
            return

    for e in exits:
        if player.rect.colliderect(e['rect']):
            if e['name'] == "wyjscie_level1":
                load_level(lewelTwo, spawn_name="SpawnPlayer2")
            elif e['name'] == "wyjscie_level2":
                load_level(lewelOne, spawn_name="PlayerSpawn")
            return


# --- START ---
pygame.init()
pygame.mixer.init()

jump_sfx = pygame.mixer.Sound("assets/Sounds/jump.wav")
death_sfx = pygame.mixer.Sound("assets/Sounds/death.mp3")
pygame.mixer.music.load("assets/Sounds/music.mp3")
jump_sfx.set_volume(0.3)
death_sfx.set_volume(0.7)
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
player = Player((0, 0))
load_level(lewelOne)

while True:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: pygame.quit(); exit()
        if ev.type == pygame.KEYDOWN and ev.key in [pygame.K_SPACE, pygame.K_UP]: player.handle_jump()

    if group:
        moving_platforms.update()
        moving_saws.update()
        falling_stones.update()
        group.update()
        check_collisions()
        group.center(player.rect.center)
        group.draw(screen)

    pygame.display.flip()
    clock.tick(60)