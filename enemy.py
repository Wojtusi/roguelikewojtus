import pygame as pg
import random
import math


class Enemy(pg.sprite.Sprite):
    def __init__(self, pos, image, wall_group=None, chase_player=True):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos

        # Movement properties
        self.speed = 2
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.change_timer = 0
        self.change_direction_interval = 60  # Frames before changing direction

        # Wall collision reference
        self.wall_group = wall_group

        # Chase behavior
        self.chase_player = chase_player
        self.chase_range = 300  # Distance at which enemy detects player
        self.lost_player_timer = 0
        self.last_known_player_pos = None

        # AI behavior
        self.behavior_mode = 'chase' if chase_player else random.choice(['patrol', 'wander', 'guard'])
        self.patrol_points = []
        self.current_patrol_index = 0
        self.guard_position = pos
        self.guard_radius = 100

        # Animation
        self.animation_timer = 0
        self.original_image = self.image.copy()

    def update(self, player_pos=None):
        """Main update method with optional player position"""
        self.move(player_pos)
        self.animate()

    def move(self, player_pos=None):
        """Handle enemy movement based on behavior mode"""
        self.change_timer += 1

        # Priority: Chase player if enabled and player is in range
        if self.chase_player and player_pos:
            distance = self.get_distance_to(player_pos)

            if distance < self.chase_range:
                # Player detected! Chase them
                self.chase_behavior(player_pos)
                self.last_known_player_pos = player_pos
                self.lost_player_timer = 0
            elif self.last_known_player_pos and self.lost_player_timer < 120:
                # Player out of range but recently seen - investigate last position
                self.lost_player_timer += 1
                self.chase_behavior(self.last_known_player_pos)
            else:
                # Player not detected - use fallback behavior
                self.execute_fallback_behavior()
        else:
            # No chase mode or no player position - use standard behavior
            self.execute_fallback_behavior()

        # Apply movement
        old_pos = self.rect.copy()
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

        # Check collision with walls
        if self.wall_group and pg.sprite.spritecollide(self, self.wall_group, False):
            self.rect = old_pos
            # Try to move around obstacle when chasing
            if self.chase_player and player_pos:
                self.navigate_around_obstacle(player_pos)
            else:
                self.change_direction()

    def execute_fallback_behavior(self):
        """Execute non-chase behavior"""
        if self.behavior_mode == 'patrol':
            self.patrol_behavior()
        elif self.behavior_mode == 'wander':
            self.wander_behavior()
        elif self.behavior_mode == 'guard':
            self.guard_behavior()
        elif self.behavior_mode == 'chase':
            # If in chase mode but no target, wander
            self.wander_behavior()

    def chase_behavior(self, target_pos):
        """Chase the player smoothly"""
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            # Calculate normalized direction
            norm_dx = dx / distance
            norm_dy = dy / distance

            # Set direction for movement
            self.direction = (norm_dx * self.speed, norm_dy * self.speed)

    def navigate_around_obstacle(self, target_pos):
        """Try to navigate around walls when chasing"""
        # Try perpendicular directions
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery

        if abs(dx) > abs(dy):
            # Try moving vertically
            self.direction = (0, 1 if dy > 0 else -1)
        else:
            # Try moving horizontally
            self.direction = (1 if dx > 0 else -1, 0)

    def wander_behavior(self):
        """Random wandering movement"""
        if self.change_timer > self.change_direction_interval:
            self.change_direction()
            self.change_timer = 0

    def patrol_behavior(self):
        """Patrol between set points"""
        if not self.patrol_points:
            # If no patrol points, set some up
            x, y = self.rect.center
            self.patrol_points = [
                (x + 100, y),
                (x + 100, y + 100),
                (x, y + 100),
                (x, y)
            ]

        # Move towards current patrol point
        target = self.patrol_points[self.current_patrol_index]
        dx = target[0] - self.rect.centerx
        dy = target[1] - self.rect.centery
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < 10:
            # Reached patrol point, move to next
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        else:
            # Move towards patrol point
            if abs(dx) > abs(dy):
                self.direction = (1 if dx > 0 else -1, 0)
            else:
                self.direction = (0, 1 if dy > 0 else -1)

    def guard_behavior(self):
        """Stay near guard position"""
        dx = self.guard_position[0] - self.rect.centerx
        dy = self.guard_position[1] - self.rect.centery
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > self.guard_radius:
            # Return to guard position
            if abs(dx) > abs(dy):
                self.direction = (1 if dx > 0 else -1, 0)
            else:
                self.direction = (0, 1 if dy > 0 else -1)
        else:
            # Small random movements while guarding
            if self.change_timer > self.change_direction_interval:
                self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)])
                self.change_timer = 0

    def change_direction(self):
        """Randomly change direction"""
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

    def animate(self):
        """Simple animation - slight bobbing effect and color change when chasing"""
        self.animation_timer += 0.1
        offset = int(math.sin(self.animation_timer) * 2)

        # Change color tint when actively chasing
        if hasattr(self, 'chase_player') and self.chase_player and self.last_known_player_pos:
            # Create a red tint overlay when chasing
            self.image = self.original_image.copy()
            red_overlay = pg.Surface(self.image.get_size())
            red_overlay.fill((255, 0, 0))
            red_overlay.set_alpha(50)
            self.image.blit(red_overlay, (0, 0))

    def set_patrol_points(self, points):
        """Set custom patrol points"""
        self.patrol_points = points
        self.behavior_mode = 'patrol'
        self.current_patrol_index = 0

    def set_guard_position(self, position, radius=100):
        """Set guard position and radius"""
        self.guard_position = position
        self.guard_radius = radius
        self.behavior_mode = 'guard'

    def set_behavior(self, behavior):
        """Change behavior mode: 'patrol', 'wander', or 'guard'"""
        if behavior in ['patrol', 'wander', 'guard']:
            self.behavior_mode = behavior

    def set_chase_mode(self, enabled, chase_range=300):
        """
        Enable or disable chase mode

        Args:
            enabled: True to enable chasing, False to disable
            chase_range: Distance at which enemy detects player
        """
        self.chase_player = enabled
        self.chase_range = chase_range
        if enabled:
            self.behavior_mode = 'chase'

    def set_speed(self, speed):
        """Change enemy speed"""
        self.speed = speed

    def chase_target(self, target_pos):
        """Make enemy move towards a target position (like the player) - DEPRECATED"""
        # Kept for backward compatibility
        self.chase_behavior(target_pos)

    def get_distance_to(self, pos):
        """Calculate distance to a position"""
        dx = pos[0] - self.rect.centerx
        dy = pos[1] - self.rect.centery
        return math.sqrt(dx ** 2 + dy ** 2)