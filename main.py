import threading
import pygame
import random
import sys
from spriteButton import Button
from network.client import Client
from network.server import Server

class Game:
    def __init__(self):
        pygame.init()
        self.width, self.height = 750, 750
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.background = (0, 0, 0)
        pygame.display.set_caption("Clashing Grid")
        pygame.display.set_icon(pygame.image.load("objects/iconBLACK.png"))

        self.running = True
        self.playerTurn = 1
        self.player1_score = 0
        self.player2_score = 0
        self.inactive_color = (128, 128, 128)
        self.active_color = (255, 255, 255)
        self.input_active_color = (0, 255, 0)
        self.input_not_active_color = (255, 255, 255)

        # game settings
        self.expansion = 1
        self.advance_mode = False

        # indicators
        self.arrow_offset = 50
        self.arrowImg = pygame.transform.scale(pygame.image.load("objects/player1Piece.png").convert_alpha(), (30, 30))
        self.arrowImg2 = pygame.transform.scale(pygame.image.load("objects/player2Piece.png").convert_alpha(), (30, 30))
        self.arrow_size = 10

        # canvas screen
        self.canvas_width, self.canvas_height = 600, 538
        self.canvas_screen = pygame.Rect((self.width - 600) // 2, (self.height - 580), self.canvas_width, self.canvas_height)

        # Grid size
        self.rows = 6
        self.cols = 6
        self.cell_width = self.canvas_width // self.cols
        self.cell_height = self.canvas_height // self.rows
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        # Player Colors
        self.player1_color = pygame.image.load("objects/player1Piece.png").convert_alpha()
        self.player1_width, self.player1_height = self.player1_color.get_width(), self.player1_color.get_height()
        self.player1_color = pygame.transform.scale(self.player1_color, (self.cell_width - 15, self.cell_height - 5))

        self.player2_color = pygame.image.load("objects/player2Piece.png").convert_alpha()
        self.player2_width, self.player2_height = self.player2_color.get_width(), self.player2_color.get_height()
        self.player2_color = pygame.transform.scale(self.player2_color, (self.cell_width - 15, self.cell_height - 5))

        # font
        self.title_font = pygame.font.Font("fonts/Quinquefive-ALoRM.ttf", 18)
        self.title_font2 = pygame.font.Font("fonts/Quinquefive-ALoRM.ttf", 32)
        self.title_font_small = pygame.font.Font("fonts/Quinquefive-ALoRM.ttf", 14)
        self.title_font_medium = pygame.font.Font("fonts/Quinquefive-ALoRM.ttf", 18)
        self.sub_title_font = pygame.font.Font("fonts/GamestationCond.otf", 32)
        self.author_font = pygame.font.Font("fonts/Quinquefive-ALoRM.ttf", 12)

        # delay
        self.delay_active = False
        self.delay_start_time = 0
        self.delay_duration = 2000

        # button sprite
        self.all_sprite = pygame.sprite.Group()
        self.sprite_button = Button(self.all_sprite)

        # FPS
        self.clock = pygame.time.Clock()

        # multiplayer
        self.multiplayer = True
        self.multiplayer_active = False
        self.client = None
        self.server = None
        self.server_ip = None
        self.server_ip_active = True

    def main_menu(self):
        # self.game_settings()
        helpImg = pygame.transform.scale(pygame.image.load("objects/help.png").convert_alpha(), (50, 50))
        helpImg_rect = helpImg.get_rect(center=(self.width - 40, 40))

        title_font = pygame.font.Font("fonts/Quinquefive-ALoRM.ttf", 32)
        title_text = title_font.render("Clashing Grid", True, (255, 255, 255))
        title_text_rect = title_text.get_rect(center=(self.width // 2, 100))

        logo = pygame.transform.scale(pygame.image.load("objects/icon.png").convert_alpha(), (200, 200))
        logo_rect = logo.get_rect(center=(self.width // 2, 300))

        local_text = self.sub_title_font.render("Local", True, (255, 255, 255))
        local_text_rect = local_text.get_rect(center=(self.width // 2, 500))

        multiplayer_text = self.sub_title_font.render("Multiplayer", True, self.active_color if self.multiplayer else self.inactive_color)
        multiplayer_text_rect = multiplayer_text.get_rect(center=(self.width // 2, 560))

        quit_text = self.sub_title_font.render("Quit", True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=(self.width // 2, 620))

        author_text = self.author_font.render("Created by: TeamBa", True, (255, 255, 255))
        author_text_rect = author_text.get_rect(center=(self.width // 2, 720))

        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    if helpImg_rect.collidepoint(event.pos) or local_text_rect.collidepoint(event.pos) or quit_text_rect.collidepoint(event.pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    elif multiplayer_text_rect.collidepoint(event.pos) and self.multiplayer:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if local_text_rect.collidepoint(event.pos):
                        self.game_settings()
                        return
                    elif multiplayer_text_rect.collidepoint(event.pos) and self.multiplayer:
                        self.multiplayer_menu()
                        return
                    elif quit_text_rect.collidepoint(event.pos):
                        sys.exit()
                    elif helpImg_rect.collidepoint(event.pos):
                        self.how_to_play()
                        return

            self.screen.fill(self.background)
            self.screen.blit(helpImg, helpImg_rect)
            self.screen.blit(title_text, title_text_rect)
            self.screen.blit(logo, logo_rect)
            self.screen.blit(local_text, local_text_rect)
            self.screen.blit(multiplayer_text, multiplayer_text_rect)
            self.screen.blit(quit_text, quit_text_rect)
            self.screen.blit(author_text, author_text_rect)

            if local_text_rect.collidepoint(mouse_pos):
                arrow_rect_left = self.arrowImg.get_rect(
                    center=(local_text_rect.left - self.arrow_offset, local_text_rect.centery))
                arrow_rect_right = self.arrowImg2.get_rect(
                    center=(local_text_rect.right + self.arrow_offset, local_text_rect.centery))
                self.screen.blit(self.arrowImg, arrow_rect_left)
                self.screen.blit(self.arrowImg2, arrow_rect_right)

            elif multiplayer_text_rect.collidepoint(mouse_pos) and self.multiplayer:
                arrow_rect_left = self.arrowImg.get_rect(
                    center=(multiplayer_text_rect.left - self.arrow_offset, multiplayer_text_rect.centery))
                arrow_rect_right = self.arrowImg2.get_rect(
                    center=(multiplayer_text_rect.right + self.arrow_offset, multiplayer_text_rect.centery))
                self.screen.blit(self.arrowImg, arrow_rect_left)
                self.screen.blit(self.arrowImg2, arrow_rect_right)

            elif quit_text_rect.collidepoint(mouse_pos):
                arrow_rect_left = self.arrowImg.get_rect(
                    center=(quit_text_rect.left - self.arrow_offset, quit_text_rect.centery))
                arrow_rect_right = self.arrowImg2.get_rect(
                    center=(quit_text_rect.right + self.arrow_offset, quit_text_rect.centery))
                self.screen.blit(self.arrowImg, arrow_rect_left)
                self.screen.blit(self.arrowImg2, arrow_rect_right)

            pygame.display.update()

    def how_to_play(self):
        sub_title = pygame.font.Font("fonts/Quinquefive-ALoRM.ttf", 14)
        title_font = pygame.font.Font("fonts/Quinquefive-ALoRM.ttf", 32)

        play_button = pygame.transform.scale(pygame.image.load("objects/playButtonWhite.png").convert_alpha(), (50, 50))
        play_button_rect = play_button.get_rect(center=(self.width // 2, self.height // 2 + 270))

        title_text = title_font.render("How to Play", True, (255, 255, 255))
        title_text_rect = title_text.get_rect(center=(self.width // 2, 100))

        instruct1 = sub_title.render("POSITION YOUR PIECES CLOSE", True, (255, 255, 255))
        instruct1_rect = instruct1.get_rect(center=(self.width // 2, 220))
        instruct1_2 = sub_title.render("TO YOUR EXISTING PIECES TO GROW", True, (255, 255, 255))
        instruct1_2_rect = instruct1_2.get_rect(center=(self.width // 2, 250))
        instruct1_3 = sub_title.render("AND EARN POINTS", True, (255, 255, 255))
        instruct1_3_rect = instruct1_3.get_rect(center=(self.width // 2, 280))

        instruct2 = sub_title.render("THE GOAL IS TO ENTRAP YOUR OPPONENT", True, (255, 255, 255))
        instruct2_rect = instruct2.get_rect(center=(self.width // 2, 330))
        instruct2_2 = sub_title.render("FROM SCORING OR WIN BY THE HIGHEST", True, (255, 255, 255))
        instruct2_2_rect = instruct2_2.get_rect(center=(self.width // 2, 360))
        instruct2_3 = sub_title.render("PIECE COUNT", True, (255, 255, 255))
        instruct2_3_rect = instruct2_3.get_rect(center=(self.width // 2, 390))

        instruct3 = sub_title.render("ThE game WILL AUTOMATICALLY END", True, (255, 255, 255))
        instruct3_rect = instruct3.get_rect(center=(self.width // 2, 440))
        instruct3_2 = sub_title.render("IF A PLAYER DOESN'T HAVE MOVES", True, (255, 255, 255))
        instruct3_2_rect = instruct3_2.get_rect(center=(self.width // 2, 470))

        instruct4 = sub_title.render("IN ADVANCED MODE PIECES CAN OVERTAKE", True, (255, 255, 255))
        instruct4_rect = instruct4.get_rect(center=(self.width // 2, 520))
        instruct4_2 = sub_title.render("OPPONENT'S PIECES", True, (255, 255, 255))
        instruct4_2_rect = instruct4_2.get_rect(center=(self.width // 2, 550))

        author_text = self.author_font.render("Created by: TeamBa", True, (255, 255, 255))
        author_text_rect = author_text.get_rect(center=(self.width // 2, 720))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    if play_button_rect.collidepoint(event.pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button_rect.collidepoint(event.pos):
                        self.run()
                        return

            self.screen.fill(self.background)
            self.screen.blit(title_text, title_text_rect)
            self.screen.blit(instruct1, instruct1_rect)
            self.screen.blit(instruct1_2, instruct1_2_rect)
            self.screen.blit(instruct1_3, instruct1_3_rect)
            self.screen.blit(instruct2, instruct2_rect)
            self.screen.blit(instruct2_2, instruct2_2_rect)
            self.screen.blit(instruct2_3, instruct2_3_rect)
            self.screen.blit(instruct3, instruct3_rect)
            self.screen.blit(instruct3_2, instruct3_2_rect)
            self.screen.blit(instruct4, instruct4_rect)
            self.screen.blit(instruct4_2, instruct4_2_rect)
            self.screen.blit(author_text, author_text_rect)
            self.screen.blit(play_button, play_button_rect)
            pygame.display.update()

    def game_settings(self):
        back_button = pygame.transform.scale(pygame.image.load("objects/playButtonWhite.png").convert_alpha(), (50, 50))
        back_button_rect = back_button.get_rect(center=(self.width - 40, 40))

        title_text = self.title_font2.render("Game Settings", True, (255, 255, 255))
        title_text_rect = title_text.get_rect(center=(self.width // 2, 100))

        expansion_text = self.title_font_medium.render("Expansion", True, (255, 255, 255))
        expansion_text_rect = expansion_text.get_rect(center=(self.width // 2 - 200, 200))
        ex1 = self.sub_title_font.render("1", True, (255, 255, 255))
        ex1_rect = ex1.get_rect(center=(self.width // 2 - 290, 250))
        ex1_HitRect = pygame.Rect(ex1_rect.x - 10, ex1_rect.y - 5, ex1_rect.width + 20, ex1_rect.height + 10)
        ex2 = self.sub_title_font.render("2", True, (255, 255, 255))
        ex2_rect = ex2.get_rect(center=(self.width // 2 - 200, 250))
        ex2_HitRect = pygame.Rect(ex2_rect.x - 10, ex2_rect.y - 5, ex2_rect.width + 20, ex2_rect.height + 10)
        ex3 = self.sub_title_font.render("3", True, (255, 255, 255))
        ex3_rect = ex3.get_rect(center=(self.width // 2 - 110, 250))
        ex3_HitRect = pygame.Rect(ex3_rect.x - 10, ex3_rect.y - 5, ex3_rect.width + 20, ex3_rect.height + 10)

        grid_size = self.title_font_medium.render("Grid Size", True, (255, 255, 255))
        grid_size_rect = grid_size.get_rect(center=(self.width // 2 + 200, 200))
        g1 = self.sub_title_font.render("6x6", True, (255, 255, 255))
        g1_rect = g1.get_rect(center=(self.width // 2 + 150, 250))
        g1_HitRect = pygame.Rect(g1_rect.x - 10, g1_rect.y - 5, g1_rect.width + 20, g1_rect.height + 10)
        g2 = self.sub_title_font.render("8x8", True, (255, 255, 255))
        g2_rect = g2.get_rect(center=(self.width // 2 + 235, 250))
        g2_HitRect = pygame.Rect(g2_rect.x - 10, g2_rect.y - 5, g2_rect.width + 20, g2_rect.height + 10)
        g3 = self.sub_title_font.render("10x10", True, (255, 255, 255))
        g3_rect = g3.get_rect(center=(self.width // 2 + 150, 300))
        g3_HitRect = pygame.Rect(g3_rect.x - 10, g3_rect.y - 5, g3_rect.width + 20, g3_rect.height + 10)
        g4 = self.sub_title_font.render("15x15", True, (255, 255, 255))
        g4_rect = g4.get_rect(center=(self.width // 2 + 240, 300))
        g4_HitRect = pygame.Rect(g4_rect.x - 10, g4_rect.y - 5, g4_rect.width + 20, g4_rect.height + 10)

        advanced_mode = self.title_font_medium.render("Advanced Mode", True, (255, 255, 255))
        advanced_mode_rect = advanced_mode.get_rect(center=(self.width // 2, 380))
        author_text = self.author_font.render("Created by: TeamBa", True, (255, 255, 255))
        author_text_rect = author_text.get_rect(center=(self.width // 2, 720))

        play_text = self.title_font2.render("Play", True, (255, 255, 255))
        play_text_rect = play_text.get_rect(center=(self.width // 2, 630))


        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    if back_button_rect.collidepoint(event.pos) or ex1_rect.collidepoint(event.pos) or ex2_rect.collidepoint(event.pos) or ex3_rect.collidepoint(event.pos) or g1_rect.collidepoint(event.pos) or g2_rect.collidepoint(event.pos) or g3_rect.collidepoint(event.pos) or g4_rect.collidepoint(event.pos) or play_text_rect.collidepoint(event.pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    elif self.sprite_button.rect.collidepoint(event.pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button_rect.collidepoint(event.pos):
                        if self.server:
                            self.multiplayer_exit_connection()
                        self.run()
                        return
                    elif ex1_rect.collidepoint(event.pos):
                        self.expansion = 1
                    elif ex2_rect.collidepoint(event.pos):
                        self.expansion = 2
                    elif ex3_rect.collidepoint(event.pos):
                        self.expansion = 3
                    elif g1_rect.collidepoint(event.pos):
                        self.rows, self.cols = 6, 6
                        self.update_grid()
                    elif g2_rect.collidepoint(event.pos):
                        self.rows, self.cols = 8, 8
                        self.update_grid()
                    elif g3_rect.collidepoint(event.pos):
                        self.rows, self.cols = 10, 10
                        self.update_grid()
                    elif g4_rect.collidepoint(event.pos):
                        self.rows, self.cols = 15, 15
                        self.update_grid()
                    elif play_text_rect.collidepoint(event.pos):
                        if self.multiplayer_active:
                            self.start_multiplayer("host")
                        pygame.time.delay(2000)
                        return
                    elif self.sprite_button.rect.collidepoint(event.pos):
                        self.advance_mode = self.sprite_button.advanced
                        self.sprite_button.handle_click(event.pos)

            self.screen.fill(self.background)
            self.screen.blit(title_text, title_text_rect)
            self.screen.blit(back_button, back_button_rect)
            self.screen.blit(expansion_text, expansion_text_rect)
            self.screen.blit(ex1, ex1_rect)
            if self.expansion == 1:
                pygame.draw.rect(self.screen, (0, 255, 0), ex1_HitRect, 2)
            elif self.expansion == 2:
                pygame.draw.rect(self.screen, (0, 255, 0), ex2_HitRect, 2)
            elif self.expansion == 3:
                pygame.draw.rect(self.screen, (0, 255, 0), ex3_HitRect, 2)
            if self.rows == 6:
                pygame.draw.rect(self.screen, (0, 255, 0), g1_HitRect, 2)
            elif self.rows == 8:
                pygame.draw.rect(self.screen, (0, 255, 0), g2_HitRect, 2)
            elif self.rows == 10:
                pygame.draw.rect(self.screen, (0, 255, 0), g3_HitRect, 2)
            elif self.rows == 15:
                pygame.draw.rect(self.screen, (0, 255, 0), g4_HitRect, 2)
            self.screen.blit(ex2, ex2_rect)
            self.screen.blit(ex3, ex3_rect)
            self.screen.blit(grid_size, grid_size_rect)
            self.screen.blit(g1, g1_rect)
            self.screen.blit(g2, g2_rect)
            self.screen.blit(g3, g3_rect)
            self.screen.blit(g4, g4_rect)
            self.all_sprite.draw(self.screen)
            self.screen.blit(advanced_mode, advanced_mode_rect)
            self.screen.blit(play_text, play_text_rect)
            self.screen.blit(author_text, author_text_rect)
            pygame.display.update()

    def multiplayer_menu(self):
        title_font = pygame.font.Font("fonts/Quinquefive-ALoRM.ttf", 32)
        title_text = title_font.render("Clashing Grid", True, (255, 255, 255))
        title_text_rect = title_text.get_rect(center=(self.width // 2, 100))

        logo = pygame.transform.scale(pygame.image.load("objects/icon.png").convert_alpha(), (200, 200))
        logo_rect = logo.get_rect(center=(self.width // 2, 300))

        host = self.sub_title_font.render("Host a Game", True, (255, 255, 255))
        host_rect = host.get_rect(center=(self.width // 2, 500))

        join = self.sub_title_font.render("Join a Game", True,
                                                      self.active_color if self.multiplayer else self.inactive_color)
        join_rect = join.get_rect(center=(self.width // 2, 560))

        back_text = self.sub_title_font.render("back", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=(self.width // 2, 620))

        author_text = self.author_font.render("Created by: TeamBa", True, (255, 255, 255))
        author_text_rect = author_text.get_rect(center=(self.width // 2, 720))

        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    if host_rect.collidepoint(
                            event.pos) or back_text_rect.collidepoint(event.pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    elif join_rect.collidepoint(event.pos) and self.multiplayer:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if host_rect.collidepoint(event.pos):
                        self.host_game()
                        return
                    elif join_rect.collidepoint(event.pos) and self.multiplayer:
                        self.join_game()
                        return
                    elif back_text_rect.collidepoint(event.pos):
                        self.run()
                        return

            self.screen.fill(self.background)
            self.screen.blit(title_text, title_text_rect)
            self.screen.blit(logo, logo_rect)
            self.screen.blit(host, host_rect)
            self.screen.blit(join, join_rect)
            self.screen.blit(back_text, back_text_rect)
            self.screen.blit(author_text, author_text_rect)

            if host_rect.collidepoint(mouse_pos):
                arrow_rect_left = self.arrowImg.get_rect(
                    center=(host_rect.left - self.arrow_offset, host_rect.centery))
                arrow_rect_right = self.arrowImg2.get_rect(
                    center=(host_rect.right + self.arrow_offset, host_rect.centery))
                self.screen.blit(self.arrowImg, arrow_rect_left)
                self.screen.blit(self.arrowImg2, arrow_rect_right)

            elif join_rect.collidepoint(mouse_pos) and self.multiplayer:
                arrow_rect_left = self.arrowImg.get_rect(
                    center=(join_rect.left - self.arrow_offset, join_rect.centery))
                arrow_rect_right = self.arrowImg2.get_rect(
                    center=(join_rect.right + self.arrow_offset, join_rect.centery))
                self.screen.blit(self.arrowImg, arrow_rect_left)
                self.screen.blit(self.arrowImg2, arrow_rect_right)

            elif back_text_rect.collidepoint(mouse_pos):
                arrow_rect_left = self.arrowImg.get_rect(
                    center=(back_text_rect.left - self.arrow_offset, back_text_rect.centery))
                arrow_rect_right = self.arrowImg2.get_rect(
                    center=(back_text_rect.right + self.arrow_offset, back_text_rect.centery))
                self.screen.blit(self.arrowImg, arrow_rect_left)
                self.screen.blit(self.arrowImg2, arrow_rect_right)

            pygame.display.update()

    def join_game(self):
        play_button = pygame.transform.scale(pygame.image.load("objects/playButtonWhite.png").convert_alpha(), (50, 50))
        play_button_rect = play_button.get_rect(center=(self.width - 40, 40))

        title_text = self.title_font2.render("CLASHING GRID", True, (255, 255, 255))
        title_text_rect = title_text.get_rect(center=(self.width // 2, 100))
        iconImg = pygame.transform.scale(pygame.image.load("objects/icon.png").convert_alpha(), (200, 200))
        iconImg_rect = iconImg.get_rect(center=(self.width // 2, 300))
        enter_code = self.sub_title_font.render("Enter Game Code", True, (255, 255, 255))
        enter_code_rect = enter_code.get_rect(center=(self.width // 2, 470))

        input_text_box = pygame.Rect(self.width // 2 - 200, 500, 400, 50)

        submit_text = self.title_font.render("Join Game", True, (255, 255, 255))
        submit_text_rect = submit_text.get_rect(center=(self.width // 2, 620))

        author_text = self.author_font.render("Created by: TeamBa", True, (255, 255, 255))
        author_text_rect = author_text.get_rect(center=(self.width // 2, 720))

        active = False
        txt = ""
        color = self.input_not_active_color

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    if submit_text_rect.collidepoint(event.pos) or input_text_box.collidepoint(event.pos) or play_button_rect.collidepoint(event.pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_text_box.collidepoint(event.pos):
                        active = True
                    elif submit_text_rect.collidepoint(event.pos):
                        self.server_ip = txt.upper()
                        self.multiplayer_active = True
                        self.start_multiplayer("join")
                        return
                    elif play_button_rect.collidepoint(event.pos):
                        self.run()
                        return

                    color = self.input_active_color if active else self.input_not_active_color

                elif event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_BACKSPACE:
                            txt = txt[:-1]
                        else:
                            if len(txt) < 18:
                                txt += event.unicode


            self.screen.fill(self.background)
            self.screen.blit(title_text, title_text_rect)
            self.screen.blit(play_button, play_button_rect)
            txt_surface = self.title_font.render(txt, True, (255, 255, 255))
            self.screen.blit(iconImg, iconImg_rect)
            self.screen.blit(enter_code, enter_code_rect)
            pygame.draw.rect(self.screen, color, input_text_box, 2)
            self.screen.blit(txt_surface, (input_text_box.x + 5, input_text_box.y + 13))
            self.screen.blit(submit_text, submit_text_rect)
            self.screen.blit(author_text, author_text_rect)
            pygame.display.update()

    def draw_grid(self):
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.canvas_screen.x + col * self.cell_width
                y = self.canvas_screen.y + row * self.cell_height

                pygame.draw.rect(self.screen, 0, (x, y, self.cell_width, self.cell_height))
                pygame.draw.rect(self.screen, (75, 75, 75), (x, y, self.cell_width, self.cell_height), 1)

                if self.grid[row][col] == 1:
                    self.screen.blit(self.player1_color, (x + 7, y + 2))
                elif self.grid[row][col] == 2:
                    self.screen.blit(self.player2_color, (x + 7, y + 2))

    def host_game(self):
        try:
            self.multiplayer_active = True
            self.server = Server()
            self.server_ip = self.server.host_ip
            threading.Thread(target=self.server.run_server, daemon=True).start()
            self.game_settings()
            return
        except Exception as e:
            print(f"Failed to start server: {e}")
            sys.exit()

    def start_multiplayer(self, action):
        try:
            self.client = Client(self, action, self.server_ip)
            print("Connected to server")
        except Exception as e:
            print(f"Failed to connect: {e}")
            sys.exit()

    def send_data(self, action, state=None):
        try:
            data = {"action": action, "state": state}
            self.client.send(data)
        except Exception as e:
            print(f"Error sending data: {e}")

    def listen_for_updates(self):
        while True:
            try:
                server_data = self.client.receive()
                if server_data:
                    if "error" in server_data:
                        print(f"Error: {server_data['error']}")
                        self.client.running = False
                        return
                    self.update_state(server_data)
                    print("Updated game state from server.")
            except Exception as e:
                print(f"Error receiving data: {e}")

    def update_state(self, state):
        self.grid = state["grid"]
        self.playerTurn = state["playerTurn"]
        self.rows = state["rows"]
        self.cols = state["cols"]
        self.expansion = state["expansion"]
        self.advance_mode = state["advance_mode"]
        self.update_grid()
        self.player_score()

    def place_initial_cell(self):
        self.player1_score = 0
        self.player2_score = 0
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.playerTurn = 1

        self.grid[random.randint(0, self.rows - 1)][random.randint(0, self.cols // 3)] = 1
        self.grid[random.randint(0, self.rows - 1)][random.randint(2 * self.cols // 3, self.cols - 1)] = 2

    def restart_game(self):
        self.place_initial_cell()
        if self.multiplayer_active:
            self.send_data("update", {"grid": self.grid, "playerTurn": self.playerTurn})

    def update_grid(self):
        self.cell_width = self.canvas_width // self.cols
        self.cell_height = self.canvas_height // self.rows
        if not self.multiplayer_active:
            self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.player1_color = pygame.transform.scale(self.player1_color, (self.cell_width - 15, self.cell_height - 5))
        self.player2_color = pygame.transform.scale(self.player2_color, (self.cell_width - 15, self.cell_height - 5))

    def get_neighbors(self, row, col):
        neighbors = []
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                neighbors.append((nr, nc))
        return neighbors

    def get_opponent(self):
        return 2 if self.playerTurn == 1 else 1

    def get_expansion(self, row, col):
        neighbors = self.get_neighbors(row, col)
        valid_neighbors = [(nr, nc) for nr, nc in neighbors if self.grid[nr][nc] is None]

        if valid_neighbors:
            new_cell = random.choice(valid_neighbors)
            self.grid[new_cell[0]][new_cell[1]] = self.playerTurn

    def get_advanced_expansion(self, row, col):
        neighbors = self.get_neighbors(row, col)
        opponent_neighbors = [(nr, nc) for nr, nc in neighbors if self.grid[nr][nc] == self.get_opponent()]

        if opponent_neighbors:
            new_cell = random.choice(opponent_neighbors)
            self.grid[new_cell[0]][new_cell[1]] = self.playerTurn

    def random_expand(self, row, col):
        if not self.advance_mode:
            neighbors = self.get_neighbors(row, col)
            valid_neighbors = [(nr, nc) for nr, nc in neighbors if self.grid[nr][nc] is None]

            if valid_neighbors:
                new_cell = random.choice(valid_neighbors)
                self.grid[new_cell[0]][new_cell[1]] = self.playerTurn
                if self.expansion == 2 or self.expansion == 3:
                    self.get_expansion(new_cell[0], new_cell[1])
                    if self.expansion == 3:
                        self.get_expansion(new_cell[0], new_cell[1])
        else:
            neighbors = self.get_neighbors(row, col)
            opponent_neighbors = [(nr, nc) for nr, nc in neighbors if self.grid[nr][nc] == self.get_opponent()]
            if opponent_neighbors:
                # Randomly select an opponent's piece to overwrite
                new_cell = random.choice(opponent_neighbors)
                self.grid[new_cell[0]][new_cell[1]] = self.playerTurn
                if self.expansion == 2 or self.expansion == 3:
                    self.get_advanced_expansion(new_cell[0], new_cell[1])
                    if self.expansion == 3:
                        self.get_advanced_expansion(new_cell[0], new_cell[1])
            else:
                neighbors = self.get_neighbors(row, col)
                valid_neighbors = [(nr, nc) for nr, nc in neighbors if self.grid[nr][nc] is None]
                if valid_neighbors:
                    new_cell = random.choice(valid_neighbors)
                    self.grid[new_cell[0]][new_cell[1]] = self.playerTurn
                    if self.expansion == 2 or self.expansion == 3:
                        self.get_expansion(new_cell[0], new_cell[1])
                        if self.expansion == 3:
                            self.get_expansion(new_cell[0], new_cell[1])

    def handle_click(self, pos):
        x, y = pos
        col = (x - self.canvas_screen.x) // self.cell_width
        row = (y - self.canvas_screen.y) // self.cell_height
        if not self.multiplayer_active:
            if 0 <= row < self.rows and 0 <= col < self.cols:  # Ensure click is within the grid
                if self.grid[row][col] is None:  # If the clicked cell is empty
                    neighbors = self.get_neighbors(row, col)
                    if any(self.grid[nr][nc] == self.playerTurn for nr, nc in neighbors):  # Valid neighbor check
                        self.grid[row][col] = self.playerTurn  # Update the grid
                        self.random_expand(row, col)  # Expand to a random valid neighbor
                        self.playerTurn = 2 if self.playerTurn == 1 else 1  # Alternate turn
        else:
            if 0 <= row < self.rows and 0 <= col < self.cols:
                if self.grid[row][
                    col] is None and self.client.player_role == self.playerTurn:
                    neighbors = self.get_neighbors(row, col)
                    if any(self.grid[nr][nc] == self.playerTurn for nr, nc in neighbors):
                        self.grid[row][col] = self.playerTurn
                        self.random_expand(row, col)
                        self.send_data("update", {"grid": self.grid, "playerTurn": self.playerTurn})
                        self.playerTurn = 2 if self.playerTurn == 1 else 1

    def check_winner(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] is None:
                    neighbors = self.get_neighbors(row, col)
                    if any(self.grid[nr][nc] == self.playerTurn for nr, nc in neighbors):
                        return  # Current player has valid moves, continue the game

        # If no valid moves, fill all remaining cells with the opponent's pieces
        opponent = 2 if self.playerTurn == 1 else 1
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] is None:
                    self.grid[row][col] = opponent

        # Proceed to the winner method
        pygame.display.update()
        self.delay_active = True
        self.delay_start_time = pygame.time.get_ticks()

    def winner(self):
        if self.player1_score == self.player2_score:
            game_overText = self.title_font.render("Draw", True, (255, 255, 255))
            game_overText_rect = game_overText.get_rect(center=(self.width // 2, 100))
            playerImg = pygame.transform.scale(pygame.image.load("objects/drawnGame.png").convert_alpha(), (300, 300))
            playerImg_rect = playerImg.get_rect(center=(self.width // 2, self.height // 2 - 30))
        else:
            game_overText = self.title_font.render(f"Player {1 if self.player1_score > self.player2_score else 2} WINS! ", True, (255, 255, 255))
            game_overText_rect = game_overText.get_rect(center=(self.width // 2, 100))
            playerImg = pygame.transform.scale(pygame.image.load(
                "objects/player1Crowned.png" if self.player1_score > self.player2_score else "objects/player2Crowned.png").convert_alpha(),
                                               (300, 300))
            playerImg_rect = playerImg.get_rect(center=(self.width // 2, self.height // 2 - 30))

        try_againText = self.title_font.render("Try Again?", True, (255, 255, 255))
        try_againText_rect = try_againText.get_rect(center=(self.width // 2, 140))

        main_menuText = self.sub_title_font.render("Main Menu", True, (255, 255, 255))
        main_menuText_rect = main_menuText.get_rect(center=(self.width // 2, self.height // 2 + 180))

        restartText = self.sub_title_font.render("Restart", True, (255, 255, 255))
        restartText_rect = restartText.get_rect(center=(self.width // 2, self.height // 2 + 230))

        quitText = self.sub_title_font.render("Quit", True, (255, 255, 255))
        quitText_rect = quitText.get_rect(center=(self.width // 2, self.height // 2 + 280))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    if main_menuText_rect.collidepoint(event.pos) or restartText_rect.collidepoint(event.pos) or quitText_rect.collidepoint(event.pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restartText_rect.collidepoint(event.pos):
                        self.restart_game()
                        return
                    elif main_menuText_rect.collidepoint(event.pos):
                        self.run()
                        return
                    elif quitText_rect.collidepoint(event.pos):
                        sys.exit()

            self.screen.fill(self.background)
            self.screen.blit(game_overText, game_overText_rect)
            self.screen.blit(try_againText, try_againText_rect)
            self.screen.blit(playerImg, playerImg_rect)
            self.screen.blit(main_menuText, main_menuText_rect)
            self.screen.blit(restartText, restartText_rect)
            self.screen.blit(quitText, quitText_rect)

            if main_menuText_rect.collidepoint(pygame.mouse.get_pos()):
                arrow_rect_left = self.arrowImg.get_rect(center=(main_menuText_rect.left - self.arrow_offset, main_menuText_rect.centery))
                arrow_rect_right = self.arrowImg2.get_rect(center=(main_menuText_rect.right + self.arrow_offset, main_menuText_rect.centery))
                self.screen.blit(self.arrowImg, arrow_rect_left)
                self.screen.blit(self.arrowImg2, arrow_rect_right)
            elif restartText_rect.collidepoint(pygame.mouse.get_pos()):
                arrow_rect_left = self.arrowImg.get_rect(center=(restartText_rect.left - self.arrow_offset, restartText_rect.centery))
                arrow_rect_right = self.arrowImg2.get_rect(center=(restartText_rect.right + self.arrow_offset, restartText_rect.centery))
                self.screen.blit(self.arrowImg, arrow_rect_left)
                self.screen.blit(self.arrowImg2, arrow_rect_right)
            elif quitText_rect.collidepoint(pygame.mouse.get_pos()):
                arrow_rect_left = self.arrowImg.get_rect(center=(quitText_rect.left - self.arrow_offset, quitText_rect.centery))
                arrow_rect_right = self.arrowImg2.get_rect(center=(quitText_rect.right + self.arrow_offset, quitText_rect.centery))
                self.screen.blit(self.arrowImg, arrow_rect_left)
                self.screen.blit(self.arrowImg2, arrow_rect_right)

            pygame.display.update()

    def player_score(self):
        self.player1_score = sum(cell == 1 for row in self.grid for cell in row)
        self.player2_score = sum(cell == 2 for row in self.grid for cell in row)

    def draw_header(self):
        title_text = self.title_font.render(f"Player {self.playerTurn}", True, (255, 255, 255))
        title_text_rect = title_text.get_rect(center=(self.width // 2, 100))

        player1_score = self.title_font.render(f"P1:{self.player1_score}", True, (255, 255, 255))
        player2_score = self.title_font.render(f"P2:{self.player2_score}", True, (255, 255, 255))

        self.screen.blit(title_text, title_text_rect)
        self.screen.blit(player1_score, (self.width // 10, 130))
        self.screen.blit(player2_score, (590, 130))

    def multiplayer_exit_connection(self):
        if self.client:
            self.client.running = False
            self.client = None
        self.multiplayer_active = False
        self.server_ip_active = True
        if self.server:
            self.server.stop_server()
            self.server_ip = None
            self.server = None
        self.run()

    def pause(self):
        paused_text = self.title_font2.render("Game Paused", True, (255, 255, 255))
        paused_text_rect = paused_text.get_rect(center=(self.width // 2, 100))

        pausedImg = pygame.transform.scale(pygame.image.load("objects/pausedIcon.png").convert_alpha(), (163, 258))
        pausedImg_rect = pausedImg.get_rect(center=(self.width // 2, self.height // 2 - 70))

        resume_text = self.sub_title_font.render("Resume", True, (255, 255, 255))
        resume_text_rect = resume_text.get_rect(center=(self.width // 2, self.height // 2 + 100))

        main_menu_text = self.sub_title_font.render("Main Menu", True, (255, 255, 255))
        main_menu_text_rect = main_menu_text.get_rect(center=(self.width // 2, self.height // 2 + 150))

        restart_text = self.sub_title_font.render("Restart", True, (255, 255, 255))
        restart_text_rect = restart_text.get_rect(center=(self.width // 2, self.height // 2 + 200))

        quit_text = self.sub_title_font.render("Quit", True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=(self.width // 2, self.height // 2 + 250))

        author_text = self.author_font.render("Created by: TeamBa", True, (255, 255, 255))
        author_text_rect = author_text.get_rect(center=(self.width // 2, 720))

        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    if resume_text_rect.collidepoint(event.pos) or main_menu_text_rect.collidepoint(event.pos) or restart_text_rect.collidepoint(event.pos) or quit_text_rect.collidepoint(event.pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if resume_text_rect.collidepoint(event.pos):
                        return
                    elif main_menu_text_rect.collidepoint(event.pos):
                        if self.server:
                            self.multiplayer_exit_connection()
                        self.run()
                        return
                    elif restart_text_rect.collidepoint(event.pos):
                        self.restart_game()
                        return
                    elif quit_text_rect.collidepoint(event.pos):
                        sys.exit()

            self.screen.fill(self.background)
            self.screen.blit(paused_text, paused_text_rect)
            self.screen.blit(pausedImg, pausedImg_rect)
            self.screen.blit(resume_text, resume_text_rect)
            self.screen.blit(main_menu_text, main_menu_text_rect)
            self.screen.blit(restart_text, restart_text_rect)
            self.screen.blit(quit_text, quit_text_rect)
            self.screen.blit(author_text, author_text_rect)

            if resume_text_rect.collidepoint(mouse_pos):
                arrow_rect_left = self.arrowImg.get_rect(
                    center=(resume_text_rect.left - self.arrow_offset, resume_text_rect.centery))
                arrow_rect_right = self.arrowImg2.get_rect(
                    center=(resume_text_rect.right + self.arrow_offset, resume_text_rect.centery))
                self.screen.blit(self.arrowImg, arrow_rect_left)
                self.screen.blit(self.arrowImg2, arrow_rect_right)

            elif main_menu_text_rect.collidepoint(mouse_pos):
                arrow_rect_left = self.arrowImg.get_rect(
                    center=(main_menu_text_rect.left - self.arrow_offset, main_menu_text_rect.centery))
                arrow_rect_right = self.arrowImg2.get_rect(
                    center=(main_menu_text_rect.right + self.arrow_offset, main_menu_text_rect.centery))
                self.screen.blit(self.arrowImg, arrow_rect_left)
                self.screen.blit(self.arrowImg2, arrow_rect_right)

            elif restart_text_rect.collidepoint(mouse_pos):
                arrow_rect_left = self.arrowImg.get_rect(
                    center=(restart_text_rect.left - self.arrow_offset, restart_text_rect.centery))
                arrow_rect_right = self.arrowImg2.get_rect(
                    center=(restart_text_rect.right + self.arrow_offset, restart_text_rect.centery))
                self.screen.blit(self.arrowImg, arrow_rect_left)
                self.screen.blit(self.arrowImg2, arrow_rect_right)

            elif quit_text_rect.collidepoint(mouse_pos):
                arrow_rect_left = self.arrowImg.get_rect(
                    center=(quit_text_rect.left - self.arrow_offset, quit_text_rect.centery))
                arrow_rect_right = self.arrowImg2.get_rect(
                    center=(quit_text_rect.right + self.arrow_offset, quit_text_rect.centery))
                self.screen.blit(self.arrowImg, arrow_rect_left)
                self.screen.blit(self.arrowImg2, arrow_rect_right)

            pygame.display.update()

    def run(self):
        self.main_menu()
        self.place_initial_cell()
        while self.multiplayer_active and self.server_ip is None:
            pygame.time.wait(100)
        game_code_text = self.sub_title_font.render(f"Game Code: {self.server_ip}", True, (255, 0, 0))
        game_code_text_rect = game_code_text.get_rect(center=(self.width // 2, 30))

        pauseButton = pygame.transform.scale(pygame.image.load("objects/pauseButton.png").convert_alpha(), (40, 40))
        pauseButton_rect = pauseButton.get_rect(center=(self.width - 50, 40))
        while self.running:
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEMOTION:
                    if pauseButton_rect.collidepoint(event.pos) or game_code_text_rect.collidepoint(event.pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pauseButton_rect.collidepoint(event.pos):
                        self.pause()
                    elif self.canvas_screen.collidepoint(event.pos):
                        self.handle_click(event.pos)
                    elif game_code_text_rect.collidepoint(event.pos):
                        self.server_ip_active = False

            self.screen.fill(self.background)
            self.screen.blit(pauseButton, pauseButton_rect)
            self.player_score()
            self.draw_header() # draws game header
            self.draw_grid() # draws grid
            if self.multiplayer_active and self.server_ip_active:
                self.screen.blit(game_code_text, game_code_text_rect)
            if self.delay_active:
                current_time = pygame.time.get_ticks()
                if current_time - self.delay_start_time >= self.delay_duration:
                    self.delay_active = False
                    self.winner()
            else:
                self.check_winner()
            self.clock.tick(60)
            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
    sys.exit()
