import arcade

# --- Constants
SCREEN_TITLE = "Pedych Game"
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)

        self.tile_map = None
        self.scene = None
        self.player_sprite = None
        self.physics_engine = None
        self.camera_sprites = None
        self.camera_gui = None
        self.score = 0
        self.left_key_down = False
        self.right_key_down = False
        self.game_over = False

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.camera_sprites = arcade.Camera(self.width, self.height)
        self.camera_gui = arcade.Camera(self.width, self.height)

        map_name = ":resources:tiled_maps/map.json"
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        arcade.set_background_color(arcade.color.RED)

        self.score = 0
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png", CHARACTER_SCALING)
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Platforms"]
        )

        self.game_over = False

    def on_draw(self):
        """Render the screen."""
        self.clear()
        self.camera_sprites.use()
        self.scene.draw()

        self.camera_gui.use()
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, start_x=10, start_y=10, color=arcade.csscolor.WHITE, font_size=18)

        if self.game_over:
            self.draw_game_over()

    def draw_game_over(self):
        """Draw the game over screen."""
        arcade.draw_text("Game Over", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                          arcade.csscolor.WHITE, font_size=30, anchor_x="center")
        arcade.draw_text("Press R to Restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                          arcade.csscolor.WHITE, font_size=20, anchor_x="center")

    def update_player_speed(self):
        self.player_sprite.change_x = 0
        if self.left_key_down and not self.right_key_down:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_key_down and not self.left_key_down:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED

        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = True
            self.update_player_speed()

        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = True
            self.update_player_speed()

        elif key == arcade.key.R and self.game_over:
            self.setup()  # Restart the game

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = False
            self.update_player_speed()

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera_sprites.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera_sprites.viewport_height / 2)

        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0

        player_centered = screen_center_x, screen_center_y
        self.camera_sprites.move_to(player_centered)

    def on_update(self, delta_time):
        """Movement and game logic"""
        if not self.game_over:
            self.physics_engine.update()

            # Check for collisions with platforms or boundaries to simulate death
            if self.player_sprite.bottom < 0:
                self.game_over = True

            coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.scene["Coins"])
            for coin in coin_hit_list:
                coin.remove_from_sprite_lists()
                self.score += 1

            self.center_camera_to_player()

    def on_resize(self, width, height):
        """ Resize window """
        self.camera_sprites.resize(int(width), int(height))
        self.camera_gui.resize(int(width), int(height))

def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
