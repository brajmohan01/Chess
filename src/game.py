import pygame

from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square
from piece import Queen, Rook, Bishop, Knight

class Game:

    def __init__(self):
        self.next_player = 'white'
        self.player_color = 'white' # 'white' or 'black'
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()

    # blit methods

    def show_bg(self, surface):
        theme = self.config.theme
        
        for row in range(ROWS):
            for col in range(COLS):
                # Flipped coords
                r = row if self.player_color == 'white' else ROWS - 1 - row
                c = col if self.player_color == 'white' else COLS - 1 - col

                # color
                color = theme.bg.light if (r + c) % 2 == 0 else theme.bg.dark
                # rect
                rect = (col * SQSIZE + BOARD_OFFSET_X, row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

                # row coordinates
                if col == 0:
                    color = theme.bg.dark if r % 2 == 0 else theme.bg.light
                    lbl = self.config.font.render(str(ROWS-r), 1, color)
                    lbl_pos = (5 + BOARD_OFFSET_X, 5 + row * SQSIZE)
                    surface.blit(lbl, lbl_pos)

                # col coordinates
                if row == 7:
                    color = theme.bg.dark if (r + c) % 2 == 0 else theme.bg.light
                    lbl = self.config.font.render(Square.get_alphacol(c), 1, color)
                    lbl_pos = (col * SQSIZE + BOARD_OFFSET_X + SQSIZE - 20, HEIGHT - 20)
                    surface.blit(lbl, lbl_pos)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                r = row if self.player_color == 'white' else ROWS - 1 - row
                c = col if self.player_color == 'white' else COLS - 1 - col

                if self.board.squares[r][c].has_piece():
                    piece = self.board.squares[r][c].piece
                    
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQSIZE + BOARD_OFFSET_X + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        theme = self.config.theme

        if self.dragger.dragging:
            piece = self.dragger.piece

            for move in piece.moves:
                r = move.final.row if self.player_color == 'white' else ROWS - 1 - move.final.row
                c = move.final.col if self.player_color == 'white' else COLS - 1 - move.final.col

                color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark
                rect = (c * SQSIZE + BOARD_OFFSET_X, r * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        theme = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                r = pos.row if self.player_color == 'white' else ROWS - 1 - pos.row
                c = pos.col if self.player_color == 'white' else COLS - 1 - pos.col

                color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark
                rect = (c * SQSIZE + BOARD_OFFSET_X, r * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_sqr:
            r = self.hovered_sqr.row if self.player_color == 'white' else ROWS - 1 - self.hovered_sqr.row
            c = self.hovered_sqr.col if self.player_color == 'white' else COLS - 1 - self.hovered_sqr.col

            color = (180, 180, 180)
            rect = (c * SQSIZE + BOARD_OFFSET_X, r * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, color, rect, width=3)

    # other methods

    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def set_hover(self, row, col):
        self.hovered_sqr = self.board.squares[row][col]

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()

    def show_promotion(self, surface):
        if self.board.promotion_pending:
            rect = (BOARD_OFFSET_X + SQSIZE * 2, SQSIZE * 3, SQSIZE * 4, SQSIZE * 2)
            pygame.draw.rect(surface, (200, 200, 200), rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, width=3)
            
            piece_classes = [('queen', Queen), ('rook', Rook), ('bishop', Bishop), ('knight', Knight)]
            color = self.board.promotion_pending[0].color
            
            for i, (name, p_class) in enumerate(piece_classes):
                temp_piece = p_class(color)
                temp_piece.set_texture(size=80)
                img = pygame.image.load(temp_piece.texture)
                img_center = BOARD_OFFSET_X + SQSIZE * 2 + SQSIZE//2 + i*SQSIZE, SQSIZE * 4
                surface.blit(img, img.get_rect(center=img_center))

    def show_game_over(self, surface, state):
        if state:
            rect = (BOARD_OFFSET_X + SQSIZE * 2, SQSIZE * 3, SQSIZE * 4, SQSIZE * 2)
            pygame.draw.rect(surface, (200, 200, 200), rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, width=3)
            
            font = pygame.font.SysFont("monospace", 40, bold=True)
            text = "CHECKMATE" if state == 'checkmate' else "STALEMATE"
            lbl = font.render(text, 1, (0, 0, 0))
            lbl_pos = lbl.get_rect(center=(BOARD_OFFSET_X + BOARD_WIDTH//2, SQSIZE * 4))
            surface.blit(lbl, lbl_pos)
