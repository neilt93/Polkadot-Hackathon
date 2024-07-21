import sys
import pygame
from pygame.locals import *
from text_input import TextInputBox  # Import the TextInputBox class
from mint import mint_nft  # Import the mint_nft function
import time
import web3

pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional

HEIGHT = 900
WIDTH = 1300
ACC = 0.5
FRIC = -0.12
GRAVITY = 0.5
FPS = 60

FramePerSec = pygame.time.Clock()

background_images = [
    pygame.image.load("nft-project/DALL·E 2024-07-20 22.53.42 - A pixelated countryside with green fields, trees, and a blue sky, in the style of old 8-bit video games.webp"),
    pygame.image.load("nft-project/Screenshot 2024-07-20 at 10.59.58 PM.png"),
    pygame.image.load("nft-project/DALL·E 2024-07-20 22.56.09 - A pixelated forest scene with dense trees, a small river, and a clear sky, in the style of old 8-bit video games.webp")
]

background_images = [pygame.transform.scale(img, (WIDTH, HEIGHT)) for img in background_images]


displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GreenCube")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((30, 30))
        self.surf.fill((128, 255, 40))
        self.rect = self.surf.get_rect()

        self.pos = vec((10, 800))  # Start pos x,y from top left
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.jumping = False

    def move(self):
        self.acc = vec(0, GRAVITY)  # Gravity pulls down

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_a]:
            self.acc.x = -ACC
        if pressed_keys[K_d]:
            self.acc.x = ACC

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WIDTH:
            self.pos.x = WIDTH
            self.transition('right')
        if self.pos.x < 0:
            self.pos.x = 0
            self.transition('left')

        self.rect.midbottom = self.pos

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.vel.y = -12  # Adjust the jump strength as needed

    def update(self):
        self.move()
        self.check_collision()

    def check_collision(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            self.jumping = False
            self.pos.y = hits[0].rect.top + 1
            self.vel.y = 0

        # Check for obstacle collisions
        obstacle_hits = pygame.sprite.spritecollide(self, obstacles, False)
        if obstacle_hits:
            self.pos.x -= self.vel.x  # Simple response to collision, adjust as needed
            self.vel.x = 0

    def transition(self, direction):
        global current_screen
        if direction == 'right':
            current_screen = (current_screen + 1) % len(screens)
            self.pos.x = 10
        elif direction == 'left':
            current_screen = (current_screen - 1) % len(screens)
            self.pos.x = WIDTH - 10
        self.pos.y = 385
        load_screen(current_screen)


class InteractableSprite(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y, color, dialogue, special=False):
        super().__init__()
        self.surf = pygame.Surface((width, height))
        self.surf.fill(color)
        self.rect = self.surf.get_rect(topleft=(x, y))
        self.dialogue = dialogue
        self.special = special

    def interact(self, dialogue_box, recipient_address):
        if self.special and recipient_address and recipient_address.startswith("0x") and len(recipient_address) == 42:
            try:
                tx_receipt = mint_nft(recipient_address, "null")
                # Add a small delay to ensure transaction confirmation
                time.sleep(5)
                nft_address = tx_receipt['to']
                dialogue_box.show(f"You win!!! Your NFT reward is at address {nft_address}. To claim it, add it to your MetaMask wallet. Click this box to copy this textbox!")
            except Exception as e:
                print(f"Error minting NFT: {e}")
                dialogue_box.show("An error occurred while minting the NFT. Please retry and enter your wallet address.")
        else:
            dialogue_box.show(self.dialogue)
import pyperclip

class DialogueBox:
    def __init__(self, width, height, x, y):
        self.surf = pygame.Surface((width, height))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(topleft=(x, y))
        self.font = pygame.font.Font(None, 28)  # Adjust font size
        self.text = ""
        self.active = False

    def show(self, text):
        self.text = text
        self.active = True
        pyperclip.copy(text)  # Copy text to clipboard

    def hide(self):
        self.active = False

    def draw(self, surface):
        if self.active:
            surface.blit(self.surf, self.rect)
            self.render_text(surface)

    def render_text(self, surface):
        words = self.text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            test_surface = self.font.render(test_line, True, (0, 0, 0))
            if test_surface.get_width() < self.rect.width - 20:  # Adjust for padding
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)

        y_offset = self.rect.y + 10
        for line in lines:
            rendered_text = self.font.render(line, True, (0, 0, 0))
            surface.blit(rendered_text, (self.rect.x + 10, y_offset))
            y_offset += rendered_text.get_height()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y, color=(255, 255, 0)):
        super().__init__()
        self.surf = pygame.Surface((width, height))
        self.surf.fill(color)
        self.rect = self.surf.get_rect(topleft=(x, y))


