import os
import pygame

class Button(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        button1 = pygame.transform.scale(pygame.image.load(os.path.join("sprites", "offButton.png")), (139, 115))
        button2 = pygame.transform.scale(pygame.image.load(os.path.join("sprites", "onButton.png")), (139, 104))
        self.images = [button1, button2]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(750 // 2, 700 // 2 + 130))
        self.advanced = True

    def handle_click(self, pos):
        # Toggle the button image if clicked
        if self.rect.collidepoint(pos):
            self.index = 1 - self.index  # Toggle between 0 and 1
            self.image = self.images[self.index]
            self.advanced = False if self.index == 1 else True
            if self.index == 0:
                self.rect = self.image.get_rect(center=(750 // 2, 700 // 2 + 130))
            else:
                self.rect = self.image.get_rect(center=(750 // 2, 700 // 2 + 136))
