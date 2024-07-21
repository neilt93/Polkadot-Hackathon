import pygame
import re
import pygame_textinput
import pyperclip  # Import pyperclip for clipboard operations

class TextInputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('lightskyblue3')
        self.text = text
        self.txt_surface = pygame.font.Font(None, 32).render(text, True, self.color)
        self.active = False
        self.input = pygame_textinput.TextInputVisualizer()
        self.input.value = text

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = pygame.Color('dodgerblue2') if self.active else pygame.Color('lightskyblue3')

        if self.active and event.type == pygame.KEYDOWN:
            # Handle clipboard shortcuts
            if event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                clipboard_text = pyperclip.paste()
                self.input.value += clipboard_text
            elif event.key == pygame.K_c and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                pyperclip.copy(self.input.value)
            elif event.key == pygame.K_x and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                pyperclip.copy(self.input.value)
                self.input.value = ''
            else:
                self.input.update([event])  # Pass event as a list

    def update(self):
        self.txt_surface = pygame.font.Font(None, 32).render(self.input.value, True, self.color)

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_text(self):
        return self.input.value

    def set_text(self, text):
        self.input.value = text
        self.update()

    def is_valid_address(self):
        pattern = re.compile("^0x[a-fA-F0-9]{40}$")
        return bool(pattern.match(self.input.value))
