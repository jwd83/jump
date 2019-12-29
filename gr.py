import pyglet
from pyglet.window import key

from player import *
from polys import *

main_batch = pyglet.graphics.Batch()

FRAME_RATE = 60.0
GRAVITY = 3
RUN_ACCELERATION = 0.25


def constrain(value, min, max):
    if value < min:
        return min
    if value > max:
        return max
    return value


class GameWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        # create our pyglet window
        super().__init__(*args, **kwargs)

        # setup key handling
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)

        # setup debug text
        self.debug_str = ""
        self.label_debug = pyglet.text.Label(
            self.debug_str,
            font_name='Arial',
            font_size=18,
            x=0,
            y=self.height,
            anchor_x='left',
            anchor_y='top',
            batch=main_batch
        )
        self.debug_enable = True

        # setup player
        player_image = pyglet.image.load('res/sprites/r2.png')
        player_image.anchor_x = int(player_image.width / 2)
        self.player = pyglet.sprite.Sprite(player_image, x=300, y=300, batch=main_batch)
        self.player.vx = 0
        self.player.vy = 0
        self.player.state = PStates.IDLE
        self.player.charge_time = 0
        self.player.facing = PFacing.FACING_RIGHT
        self.player.rect = Poly(300, 300)
        self.player.rect.add_point(-10, 0)
        self.player.rect.add_point(-10, 38)
        self.player.rect.add_point(11, 38)
        self.player.rect.add_point(11, 0)

    def on_draw(self):
        frame_batch = pyglet.graphics.Batch()

        if self.player.facing == PFacing.FACING_LEFT:
            self.player.scale_x = -1
        else:
            self.player.scale_x = 1

        self.player.rect.move(self.player.x, self.player.y)

        self.clear()

        # draw the debugging string if requested
        if self.debug_enable:
            self.label_debug.text = self.debug_str
            # self.label_debug.batch = batch

        # prepare batch
        # batch.add(self.player)
        # batch.add(self.label_debug)
        self.player.rect.add_to_batch(frame_batch)

        # render batch
        main_batch.draw()
        frame_batch.draw()

        # clean up the debugging string
        self.debug_str = ""

    def update(self, dt):
        # handle left/right movement
        self.update_player(dt)
        # FPS: {int(pyglet.clock.get_fps())},
        self.debug_str += f"State: {self.player.state}, Facing: {self.player.facing}, Charge: {self.player.charge_time}"
        # if self.player.state == PStates.IDLE or self.player.state == PStates.MOVING_LEFT:
        #
        # if self.keys[key.LEFT]:
        #     self.player.vx -= RUN_ACCELERATION
        #
        # if self.keys[key.RIGHT]:
        #     self.player.vx += RUN_ACCELERATION
        #
        # if not self.keys[key.RIGHT] and not self.keys[key.LEFT]:
        #     self.player.vx = 0
        #
        # # handle jumping
        # if self.player.y == 0 and self.keys[key.SPACE]:
        #     self.player.vy = 20

        # handle gravity
        if self.player.y > 0:
            self.player.vy -= 1

        # handle left and right movement
        if self.player.state == PStates.MOVING_RIGHT:
            self.player.vx = 1
        if self.player.state == PStates.MOVING_LEFT:
            self.player.vx = -1
        if self.player.state == PStates.IDLE or self.player.state == PStates.CHARGING:
            self.player.vx = 0

        self.player.vx = constrain(self.player.vx, -5, 5)
        self.player.vy = constrain(self.player.vy, -20, 200)

        self.move_player()

        if self.player.y < 0:
            self.player.y = 0
            self.player.vy = 0
            self.player.vx = 0
            self.player.state = PStates.IDLE

    def update_player(self, dt):
        # update facing direction

        if self.keys[key.LEFT]:
            self.player.facing = PFacing.FACING_LEFT

        if self.keys[key.RIGHT]:
            self.player.facing = PFacing.FACING_RIGHT

        # if player is in a jump they have no control
        if self.player.state == PStates.JUMPING:
            return

        # if a player is charging a jump they may only continue charging or release the jump
        if self.player.state == PStates.CHARGING:
            if self.keys[key.SPACE]:
                self.player.charge_time += dt
                self.player.charge_time = constrain(self.player.charge_time, 0, 0.9)

            else:
                self.player.state = PStates.JUMPING
                self.player.vy = self.player.charge_time * 25

                if self.keys[key.LEFT]:
                    self.player.vx = -4

                if self.keys[key.RIGHT]:
                    self.player.vx = 4

            return

        # if a player is not jumping or charging they may begin charging
        if self.keys[key.SPACE]:
            self.player.charge_time = 0
            self.player.state = PStates.CHARGING
            return

        # check if left or right motion is requested
        if self.keys[key.LEFT]:
            self.player.state = PStates.MOVING_LEFT
            return

        if self.keys[key.RIGHT]:
            self.player.state = PStates.MOVING_RIGHT
            return

        # default to idle state
        self.player.state = PStates.IDLE

    def move_player(self):
        self.player.x += self.player.vx
        self.player.y += self.player.vy


if __name__ == "__main__":
    window = GameWindow(1280, 720, "GR")
    pyglet.clock.schedule_interval(window.update, 1.0 / FRAME_RATE)
    pyglet.app.run()