obstacles = pygame.sprite.Group()

class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y, color=(255, 0, 0)):
        super().__init__()
        self.surf = pygame.Surface((width, height))
        self.surf.fill(color)
        self.rect = self.surf.get_rect(topleft=(x, y))


def load_screen(screen_index):
    global platforms, interactables, obstacles
    platforms.empty()
    interactables.empty()
    obstacles.empty()
    for plat in screens[screen_index]['platforms']:
        platforms.add(plat)
    for interactable in screens[screen_index]['interactables']:
        interactables.add(interactable)
    for obstacle in screens[screen_index]['obstacles']:
        obstacles.add(obstacle)
    all_sprites.empty()
    all_sprites.add(platforms)
    all_sprites.add(interactables)
    all_sprites.add(obstacles)
    all_sprites.add(P1)


# Multiple screens
base = Platform(WIDTH, 20, 0, HEIGHT - 10, color=(100, 100, 100))
screens = [
    {
        'platforms': [base, Platform(100, 20, 250, 800, color=(0, 0, 0)), Platform(100, 20, 450, 700, color=(0, 0, 0)), 
                      Platform(100, 20, 650, 580, color=(0, 0, 0))],
        'interactables': [],
        'obstacles': [Obstacle(200, 200, 600, 700)] 
    },
    {
        'platforms': [base, Platform(100, 20, 350, 800, color=(0, 0, 0)), Platform(100, 20, 450, 700, color=(0, 0, 0)),
                      Platform(100, 20, 300, 600, color=(0, 0, 0)), Platform(100, 20, 450, 500, color=(0, 0, 0)),
                      Platform(100, 20, 600, 400, color=(0, 0, 120)), Platform(100, 20, 800, 280, color=(0, 0, 120)),
                      Platform(100, 20, 1000, 280, color=(0, 0, 120))],
        'interactables': [],
        'obstacles': [Obstacle(400, 800, 800, 300)]
    },
    {
        'platforms': [base, Platform(200, 400, 575, 800, color=(255, 223, 0))],
        'interactables': [InteractableSprite(30, 30, 650, 770, (0, 255, 0), "HI!!!", special=True)],
        'obstacles': []
    }
]


# Create instances of the Player and Platform
P1 = Player()
dialogue_box = DialogueBox(800, 200, WIDTH // 2 - 400, HEIGHT - 250)


# Create groups for sprites
platforms = pygame.sprite.Group()
interactables = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

# Start with the first screen
current_screen = 0
load_screen(current_screen)

input_box = TextInputBox(100, 100, 12000, 32)  # Adjust the x and y coordinates as needed

# Create the font and label
label_font = pygame.font.Font(None, 28)
label_text = "Enter wallet address here:"
label_surface = label_font.render(label_text, True, (0, 0, 0))

# Main game loop
while True:
    events = pygame.event.get()  # Get all events
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                P1.jump()
            if event.key == K_e:  # Press 'E' to interact
                if input_box.is_valid_address():
                    hits = pygame.sprite.spritecollide(P1, interactables, False)
                    if hits:
                        hits[0].interact(dialogue_box, input_box.get_text())
                else:
                    print("Invalid address entered")
        input_box.handle_event(event)

    # Update player movement and check for collisions
    P1.update()
    input_box.update()

    # Fill the screen with the current background image
    displaysurface.blit(background_images[current_screen], (0, 0))  # Draw the current background image

    # Draw all sprites
    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)

    # Draw the label
    displaysurface.blit(label_surface, (100, 70))  # Adjust the x and y coordinates as needed

    # Draw the text input box
    input_box.draw(displaysurface)

    # Draw the dialogue box
    dialogue_box.draw(displaysurface)

    # Update the display
    pygame.display.update()
    FramePerSec.tick(FPS)

