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


class gameColorGuardian():
    __name__ = "gameColorGuardian"


    GAME_STANDBY = 0
    GAME_RUNNING = 1
    GAME_OVER = 2
    GAME_SUCCESS = 3


    target_colors = [
        CRGB(1.0, 0.0, 0.0),
        CRGB(0.0, 1.0, 0.0),
        CRGB(0.0, 0.0, 1.0),
    ]

    def __init__(self, *,):
        print("\n"*2)
        print(40 * "*")
        print("1D Game Color Guardian")
        print(40 * "*")

        # config
        self.brightness = 0.8
        self.pixel_count = 144

        self.bullet_speed = 0.008
        self.target_speed_default = 0.2
        self.targets_count_default = 5
        self.success_duration = 5.0
        
        # internal variables
        self.state = self.GAME_STANDBY
        self.success_start = 0
        self.hue = 0.0

        self.bullet_color = CRGB(0,0,0)
        self.bullet_position = 0
        self.bullet_last_update = 0

        self.targets = []
        self.target_position = 0
        self.target_last_update = 0
        self.target_speed = self.target_speed_default
        self.targets_count = self.targets_count_default

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
            # print("red")
            self.bullet_set(CRGB(1.0,0,0))
        if not self.btnGREEN.value:
            # print("green")
            self.bullet_set(CRGB(0,1.0,0))
        if not self.btnBLUE.value:
            # print("blue")
            self.bullet_set(CRGB(0,0,1.0))
        if not self.btnWHITE.value:
            self.game_start()
            time.sleep(0.1)


    def standby_draw(self):
        for i in range(self.pixel_count):
            pixel_pos = helper.map_to_01(i, 0, self.pixel_count)
            color = CHSV(self.hue + pixel_pos)
            # handle gamma and global brightness
            color_rgb = fancy.gamma_adjust(color, brightness=0.01)
            self.pixels[i] = color_rgb.pack()
    
    def rainbow_draw(self):
        for i in range(self.pixel_count):
            pixel_pos = helper.map_to_01(i, 0, self.pixel_count)
            color = CHSV(self.hue + pixel_pos)
            # handle gamma and global brightness
            color_rgb = fancy.gamma_adjust(color, brightness=self.brightness)
            self.pixels[i] = color_rgb.pack()
   
    def rainbow_update(self):
        if self.hue > 1.0:
            self.hue = 0.0
        else:
            self.hue += 0.005

    def bullet_set(self, color):
        self.pixels[self.bullet_position - 1 ] = CRGB(0,0,0).pack()
        self.pixels[self.bullet_position] = CRGB(0,0,0).pack()
        self.bullet_color = color
        self.bullet_position = 0

    def bullet_draw(self):
        self.pixels[self.bullet_position - 1] = CRGB(0,0,0).pack()
        self.pixels[self.bullet_position] = self.bullet_color.pack()

    def bullet_update(self):
        if (time.monotonic() - self.bullet_last_update) > self.bullet_speed:
            self.bullet_last_update = time.monotonic()
            self.bullet_position += 1
            if self.bullet_position >= self.pixel_count:
                self.bullet_color = CRGB(0,0,0)
                self.bullet_position = 0

    def target_draw(self):
        targets_count = len(self.targets)
        for i in range(targets_count):
            self.pixels[self.target_position + i] = self.targets[i].pack()
        last_pixel_position = self.target_position + targets_count
        if (last_pixel_position) < self.pixel_count-1:
            self.pixels[last_pixel_position] = CRGB(0,0,0).pack()
    
    def target_update(self):
        if (time.monotonic() - self.target_last_update) > self.target_speed:
            self.target_last_update = time.monotonic()
            self.target_position -= 1
            # print(f"pixel_count {self.pixel_count}  len(targets) {len(self.targets)}  target_position  {self.target_position}  last_pixel_position {self.target_position + len(self.targets)}")

    def game_rest(self):
        self.targets = []
        for i in range(self.targets_count):
            self.targets.append(
                self.target_colors[
                    random.randrange(0, len(self.target_colors))
                ]
            )
        
        self.bullet_color = CRGB(0)
        self.bullet_position = 0

        self.target_position = self.pixel_count - len(self.targets)
        # print(f"target_position: '{self.target_position}'")
        self.pixels.fill(0)
  
    def game_start(self):
        print("start!")
        self.targets_count = self.targets_count_default
        self.target_speed = self.target_speed_default
        self.game_rest()
        self.state = self.GAME_RUNNING
   
    def game_start_next_level(self):
        print("start next level...")
        self.targets_count += 2
        self.target_speed -= 0.05
        self.game_rest()
        self.state = self.GAME_RUNNING

    def game_over(self):
        print("Game Over")
        self.pixels.fill(0)
        self.state = self.GAME_STANDBY
    
    def game_success(self):
        print("Yeah!")
        self.success_start = time.monotonic()
        self.state = self.GAME_SUCCESS
    
    def game_success_update(self):
        if (time.monotonic() - self.success_start) > self.success_duration:
            self.game_start_next_level()


    def game_draw(self):
        self.bullet_draw()
        self.target_draw()
        self.pixels.show()

    def game_next_step(self):
        self.bullet_update()
        self.target_update()
        
        if self.target_position < 1:
            self.game_over()

        if self.target_position == self.bullet_position:
            # print(f"hit! target: {self.targets[0]}; ")
            # print(f"target", self.targets[0])
            # print(f"bullet_color", self.bullet_color)
            if self.targets[0].pack() == self.bullet_color.pack():
                print(f"hit!")
                self.targets.pop(0)
                self.bullet_color = CRGB(0)
                self.bullet_position = 0
                # print(f"self.targets",self.targets)
                if len(self.targets) <= 0:
                    self.game_success()

    def game_update(self):
        if self.state == self.GAME_STANDBY:
            self.standby_draw()
        elif self.state == self.GAME_RUNNING:
            self.game_draw()
            self.game_next_step()
        elif self.state == self.GAME_OVER:
            self.game_over()
        elif self.state == self.GAME_SUCCESS:
            self.rainbow_draw()
            self.rainbow_update()
            self.game_success_update()
        self.pixels.show()

    def main_loop(self):
        self.button_update()
        self.game_update()
        


game_rgb_guardian = gameColorGuardian()

while True:
    game_rgb_guardian.main_loop()
