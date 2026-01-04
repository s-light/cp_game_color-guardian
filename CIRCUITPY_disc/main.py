import time
import board
import pwmio
import digitalio
import random
import helper

from rainbowio import colorwheel
import adafruit_fancyled.adafruit_fancyled as fancy
import adafruit_dotstar

from adafruit_fancyled.adafruit_fancyled import CHSV, CRGB


class gameRGBGuardian():
    __name__ = "gameRGBGuardian"

    target_colors = [
        CRGB(1.0, 0.0, 0.0),
        CRGB(0.0, 1.0, 0.0),
        CRGB(0.0, 0.0, 1.0),
    ]

    def __init__(self, *,):
        print("\n"*2)
        print(40 * "*")
        print("1D Game RGB Guardian")
        print(40 * "*")

        self.brightness = 0.5
        self.pixel_count = 144
        self.hue = 0.0
        self.game_running = False

        self.bullet_color = CRGB(0,0,0)
        self.bullet_position = 0

        self.bullet_last_update = 0
        self.bullet_speed = 0.01

        self.target_last_update = 0
        self.target_speed = 0.1

        self.targets = []
        self.target_position = 0


        self.pixel_init()
        self.button_init()
        print("init done.")

        self.game_rest()

    def pixel_init(self):
        # deactivate internal displays...
        # displayio.release_displays()
        self.pixels = adafruit_dotstar.DotStar(
            clock=board.D12,
            data=board.D11,
            n=self.pixel_count,
            brightness=self.brightness,
            auto_write=False,
        )

    def button_init(self):
        # game-buttons
        self.btnRED = digitalio.DigitalInOut(board.D18)
        self.btnRED.direction = digitalio.Direction.INPUT
        self.btnRED.pull = digitalio.Pull.UP
        self.btnGREEN = digitalio.DigitalInOut(board.D17)
        self.btnGREEN.direction = digitalio.Direction.INPUT
        self.btnGREEN.pull = digitalio.Pull.UP
        self.btnBLUE = digitalio.DigitalInOut(board.D16)
        self.btnBLUE.direction = digitalio.Direction.INPUT
        self.btnBLUE.pull = digitalio.Pull.UP
        self.btnWHITE = digitalio.DigitalInOut(board.D15)
        self.btnWHITE.direction = digitalio.Direction.INPUT
        self.btnWHITE.pull = digitalio.Pull.UP

    def button_update(self):
        if not self.btnRED.value:
            print("red")
            self.bullet_set(CRGB(1.0,0,0))
        if not self.btnGREEN.value:
            print("green")
            self.bullet_set(CRGB(0,1.0,0))
        if not self.btnBLUE.value:
            print("blue")
            self.bullet_set(CRGB(0,0,1.0))
        if not self.btnWHITE.value:
            print("white - start!")
            self.game_rest()
            self.game_running = True


    def rainbow_update(self):
        """based on CircuitPython Essentials DotStar example"""

        if self.hue > 1.0:
            self.hue = 0.0
        else:
            self.hue += 0.001

        for i in range(self.pixel_count):
            pixel_pos = helper.map_to_01(i, 0, self.pixel_count)
            color = CHSV(self.hue + pixel_pos)
            # handle gamma and global brightness
            color_rgb = fancy.gamma_adjust(color, brightness=self.brightness)
            self.pixels[i] = color_rgb.pack()

    def bullet_set(self, color):
        self.pixels[self.bullet_position - 1 ] = CRGB(0,0,0).pack()
        self.pixels[self.bullet_position] = CRGB(0,0,0).pack()
        self.bullet_color = color
        self.bullet_position = 0

    def bullet_update(self):
        self.pixels[self.bullet_position - 1] = CRGB(0,0,0).pack()
        self.pixels[self.bullet_position] = self.bullet_color.pack()

    def target_update(self):
        for i in range(len(self.targets)):
            self.pixels[self.target_position + i] = self.targets[i].pack()
        if (self.target_position + len(self.targets)) < self.pixel_count:
            self.pixels[self.target_position + len(self.targets) -1] = CRGB(0,0,0).pack()

    def game_rest(self):
        self.targets = []
        for i in range(10):
            self.targets.append(
                self.target_colors[
                    random.randrange(0, len(self.target_colors))
                ]
            )

        self.target_position = self.pixel_count - len(self.targets)
        self.pixels.fill(0)

    def game_over(self):
        print("Game Over")
        self.pixels.fill(0)
        self.game_running = False


    def game_next_step(self):
        if self.game_running:
            self.bullet_position += 1
            if self.bullet_position >= self.pixel_count:
                self.bullet_color = CRGB(0,0,0)
                self.bullet_position = 0
            
            self.target_position -= 1
            if self.target_position < 1:
                self.game_over()

            if self.target_position == self.bullet_position:
                if self.targets[0] == self.bullet_color:
                    self.targets.pop(0)
                    self.bullet_color = 0
                    self.bullet_position = 0


    def main_loop(self):
        self.button_update()
        # self.rainbow_update()
        self.bullet_update()
        self.target_update()
        self.pixels.show()

        self.game_next_step()
        
        time.sleep(0.05)


game_rgb_guardian = gameRGBGuardian()

while True:
    game_rgb_guardian.main_loop()
