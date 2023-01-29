import pygame as pg
import os

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

# functions to load resources
def load_image(name, colorkey=None, scale=1):
    fullname = os.path.join(data_dir, name)
    image = pg.image.load(fullname)

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.scale(image, size)

    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self):
            pass

    if not pg.mixer or not pg.mixer.get_init():
        return NoneSound()

    fullname = os.path.join(data_dir, name)
    sound = pg.mixer.Sound(fullname)
    return sound

# classes for our game objects
class Fist(pg.sprite.Sprite):
    """moves a clenched fist on the screen, following the mouse"""
    def __init__(self) -> None:
        pg.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("fist.png", -1)
        self.fist_offset = (-235, -80)
        self.punching = False

    def update(self):
        """move the fist based on the mouse position"""
        pos = pg.mouse.get_pos()
        self.rect.topleft = pos
        self.rect.move_ip(self.fist_offset)
        if self.punching:
            self.rect.move_ip(15, 25)

    def punch(self, target):
        """returns true if the fist collides with the target"""
        if not self.punching:
            self.punching = True
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)

    def unpunch(self):
        """called to pull the fist back"""
        self.punching = False

class Chimp(pg.sprite.Sprite):
    """moves a monkey critter across the screen. it can spin the
    monkey when it is punched."""
    def __init__(self) -> None:
        pg.sprite.Sprite.__init__(self) # call Sprite initializer
        self.image, self.rect = load_image("chimp.png", -1, 4)
        screen = pg.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10, 90
        self.move = 18
        self.dizzy = False

    def update(self):
        if self.dizzy:
            self._spin()
        else:
            self._walk()

    def _walk(self):
        """move the monkey across the screen, and turn at the ends"""
        newpos = self.rect.move((self.move, 0))
        # Change moving direction and flip the image if object outside the screen.
        if not self.area.contains(newpos):
            if self.rect.left < self.area.left \
                or self.rect.right > self.area.right:
                self.move = -self.move
                newpos = self.rect.move((self.move, 0))
                self.image = pg.transform.flip(
                    self.image, True, False)
        self.rect = newpos

    def _spin(self):
        """spin the monkey image"""
        center = self.rect.center
        self.dizzy = self.dizzy + 12
        if self.dizzy >= 360:
            self.dizzy = False
            self.image = self.original
        else:
            rotate = pg.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center=center)

    def punched(self):
        """this will cause the monkey to start spinning"""
        if not self.dizzy:
            self.dizzy = True
            self.original = self.image

# Initialize Everything
pg.init()
screen = pg.display.set_mode((1280, 480), pg.SCALED)
pg.display.set_caption("Punching the Chimpanzee")
pg.mouse.set_visible(False)

# Create The Background
background = pg.Surface(screen.get_size())
background = background.convert()
background.fill((170, 238, 187))

# Put Text On The Background, Centered
if pg.font:
    font = pg.font.Font(None, 64)
    text = font.render("Pummel the Chimp!", 
                    True, (10, 10, 10))
    textpos = text.get_rect(
        centerx=background.get_width()/2, y=10)
    background.blit(text, textpos)
# Display The Background
screen.blit(background, (0, 0))
pg.display.update()
# Initialize Game Objects
whiff_sound = load_sound("whiff.wav")
punch_sound = load_sound("punch.wav")
chimp = Chimp()
fist = Fist()
allsprites = pg.sprite.RenderPlain((chimp, fist))
clock = pg.time.Clock()
# Main Loop
going = True
while going:
    # Set maximum frame per second
    clock.tick(60)
    # Handle Input Events
    for event in pg.event.get():
        if event.type == pg.QUIT: # quit
            going = False
        elif event.type == pg.KEYDOWN \
            and event.key == pg.K_ESCAPE: # escape
            going = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if fist.punch(chimp):
                punch_sound.play() # punch
                chimp.punched()
            else:
                whiff_sound.play() # miss
        elif event.type == pg.MOUSEBUTTONUP:
            fist.unpunch()
    allsprites.update()
    # Draw Everything
    screen.blit(background, (0, 0))
    allsprites.draw(screen)
    pg.display.update()
pg.quit()
# Game Over
