import pygame

class Game:
    def __init__(self):
        pygame.init()
        self.width, self.height = 700, 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.background = (0, 0, 0)
        pygame.display.set_caption("Clashing Grid")
        pygame.display.set_icon(pygame.image.load("objects/iconBLACK.png"))

        self.running = True
        self.playerTurn = 1
        self.player1_score = 0
        self.player2_score = 0

        # canvas screen
        self.canvas_width, self.canvas_height = 600, 538
        self.canvas_screen = pygame.Rect((self.width - 600) // 2, (self.height - 580), self.canvas_width, self.canvas_height)

        # Grid size
        self.rows, self.cols = 10, 10
        self.cell_width = self.canvas_width // self.cols
        self.cell_height = self.canvas_height // self.rows

        # Colors
        self.player1_color = (0, 120, 255)
        self.player2_color = (255, 50, 50)
        self.canvas_color = (29, 30, 30)

        # font
        self.title_font = pygame.font.Font("fonts/Quinquefive-ALoRM.ttf", 18)
        self.sub_title_font = pygame.font.Font("fonts/GamestationCond.otf", 32)

        # FPS
        self.clock = pygame.time.Clock()

    def draw_grid(self):
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.canvas_screen.x + col * self.cell_width
                y = self.canvas_screen.y + row * self.cell_height

                pygame.draw.rect(self.screen, 0, (x, y, self.cell_width, self.cell_height))
                pygame.draw.rect(self.screen, (75, 75, 75), (x, y, self.cell_width, self.cell_height), 1)

    def player_turn(self):
        pass

    def player_score(self):
        pass

    def draw_header(self):
        title_text = self.title_font.render(f"Player {self.playerTurn}", True, (255, 255, 255))
        title_text_rect = title_text.get_rect(center=(self.width // 2, 50))

        player1_score = self.title_font.render(f"P1:{self.player1_score}", True, (255, 255, 255))
        player1_score_rect = player1_score.get_rect(center=(self.width // 6 - 10, 90))
        player2_score = self.title_font.render(f"P2:{self.player2_score}", True, (255, 255, 255))
        player2_score_rect = player2_score.get_rect(center=(605, 90))

        self.screen.blit(title_text, title_text_rect)
        self.screen.blit(player1_score, player1_score_rect)
        self.screen.blit(player2_score, player2_score_rect)

    def run(self):
        pauseButton = pygame.image.load("objects/pauseButton.png").convert_alpha()
        pauseButton_rect = pauseButton.get_rect(center=(self.width - 30, 30))
        while self.running:
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEMOTION:
                    if pauseButton_rect.collidepoint(event.pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            self.screen.blit(pauseButton, pauseButton_rect)
            self.draw_header() # draws game header
            self.draw_grid() # draws grid
            self.clock.tick(60)
            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()