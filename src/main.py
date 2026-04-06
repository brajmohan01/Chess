import pygame
import sys
import json
import os
import random

from const import *
from game import Game
from square import Square
from move import Move
from piece import Queen, Rook, Bishop, Knight
from ui import Button, Checkbox, InputBox, ConfirmationDialog
from network import Network

class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
        pygame.display.set_caption('Chess')
        self.game = Game()
        self.game_state = None
        self.room_code = None
        
        # Multiplayer State
        self.network = Network()
        self.joining = False
        self.connected_to_server = False
        self.player_role = None # 'white' or 'black' (None for local)
        self.error_msg = None
        self.active_dialog = None # ConfirmationDialog instance
        self.dialog_type = None # "resign" or "reset"
        
        self.input_name = InputBox(WIDTH//2 - 100, HEIGHT//2 - 100, 200, 40, label="Your Name")
        self.input_user = InputBox(WIDTH//2 - 100, HEIGHT//2 - 20, 200, 40, label="Username")
        self.input_code = InputBox(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 40, label="Room Code")
        self.btn_confirm_join = Button(WIDTH//2 - 60, HEIGHT//2 + 130, 120, 40, "CONNECT")

        # Load Profile
        self.profile = {"username": "Player1", "wins": 0, "losses": 0, "draws": 0, "resigns": 0}
        if os.path.exists('src/profile.json'):
            with open('src/profile.json', 'r') as f:
                self.profile = json.load(f)

        # UI Elements (Right Panel)
        self.chk_timed = Checkbox(BOARD_OFFSET_X + BOARD_WIDTH + 20, 20, 20, "Timed Match (10m)", True)
        self.btn_invite = Button(BOARD_OFFSET_X + BOARD_WIDTH + 20, 70, 100, 40, "Invite")
        self.btn_join = Button(BOARD_OFFSET_X + BOARD_WIDTH + 140, 70, 100, 40, "Join")
        self.btn_resign = Button(BOARD_OFFSET_X + BOARD_WIDTH + 20, 160, 220, 40, "Resign")
        self.btn_reset = Button(BOARD_OFFSET_X + BOARD_WIDTH + 20, 210, 220, 40, "Reset", color=(200, 50, 50))

        # Timer
        self.white_time = 600 # 10 mins
        self.black_time = 600
        self.last_tick = pygame.time.get_ticks()
        self.timer_started = False
        
        # Scroll State
        self.scroll_offset = 0
        
        self.font = pygame.font.SysFont("monospace", 20, bold=True)

    def save_profile(self):
        with open('src/profile.json', 'w') as f:
            json.dump(self.profile, f)

    def draw_panels(self, screen):
        # Left Panel (Timer + Moves)
        pygame.draw.rect(screen, (30, 30, 30), (0, 0, BOARD_OFFSET_X, HEIGHT))
        
        # Turn Indicator
        turn_text = "WHITES TURN" if self.game.next_player == 'white' else "BLACKS TURN"
        turn_color = (255, 255, 255) if self.game.next_player == 'white' else (150, 150, 150)
        lbl_turn = self.font.render(turn_text, 1, turn_color)
        screen.blit(lbl_turn, (20, 20))

        # Draw Timers
        if self.chk_timed.checked:
            wt = max(0, int(self.white_time))
            bt = max(0, int(self.black_time))
            w_str = f"White: {wt//60:02d}:{wt%60:02d}"
            b_str = f"Black: {bt//60:02d}:{bt%60:02d}"
            
            lbl_w = self.font.render(w_str, 1, (255, 255, 255))
            lbl_b = self.font.render(b_str, 1, (255, 255, 255))
            screen.blit(lbl_w, (20, HEIGHT - 50))
            screen.blit(lbl_b, (20, 55)) # Moved down from 20 to 55 to avoid overlap

        # Draw Move History
        history_font = pygame.font.SysFont("monospace", 16)
        lbl_h = self.font.render("MOVE HISTORY", 1, (200, 200, 200))
        screen.blit(lbl_h, (20, 100)) # Moved down to 100
        
        lbl_w_title = history_font.render("WHITE", 1, (255, 255, 255))
        lbl_b_title = history_font.render("BLACK", 1, (255, 255, 255))
        screen.blit(lbl_w_title, (20, 140)) # Moved down
        screen.blit(lbl_b_title, (150, 140)) # Moved down
        
        # Render moves with scrolling
        y_offset = 170 # Moved down
        visible_moves = self.game.board.move_history[self.scroll_offset * 2:]
        
        for i in range(0, len(visible_moves), 2):
            if y_offset > HEIGHT - 100: break 
            
            # White move
            m_w = visible_moves[i]
            move_str_w = f"{m_w[0][0].upper()}:{Square.get_alphacol(m_w[1].col)}{8-m_w[1].row}-{Square.get_alphacol(m_w[2].col)}{8-m_w[2].row}"
            lbl_mw = history_font.render(move_str_w, 1, (200, 200, 200))
            screen.blit(lbl_mw, (20, y_offset))
            
            # Black move
            if i + 1 < len(visible_moves):
                m_b = visible_moves[i+1]
                move_str_b = f"{m_b[0][0].upper()}:{Square.get_alphacol(m_b[1].col)}{8-m_b[1].row}-{Square.get_alphacol(m_b[2].col)}{8-m_b[2].row}"
                lbl_mb = history_font.render(move_str_b, 1, (200, 200, 200))
                screen.blit(lbl_mb, (150, y_offset))
            
            y_offset += 25

        # Scrollbar Indicator (Simple)
        if len(self.game.board.move_history) > 40:
            bar_height = 50
            bar_y = 170 + (self.scroll_offset / max(1, len(self.game.board.move_history)//2)) * (HEIGHT - 290)
            pygame.draw.rect(screen, (100, 100, 100), (280, bar_y, 10, bar_height))

        # Right Panel
        pygame.draw.rect(screen, (30, 30, 30), (BOARD_OFFSET_X + BOARD_WIDTH, 0, WIDTH - (BOARD_OFFSET_X + BOARD_WIDTH), HEIGHT))
        self.chk_timed.draw(screen)
        self.btn_invite.draw(screen)
        self.btn_join.draw(screen)
        self.btn_resign.draw(screen)
        self.btn_reset.draw(screen)
        
        # Connection Status
        status_text = "OFFLINE"
        status_color = (200, 200, 200)
        if self.connected_to_server:
            if self.player_role:
                status_text = "CONNECTED"
                status_color = (0, 255, 0)
                if self.game.next_player != self.game.player_color:
                    status_text = "THINKING..."
                    status_color = (255, 165, 0)
            else:
                status_text = "WAITING..."
                status_color = (255, 255, 0)
        
        lbl_status = self.font.render(status_text, 1, status_color)
        screen.blit(lbl_status, (BOARD_OFFSET_X + BOARD_WIDTH + 20, 270))

        # Room Code Display
        if self.room_code:
            lbl_code = self.font.render(f"CODE: {self.room_code}", 1, (255, 215, 0))
            screen.blit(lbl_code, (BOARD_OFFSET_X + BOARD_WIDTH + 20, 120))

        # Profile Stats
        lbl_p = self.font.render(f"Profile: {self.profile['username']}", 1, (255, 255, 255))
        lbl_w = self.font.render(f"Wins: {self.profile['wins']}", 1, (0, 255, 0))
        lbl_l = self.font.render(f"Losses: {self.profile['losses']}", 1, (255, 0, 0))
        lbl_d = self.font.render(f"Draws: {self.profile['draws']}", 1, (200, 200, 200))
        lbl_r = self.font.render(f"Resigns: {self.profile['resigns']}", 1, (255, 100, 100))
        screen.blit(lbl_p, (BOARD_OFFSET_X + BOARD_WIDTH + 20, 350))
        screen.blit(lbl_w, (BOARD_OFFSET_X + BOARD_WIDTH + 20, 380))
        screen.blit(lbl_l, (BOARD_OFFSET_X + BOARD_WIDTH + 20, 410))
        screen.blit(lbl_d, (BOARD_OFFSET_X + BOARD_WIDTH + 20, 440))
        screen.blit(lbl_r, (BOARD_OFFSET_X + BOARD_WIDTH + 20, 470))

    def mainloop(self):
        
        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger

        while True:
            # fill background for panels
            screen.fill((40, 40, 40))

            # check network messages
            while self.network.msg_queue:
                msg = self.network.msg_queue.pop(0)
                try:
                    if msg.get("type") == "start":
                        self.player_role = msg["color"]
                        game.player_color = self.player_role
                        print(f"Match started! You are {self.player_role}")
                    
                    elif msg.get("cmd") == "resign_request":
                        self.active_dialog = ConfirmationDialog(WIDTH//2 - 150, HEIGHT//2 - 75, 300, 150, "Opponent wants to RESIGN.\nAccept?")
                        self.dialog_type = "resign"
                        
                    elif msg.get("cmd") == "reset_request":
                        self.active_dialog = ConfirmationDialog(WIDTH//2 - 150, HEIGHT//2 - 75, 300, 150, "Opponent wants to RESET.\nAccept?")
                        self.dialog_type = "reset"
                        
                    elif msg.get("cmd") == "resign_response":
                        if msg["response"] == "YES":
                            self.game_state = "Opponent Resigned"
                            self.profile['wins'] += 1
                            self.save_profile()
                            
                    elif msg.get("cmd") == "reset_response":
                        if msg["response"] == "YES":
                            self.btn_reset.is_clicked((0,0)) # Perform reset locally
                            
                    elif msg.get("cmd") == "move":
                        print(f"Received network move: {msg}")
                        initial = Square(msg["initial"][0], msg["initial"][1])
                        final = Square(msg["final"][0], msg["final"][1])
                        move = Move(initial, final)

                        # Find piece and ensure moves are calculated
                        piece = board.squares[initial.row][initial.col].piece
                        if piece:
                            board.calc_moves(piece, initial.row, initial.col, bool=False)
                            board.move(piece, move)
                            board.set_true_en_passant(piece)
                            game.play_sound(False)
                            game.next_turn()
                            self.timer_started = True
                            self.game_state = board.check_game_over(game.next_player)
                        else:
                            print(f"Error: No piece found at {initial.row}, {initial.col}")
                except Exception as e:
                    print(f"Network Move Error: {e}")

            # update timer
            current_tick = pygame.time.get_ticks()
            dt = (current_tick - self.last_tick) / 1000.0
            self.last_tick = current_tick

            if self.timer_started and self.chk_timed.checked and not self.game_state:
                if game.next_player == 'white':
                    self.white_time -= dt
                    if self.white_time <= 0:
                        self.game_state = 'black_wins_on_time'
                else:
                    self.black_time -= dt
                    if self.black_time <= 0:
                        self.game_state = 'white_wins_on_time'

            # show methods
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)
            
            self.draw_panels(screen)
            
            if board.promotion_pending:
                game.show_promotion(screen)
                
            if self.game_state:
                if self.game_state == 'white_wins_on_time':
                    game.show_game_over(screen, 'TIME OUT: White Wins')
                elif self.game_state == 'black_wins_on_time':
                    game.show_game_over(screen, 'TIME OUT: Black Wins')
                elif self.game_state == 'resigned':
                    game.show_game_over(screen, 'RESIGNED')
                else:
                    game.show_game_over(screen, self.game_state)

            if dragger.dragging:
                dragger.update_blit(screen)

            # Draw Dialog
            if self.active_dialog:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(150)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
                self.active_dialog.draw(screen)

            # Draw Joining Overlay
            if self.joining:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(200)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
                
                self.input_name.draw(screen)
                self.input_user.draw(screen)
                self.input_code.draw(screen)
                self.btn_confirm_join.draw(screen)
                
                if self.error_msg:
                    lbl_err = self.font.render(self.error_msg, 1, (255, 0, 0))
                    lbl_rect = lbl_err.get_rect(center=(WIDTH//2, HEIGHT//2 + 190))
                    screen.blit(lbl_err, lbl_rect)

            for event in pygame.event.get():
                if self.active_dialog:
                    res = self.active_dialog.handle_event(event)
                    if res:
                        if res == "YES":
                            if self.dialog_type == "resign":
                                self.game_state = "resigned"
                                self.profile['losses'] += 1
                                self.profile['resigns'] += 1
                                self.save_profile()
                                self.network.send({"cmd": "resign_response", "code": self.room_code, "response": "YES"})
                            elif self.dialog_type == "reset":
                                self.network.send({"cmd": "reset_response", "code": self.room_code, "response": "YES"})
                                # Trigger local reset
                                self.btn_reset.is_clicked((0,0))
                        else: # NO
                            cmd = "resign_response" if self.dialog_type == "resign" else "reset_response"
                            self.network.send({"cmd": cmd, "code": self.room_code, "response": "NO"})
                        
                        self.active_dialog = None
                        self.dialog_type = None
                    continue

                if self.joining:
                    self.input_name.handle_event(event)
                    self.input_user.handle_event(event)
                    self.input_code.handle_event(event)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.btn_confirm_join.is_clicked(event.pos):
                            if self.network.connect():
                                # Update profile name
                                if self.input_user.text:
                                    self.profile['username'] = self.input_user.text
                                    self.save_profile()
                                    
                                self.room_code = self.input_code.text
                                self.network.send({"cmd": "join", "code": self.room_code})
                                self.connected_to_server = True
                                self.joining = False
                                self.error_msg = None
                            else:
                                self.error_msg = "CONNECTION FAILED: IS SERVER RUNNING?"
                            
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.joining = False
                    continue

                # Scroll
                if event.type == pygame.MOUSEWHEEL:
                    self.scroll_offset = max(0, self.scroll_offset - event.y)
                    continue

                # click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.chk_timed.toggle(event.pos): continue
                    
                    if self.btn_resign.is_clicked(event.pos) and not self.game_state:
                        if self.connected_to_server:
                            self.network.send({"cmd": "resign_request", "code": self.room_code})
                        else:
                            self.game_state = 'resigned'
                            self.profile['resigns'] += 1
                            self.profile['losses'] += 1
                            self.save_profile()
                        continue
                    
                    if self.btn_reset.is_clicked(event.pos):
                        if self.connected_to_server and not self.game_state:
                            self.network.send({"cmd": "reset_request", "code": self.room_code})
                        else:
                            game.reset()
                            game = self.game
                            board = self.game.board
                            dragger = self.game.dragger
                            self.game_state = None
                            self.timer_started = False
                            self.white_time = 600
                            self.black_time = 600
                            self.room_code = None
                            self.connected_to_server = False
                            self.player_role = None
                        continue

                    if self.btn_invite.is_clicked(event.pos):
                        self.room_code = "".join([str(random.randint(0, 9)) for _ in range(6)])
                        if self.network.connect():
                            self.network.send({"cmd": "create", "code": self.room_code})
                            self.connected_to_server = True
                        else:
                            print("Server not found - staying in offline mode")
                        continue
                    
                    if self.btn_join.is_clicked(event.pos):
                        self.room_code = None
                        self.joining = True
                        continue

                    if board.promotion_pending:
                        # ... (Promotion logic remains same, but would need network send)
                        continue

                    if self.game_state: continue
                    
                    # Restrict dragging to own turn and color
                    if self.player_role and game.next_player != self.player_role:
                        continue

                    dragger.update_mouse(event.pos)

                    # ADJUSTED COORDS FOR FLIPPED BOARD
                    clicked_row = dragger.mouseY // SQSIZE
                    clicked_col = (dragger.mouseX - BOARD_OFFSET_X) // SQSIZE
                    
                    if game.player_color == 'black':
                        clicked_row = ROWS - 1 - clicked_row
                        clicked_col = COLS - 1 - clicked_col

                    if 0 <= clicked_col < COLS and 0 <= clicked_row < ROWS:
                        if board.squares[clicked_row][clicked_col].has_piece():
                            piece = board.squares[clicked_row][clicked_col].piece
                            if piece.color == game.next_player:
                                board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                                # Save initial correctly for flipped
                                dragger.initial_row = clicked_row
                                dragger.initial_col = clicked_col
                                dragger.drag_piece(piece)
                
                # mouse motion
                elif event.type == pygame.MOUSEMOTION:
                    if self.game_state or board.promotion_pending: continue

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                
                # click release
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.game_state or board.promotion_pending: continue
                    
                    if dragger.dragging:
                        released_row = event.pos[1] // SQSIZE
                        released_col = (event.pos[0] - BOARD_OFFSET_X) // SQSIZE
                        
                        if game.player_color == 'black':
                            released_row = ROWS - 1 - released_row
                            released_col = COLS - 1 - released_col

                        if 0 <= released_col < COLS and 0 <= released_row < ROWS:
                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, released_col)
                            move = Move(initial, final)

                            if board.valid_move(dragger.piece, move):
                                captured = board.squares[released_row][released_col].has_piece()
                                board.move(dragger.piece, move)
                                board.set_true_en_passant(dragger.piece)                            
                                game.play_sound(captured)
                                game.next_turn()
                                self.timer_started = True
                                
                                # Send move to network
                                if self.connected_to_server:
                                    self.network.send({
                                        "cmd": "move", 
                                        "code": self.room_code,
                                        "initial": [dragger.initial_row, dragger.initial_col],
                                        "final": [released_row, released_col]
                                    })

                                if not board.promotion_pending:
                                    self.game_state = board.check_game_over(game.next_player)
                    
                    dragger.undrag_piece()
                
                # ... (rest remains same)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t: game.change_theme()
                    if event.key == pygame.K_r: self.btn_reset.is_clicked((0,0)) # trigger reset

                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            pygame.display.update()


main = Main()
main.mainloop()