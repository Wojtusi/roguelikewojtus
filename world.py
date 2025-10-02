import pygame as pg
import json


class World():
    def __init__(self, data, map_image):
        """
        Initialize the World class

        Args:
            data: Dictionary containing map data (can be from Tiled JSON or custom format)
            map_image: pygame Surface for the map background
        """
        self.waypoints = []
        self.level_data = data
        self.image = map_image

        # Additional world properties
        self.spawn_points = []
        self.treasure_locations = []
        self.enemy_spawn_points = []
        self.width = map_image.get_width() if map_image else 0
        self.height = map_image.get_height() if map_image else 0

        # Process the data immediately when creating the world
        if self.level_data:
            self.process_data()

    def process_data(self):
        """Look through data to extract relevant info"""
        try:
            # Handle both dictionary and list data structures
            if isinstance(self.level_data, dict):
                if "layers" in self.level_data:
                    for layer in self.level_data["layers"]:
                        layer_name = layer.get("name", "")

                        # Process waypoints layer
                        if layer_name == "waypoints":
                            for obj in layer.get("objects", []):
                                if "polyline" in obj:
                                    waypoint_data = obj["polyline"]
                                    self.process_waypoints(waypoint_data)

                        # Process spawn points layer
                        elif layer_name == "spawns":
                            for obj in layer.get("objects", []):
                                x = obj.get("x", 0)
                                y = obj.get("y", 0)
                                self.spawn_points.append((x, y))

                        # Process enemy spawns
                        elif layer_name == "enemies":
                            for obj in layer.get("objects", []):
                                x = obj.get("x", 0)
                                y = obj.get("y", 0)
                                self.enemy_spawn_points.append((x, y))

                # Handle custom format with direct waypoints
                elif "waypoints" in self.level_data:
                    self.waypoints = self.level_data["waypoints"]

                # Handle spawn points in custom format
                if "spawn_points" in self.level_data:
                    self.spawn_points = self.level_data["spawn_points"]

                if "enemy_spawns" in self.level_data:
                    self.enemy_spawn_points = self.level_data["enemy_spawns"]

            else:
                print("Warning: level_data is not a dictionary format")
        except (KeyError, TypeError) as e:
            print(f"Error processing data: {e}")
            print("Using default empty waypoints")

    def process_waypoints(self, data):
        """Iterate through waypoints to extract individual sets of x and y coordinates"""
        try:
            for point in data:
                temp_x = point.get("x", 0)
                temp_y = point.get("y", 0)
                self.waypoints.append((temp_x, temp_y))
        except (AttributeError, TypeError) as e:
            print(f"Error processing waypoints: {e}")

    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw the world with optional camera offset"""
        surface.blit(self.image, (-camera_x, -camera_y))

    def draw_waypoints(self, surface, camera_x=0, camera_y=0, color=(255, 255, 0), radius=5):
        """Draw waypoints for debugging/visualization"""
        for i, waypoint in enumerate(self.waypoints):
            screen_x = int(waypoint[0] - camera_x)
            screen_y = int(waypoint[1] - camera_y)

            # Only draw if waypoint is visible on screen
            if (0 <= screen_x <= surface.get_width() and
                    0 <= screen_y <= surface.get_height()):
                # Draw the waypoint circle
                pg.draw.circle(surface, color, (screen_x, screen_y), radius)

                # Draw a border for better visibility
                pg.draw.circle(surface, (0, 0, 0), (screen_x, screen_y), radius + 1, 1)

                # Optionally draw waypoint number
                font = pg.font.SysFont(None, 20)
                text = font.render(str(i), True, (255, 255, 255))
                text_rect = text.get_rect(center=(screen_x, screen_y - radius - 10))
                surface.blit(text, text_rect)

    def draw_spawn_points(self, surface, camera_x=0, camera_y=0, color=(0, 255, 0), radius=6):
        """Draw spawn points for debugging"""
        for spawn in self.spawn_points:
            screen_x = int(spawn[0] - camera_x)
            screen_y = int(spawn[1] - camera_y)

            if (0 <= screen_x <= surface.get_width() and
                    0 <= screen_y <= surface.get_height()):
                pg.draw.circle(surface, color, (screen_x, screen_y), radius)
                pg.draw.circle(surface, (0, 0, 0), (screen_x, screen_y), radius + 1, 1)

    def draw_enemy_spawns(self, surface, camera_x=0, camera_y=0, color=(255, 0, 0), radius=6):
        """Draw enemy spawn points for debugging"""
        for spawn in self.enemy_spawn_points:
            screen_x = int(spawn[0] - camera_x)
            screen_y = int(spawn[1] - camera_y)

            if (0 <= screen_x <= surface.get_width() and
                    0 <= screen_y <= surface.get_height()):
                pg.draw.circle(surface, color, (screen_x, screen_y), radius)
                pg.draw.circle(surface, (0, 0, 0), (screen_x, screen_y), radius + 1, 1)

    def get_waypoints(self):
        """Return the list of waypoints"""
        return self.waypoints

    def get_spawn_points(self):
        """Return the list of spawn points"""
        return self.spawn_points

    def get_enemy_spawns(self):
        """Return the list of enemy spawn points"""
        return self.enemy_spawn_points

    def add_waypoint(self, x, y):
        """Manually add a waypoint"""
        self.waypoints.append((x, y))

    def add_spawn_point(self, x, y):
        """Manually add a spawn point"""
        self.spawn_points.append((x, y))

    def add_enemy_spawn(self, x, y):
        """Manually add an enemy spawn point"""
        self.enemy_spawn_points.append((x, y))

    def clear_waypoints(self):
        """Clear all waypoints"""
        self.waypoints = []

    def clear_spawn_points(self):
        """Clear all spawn points"""
        self.spawn_points = []

    def clear_enemy_spawns(self):
        """Clear all enemy spawn points"""
        self.enemy_spawn_points = []

    def get_nearest_waypoint(self, pos):
        """
        Find the nearest waypoint to a given position

        Args:
            pos: Tuple (x, y) of the position to check

        Returns:
            Tuple of (waypoint, distance, index) or None if no waypoints
        """
        if not self.waypoints:
            return None

        min_distance = float('inf')
        nearest_waypoint = None
        nearest_index = -1

        for i, waypoint in enumerate(self.waypoints):
            dx = waypoint[0] - pos[0]
            dy = waypoint[1] - pos[1]
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance < min_distance:
                min_distance = distance
                nearest_waypoint = waypoint
                nearest_index = i

        return (nearest_waypoint, min_distance, nearest_index)

    def get_waypoint_path(self, start_index, end_index):
        """
        Get a path of waypoints from start to end index

        Args:
            start_index: Starting waypoint index
            end_index: Ending waypoint index

        Returns:
            List of waypoints forming the path
        """
        if start_index < 0 or end_index >= len(self.waypoints):
            return []

        if start_index <= end_index:
            return self.waypoints[start_index:end_index + 1]
        else:
            # Wrap around if needed
            return self.waypoints[start_index:] + self.waypoints[:end_index + 1]

    def is_position_valid(self, x, y):
        """
        Check if a position is within the world bounds

        Args:
            x, y: Position coordinates

        Returns:
            True if position is valid, False otherwise
        """
        return 0 <= x <= self.width and 0 <= y <= self.height

    def save_to_file(self, filename):
        """
        Save world data to a JSON file

        Args:
            filename: Path to save file
        """
        data = {
            "waypoints": self.waypoints,
            "spawn_points": self.spawn_points,
            "enemy_spawns": self.enemy_spawn_points,
            "width": self.width,
            "height": self.height
        }

        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"World data saved to {filename}")
        except Exception as e:
            print(f"Error saving world data: {e}")

    @staticmethod
    def load_from_file(filename, map_image):
        """
        Load world data from a JSON file

        Args:
            filename: Path to load file
            map_image: pygame Surface for the map

        Returns:
            World instance
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            print(f"World data loaded from {filename}")
            return World(data, map_image)
        except Exception as e:
            print(f"Error loading world data: {e}")
            return World({}, map_image)


