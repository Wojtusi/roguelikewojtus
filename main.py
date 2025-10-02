import pygame as pg
import constants as c
import random
import math
from world import World
from enemy import Enemy

pg.init()

# Screen and other things
screen = pg.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
pg.display.set_caption("RoguelikeWojtusSlodziak - Enhanced Edition")
clock = pg.time.Clock()
font = pg.font.SysFont(None, 24)
big_font = pg.font.SysFont(None, 36)


# Create a procedural background
def create_background(width, height):
    background = pg.Surface((width, height))
    for y in range(height):
        color_intensity = int(30 + (y / height) * 40)
        pg.draw.line(background, (color_intensity, color_intensity + 10, color_intensity + 20), (0, y), (width, y))

    for _ in range(200):
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(2, 8)
        color = (random.randint(40, 80), random.randint(50, 90), random.randint(60, 100))
        pg.draw.circle(background, color, (x, y), radius)

    return background


# Map settings
tile_size = 32
wall_group = pg.sprite.Group()
treasure_group = pg.sprite.Group()
enemy_group = pg.sprite.Group()

# Game stats
player_health = 100
treasures_collected = 0
game_time = 0


# === Classes ===
class Wall(pg.sprite.Sprite):
    def __init__(self, x, y, size, wall_type='W'):
        super().__init__()
        self.image = pg.Surface((size, size))
        self.wall_type = wall_type

        if wall_type == 'W':
            self.image.fill((139, 69, 19))
            for _ in range(5):
                rect_x = random.randint(2, size - 6)
                rect_y = random.randint(2, size - 6)
                pg.draw.rect(self.image, (160, 82, 45), (rect_x, rect_y, 4, 4))
        elif wall_type == 'B':
            self.image.fill((105, 105, 105))
            pg.draw.line(self.image, (169, 169, 169), (0, size // 3), (size, size // 3), 2)
            pg.draw.line(self.image, (169, 169, 169), (0, 2 * size // 3), (size, 2 * size // 3), 2)
        elif wall_type == 'S':
            self.image.fill((128, 128, 128))
            pg.draw.line(self.image, (64, 64, 64), (size // 4, 0), (3 * size // 4, size), 2)
        elif wall_type == 'L':
            self.image.fill((255, 69, 0))
            pg.draw.circle(self.image, (255, 140, 0), (size // 2, size // 2), size // 3)
        elif wall_type == 'I':
            self.image.fill((173, 216, 230))
            pg.draw.polygon(self.image, (255, 255, 255), [(size // 2, 5), (size // 2 - 3, 15), (size // 2 + 3, 15)])

        pg.draw.rect(self.image, (0, 0, 0), self.image.get_rect(), 2)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Treasure(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface((tile_size // 2, tile_size // 2))
        self.image.fill((255, 215, 0))
        pg.draw.circle(self.image, (255, 255, 255), (tile_size // 4, tile_size // 4), 3)
        self.rect = self.image.get_rect()
        self.rect.center = (x + tile_size // 2, y + tile_size // 2)
        self.bob_offset = 0
        self.original_y = self.rect.y

    def update(self):
        self.bob_offset += 0.2
        self.rect.y = self.original_y + math.sin(self.bob_offset) * 3


class Player(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        try:
            self.image = pg.image.load("ziuty/czarodziej.png").convert_alpha()
        except:
            self.image = pg.Surface((tile_size - 4, tile_size - 4))
            self.image.fill((0, 0, 255))
            pg.draw.polygon(self.image, (128, 0, 128),
                            [(tile_size // 2 - 4, 5), (tile_size // 2 - 4, 15), (tile_size // 2 + 4, 10)])
            pg.draw.circle(self.image, (255, 220, 177), (tile_size // 2 - 4, tile_size // 2), 6)
            pg.draw.circle(self.image, (0, 0, 0), (tile_size // 2 - 6, tile_size // 2 - 2), 1)
            pg.draw.circle(self.image, (0, 0, 0), (tile_size // 2 - 2, tile_size // 2 - 2), 1)

        self.rect = self.image.get_rect(center=pos)
        self.speed = 8
        self.invulnerable = False
        self.invuln_timer = 0

    def update(self, keys, wall_group, treasure_group, enemy_group):
        global player_health, treasures_collected

        if self.invulnerable:
            self.invuln_timer -= 1
            if self.invuln_timer <= 0:
                self.invulnerable = False

        old_x = self.rect.x
        old_y = self.rect.y

        dx, dy = 0, 0
        if keys[pg.K_w] or keys[pg.K_UP]:
            dy = -self.speed
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            dy = self.speed
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            dx = -self.speed
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            dx = self.speed

        if dx != 0 and dy != 0:
            dx = int(dx * 0.707)
            dy = int(dy * 0.707)

        self.rect.x += dx
        if pg.sprite.spritecollide(self, wall_group, False):
            self.rect.x = old_x

        self.rect.y += dy
        if pg.sprite.spritecollide(self, wall_group, False):
            self.rect.y = old_y

        collected = pg.sprite.spritecollide(self, treasure_group, True)
        treasures_collected += len(collected)

        if not self.invulnerable:
            enemies_hit = pg.sprite.spritecollide(self, enemy_group, False)
            if enemies_hit:
                player_health -= 10
                self.invulnerable = True
                self.invuln_timer = 60


def create_dungeon_map():
    map_design = [
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "W......................................W",
        "W..T.........BBBBB.....................W",
        "W...........B.....B........E...........W",
        "W..........B.......B...................W",
        "W.........B....T....B..................W",
        "W........BBBBB.BBBBB...................W",
        "W......................................W",
        "WSSSSSS................LLLLLLLLL.......W",
        "W.....S................L.......L.......W",
        "W.....S....E...........L...T...L.......W",
        "W.....S................L.......L.......W",
        "W.....S................LLLLLLLLL.......W",
        "W.....SSSSSSS..........................W",
        "W......................................W",
        "W..........................P...........W",
        "W......................................W",
        "W......................................W",
        "W......................................W",
        "W......................................W",
        "W......................................W",
        "W..T................E..................W",
        "W......................................W",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW"
    ]
    return map_design


def create_enemy_image():
    """Create enemy sprite image"""
    img = pg.Surface((tile_size - 4, tile_size - 4))
    img.fill((255, 0, 255))
    pg.draw.circle(img, (255, 255, 255), (8, 8), 3)
    pg.draw.circle(img, (255, 255, 255), (20, 8), 3)
    pg.draw.circle(img, (0, 0, 0), (8, 8), 2)
    pg.draw.circle(img, (0, 0, 0), (20, 8), 2)
    return img


def find_safe_spawn_position(wall_group, safe_spawn_positions, preferred_pos=None):
    """Find a safe position where player won't collide with walls"""
    if preferred_pos:
        test_rect = pg.Rect(preferred_pos[0] - (tile_size - 4) // 2,
                            preferred_pos[1] - (tile_size - 4) // 2,
                            tile_size - 4, tile_size - 4)

        collision = False
        for wall in wall_group:
            if test_rect.colliderect(wall.rect):
                collision = True
                break

        if not collision:
            return preferred_pos

    for pos in safe_spawn_positions:
        test_rect = pg.Rect(pos[0] - (tile_size - 4) // 2,
                            pos[1] - (tile_size - 4) // 2,
                            tile_size - 4, tile_size - 4)

        collision = False
        for wall in wall_group:
            if test_rect.colliderect(wall.rect):
                collision = True
                break

        if not collision:
            return pos

    return preferred_pos or (400, 400)


def initialize_game():
    """Initialize or reset the game"""
    global player_health, treasures_collected, game_time
    global wall_group, treasure_group, enemy_group
    global player, player_group, world

    player_health = 100
    treasures_collected = 0
    game_time = 0

    wall_group.empty()
    treasure_group.empty()
    enemy_group.empty()

    world_data = create_dungeon_map()
    map_width = len(world_data[0]) * tile_size
    map_height = len(world_data) * tile_size
    map_image = create_background(map_width, map_height)

    # Create World instance
    world = World({}, map_image)

    player_spawn_pos = None
    safe_spawn_positions = []
    enemy_image = create_enemy_image()

    for row_index, row in enumerate(world_data):
        for col_index, tile in enumerate(row):
            x = col_index * tile_size
            y = row_index * tile_size

            if tile in ['W', 'B', 'S', 'L', 'I']:
                wall = Wall(x, y, tile_size, tile)
                wall_group.add(wall)
            elif tile == 'T':
                treasure = Treasure(x, y)
                treasure_group.add(treasure)
                # Add waypoint at treasure location
                world.add_waypoint(x + tile_size // 2, y + tile_size // 2)
            elif tile == 'E':
                pos = (x + tile_size // 2, y + tile_size // 2)
                # Create enemy with chase mode enabled
                enemy = Enemy(pos, enemy_image, wall_group, chase_player=True)
                # Optional: Randomize some enemy stats
                if random.random() < 0.3:  # 30% chance for faster enemy
                    enemy.set_speed(3)
                enemy_group.add(enemy)
            elif tile == 'P':
                player_spawn_pos = (x + tile_size // 2, y + tile_size // 2)
            elif tile == '.':
                safe_spawn_positions.append((x + tile_size // 2, y + tile_size // 2))

    safe_spawn_pos = find_safe_spawn_position(wall_group, safe_spawn_positions, player_spawn_pos)
    player = Player(pos=safe_spawn_pos)
    player_group = pg.sprite.Group(player)

    return player, player_group, world


# Initialize game
player, player_group, world = initialize_game()
camera_x = 0
camera_y = 0

# === Main game loop ===
run = True
show_waypoints = False
chase_mode_enabled = True  # Track if chase mode is globally enabled

while run:
    dt = clock.tick(c.FPS)
    game_time += dt
    keys = pg.key.get_pressed()

    # Update game objects
    player_group.update(keys, wall_group, treasure_group, enemy_group)
    treasure_group.update()

    # Update enemies with player position for chase behavior
    for enemy in enemy_group:
        enemy.update(player.rect.center)

    # Camera follows player smoothly
    target_camera_x = player.rect.centerx - c.SCREEN_WIDTH // 2
    target_camera_y = player.rect.centery - c.SCREEN_HEIGHT // 2

    camera_x += (target_camera_x - camera_x) * 0.1
    camera_y += (target_camera_y - camera_y) * 0.1

    map_width = world.image.get_width()
    map_height = world.image.get_height()
    camera_x = max(0, min(camera_x, map_width - c.SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, map_height - c.SCREEN_HEIGHT))

    # Drawing
    screen.fill((20, 20, 30))

    # Draw world background
    world.draw(screen, camera_x, camera_y)

    # Draw waypoints if enabled (toggle with W key)
    if show_waypoints:
        world.draw_waypoints(screen, camera_x, camera_y, (255, 215, 0), 8)

    # Draw walls
    for wall in wall_group:
        wall_screen_pos = (wall.rect.x - camera_x, wall.rect.y - camera_y)
        if (-tile_size <= wall_screen_pos[0] <= c.SCREEN_WIDTH and
                -tile_size <= wall_screen_pos[1] <= c.SCREEN_HEIGHT):
            screen.blit(wall.image, wall_screen_pos)

    # Draw treasures
    for treasure in treasure_group:
        screen.blit(treasure.image, (treasure.rect.x - camera_x, treasure.rect.y - camera_y))

    # Draw enemies
    for enemy in enemy_group:
        screen.blit(enemy.image, (enemy.rect.x - camera_x, enemy.rect.y - camera_y))

        # Optional: Draw detection radius when in debug mode
        if show_waypoints:  # Reuse F1 debug key
            # Show chase range
            screen_x = int(enemy.rect.centerx - camera_x)
            screen_y = int(enemy.rect.centery - camera_y)
            pg.draw.circle(screen, (255, 0, 0, 50), (screen_x, screen_y), int(enemy.chase_range), 1)

            # Draw line to player if chasing
            if enemy.chase_player:
                distance = enemy.get_distance_to(player.rect.center)
                if distance < enemy.chase_range:
                    player_screen_x = int(player.rect.centerx - camera_x)
                    player_screen_y = int(player.rect.centery - camera_y)
                    pg.draw.line(screen, (255, 100, 100), (screen_x, screen_y),
                                 (player_screen_x, player_screen_y), 2)

    # Draw player
    if not player.invulnerable or (player.invulnerable and player.invuln_timer % 10 < 5):
        screen.blit(player.image, (player.rect.x - camera_x, player.rect.y - camera_y))

    # UI Elements
    health_bar_width = 200
    health_bar_height = 20
    health_ratio = max(0, player_health / 100)
    pg.draw.rect(screen, (255, 0, 0), (10, 10, health_bar_width, health_bar_height))
    pg.draw.rect(screen, (0, 255, 0), (10, 10, health_bar_width * health_ratio, health_bar_height))
    pg.draw.rect(screen, (255, 255, 255), (10, 10, health_bar_width, health_bar_height), 2)

    health_text = font.render(f"Health: {player_health}/100", True, (255, 255, 255))
    screen.blit(health_text, (220, 15))

    treasure_text = font.render(f"Treasures: {treasures_collected}", True, (255, 255, 255))
    screen.blit(treasure_text, (10, 40))

    time_seconds = game_time // 1000
    time_text = font.render(f"Time: {time_seconds}s", True, (255, 255, 255))
    screen.blit(time_text, (10, 65))

    # Game over check
    if player_health <= 0:
        game_over_text = big_font.render("GAME OVER! Press R to restart", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2))
        screen.blit(game_over_text, text_rect)

        if keys[pg.K_r]:
            player, player_group, world = initialize_game()
            camera_x = 0
            camera_y = 0

    # Victory check
    if treasures_collected >= 4:
        victory_text = big_font.render("VICTORY! All treasures collected!", True, (0, 255, 0))
        text_rect = victory_text.get_rect(center=(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2))
        screen.blit(victory_text, text_rect)

    # Event handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                run = False
            elif event.key == pg.K_F1:
                show_waypoints = not show_waypoints
            elif event.key == pg.K_F2:
                # Toggle chase mode for all enemies
                chase_mode_enabled = not chase_mode_enabled
                for enemy in enemy_group:
                    enemy.set_chase_mode(chase_mode_enabled)
                print(f"Chase mode: {'ENABLED' if chase_mode_enabled else 'DISABLED'}")

    pg.display.flip()

pg.quit()