# Test and example usage
def create_test_world():
    """Create a test world with sample data"""

    # Sample JSON-like data structure that might come from Tiled or similar map editor
    sample_data = {
        "layers": [
            {
                "name": "waypoints",
                "objects": [
                    {
                        "polyline": [
                            {"x": 100, "y": 150},
                            {"x": 200, "y": 250},
                            {"x": 300, "y": 100},
                            {"x": 400, "y": 200}
                        ]
                    },
                    {
                        "polyline": [
                            {"x": 500, "y": 300},
                            {"x": 600, "y": 400}
                        ]
                    }
                ]
            },
            {
                "name": "spawns",
                "objects": [
                    {"x": 50, "y": 50},
                    {"x": 750, "y": 550}
                ]
            },
            {
                "name": "enemies",
                "objects": [
                    {"x": 200, "y": 200},
                    {"x": 400, "y": 400},
                    {"x": 600, "y": 200}
                ]
            }
        ]
    }

    # Create a simple test image
    test_image = pg.Surface((800, 600))
    test_image.fill((50, 150, 50))  # Green background

    # Create and return the world
    world = World(sample_data, test_image)
    return world


# Main test program
if __name__ == "__main__":
    pg.init()
    screen = pg.display.set_mode((800, 600))
    pg.display.set_caption("World Class Test")
    clock = pg.time.Clock()

    # Create test world
    world = create_test_world()

    print(f"\nLoaded {len(world.get_waypoints())} waypoints:")
    for i, waypoint in enumerate(world.get_waypoints()):
        print(f"  Waypoint {i}: {waypoint}")

    print(f"\nLoaded {len(world.get_spawn_points())} spawn points:")
    for i, spawn in enumerate(world.get_spawn_points()):
        print(f"  Spawn {i}: {spawn}")

    print(f"\nLoaded {len(world.get_enemy_spawns())} enemy spawns:")
    for i, spawn in enumerate(world.get_enemy_spawns()):
        print(f"  Enemy spawn {i}: {spawn}")

    # Test nearest waypoint
    test_pos = (250, 250)
    nearest = world.get_nearest_waypoint(test_pos)
    if nearest:
        print(f"\nNearest waypoint to {test_pos}:")
        print(f"  Waypoint: {nearest[0]}, Distance: {nearest[1]:.2f}, Index: {nearest[2]}")

    # Simple test loop
    running = True
    camera_x, camera_y = 0, 0
    show_waypoints = True
    show_spawns = True
    show_enemies = True

    font = pg.font.SysFont(None, 24)

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    show_waypoints = not show_waypoints
                elif event.key == pg.K_s:
                    show_spawns = not show_spawns
                elif event.key == pg.K_e:
                    show_enemies = not show_enemies
                elif event.key == pg.K_ESCAPE:
                    running = False

        # Move camera with arrow keys
        keys = pg.key.get_pressed()
        camera_speed = 5
        if keys[pg.K_LEFT]:
            camera_x -= camera_speed
        if keys[pg.K_RIGHT]:
            camera_x += camera_speed
        if keys[pg.K_UP]:
            camera_y -= camera_speed
        if keys[pg.K_DOWN]:
            camera_y += camera_speed

        # Draw everything
        screen.fill((0, 0, 0))
        world.draw(screen, camera_x, camera_y)

        if show_waypoints:
            world.draw_waypoints(screen, camera_x, camera_y, (255, 215, 0), 8)

        if show_spawns:
            world.draw_spawn_points(screen, camera_x, camera_y, (0, 255, 0), 8)

        if show_enemies:
            world.draw_enemy_spawns(screen, camera_x, camera_y, (255, 0, 0), 8)

        # Draw instructions
        instructions = [
            "Arrow Keys: Move camera",
            "W: Toggle waypoints",
            "S: Toggle spawn points",
            "E: Toggle enemy spawns",
            "ESC: Quit"
        ]

        y_offset = 10
        for instruction in instructions:
            text = font.render(instruction, True, (255, 255, 255))
            text_bg = pg.Surface((text.get_width() + 10, text.get_height() + 4))
            text_bg.fill((0, 0, 0))
            text_bg.set_alpha(180)
            screen.blit(text_bg, (5, y_offset - 2))
            screen.blit(text, (10, y_offset))
            y_offset += 25

        pg.display.flip()
        clock.tick(60)

    pg.quit()
