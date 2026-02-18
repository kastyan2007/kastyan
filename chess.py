# chess.py

import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatType

# Хранение активных игр
active_games = {}

class ChessGame:
    def __init__(self, player1_id, player2_id=None):
        self.board = self.create_initial_board()
        self.current_turn = 'white'
        self.player1 = player1_id
        self.player2 = player2_id
        self.selected_piece = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.last_move = None
        
    def create_initial_board(self):
        board = [[' ' for _ in range(8)] for _ in range(8)]
        
        for i in range(8):
            board[1][i] = '♟'
            board[6][i] = '♙'
        
        black_pieces = ['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜']
        white_pieces = ['♖', '♘', '♗', '♕', '♔', '♗', '♘', '♖']
        
        for i in range(8):
            board[0][i] = black_pieces[i]
            board[7][i] = white_pieces[i]
            
        return board
    
    def get_piece_color(self, piece):
        if piece == ' ':
            return None
        if piece in ['♔', '♕', '♖', '♗', '♘', '♙']:
            return 'white'
        elif piece in ['♚', '♛', '♜', '♝', '♞', '♟']:
            return 'black'
        return None
    
    def get_valid_moves(self, row, col):
        piece = self.board[row][col]
        if piece == ' ':
            return []
        
        color = self.get_piece_color(piece)
        moves = []
        
        if piece in ['♙', '♟']:
            moves = self.get_pawn_moves(row, col, color)
        elif piece in ['♖', '♜']:
            moves = self.get_rook_moves(row, col, color)
        elif piece in ['♘', '♞']:
            moves = self.get_knight_moves(row, col, color)
        elif piece in ['♗', '♝']:
            moves = self.get_bishop_moves(row, col, color)
        elif piece in ['♕', '♛']:
            moves = self.get_queen_moves(row, col, color)
        elif piece in ['♔', '♚']:
            moves = self.get_king_moves(row, col, color)
            
        return moves
    
    def get_pawn_moves(self, row, col, color):
        moves = []
        direction = -1 if color == 'white' else 1
        start_row = 6 if color == 'white' else 1
        
        if 0 <= row + direction < 8 and self.board[row + direction][col] == ' ':
            moves.append((row + direction, col))
            if row == start_row and self.board[row + 2*direction][col] == ' ':
                moves.append((row + 2*direction, col))
        
        for dc in [-1, 1]:
            if 0 <= col + dc < 8 and 0 <= row + direction < 8:
                target = self.board[row + direction][col + dc]
                if target != ' ' and self.get_piece_color(target) != color:
                    moves.append((row + direction, col + dc))
        
        return moves
    
    def get_rook_moves(self, row, col, color):
        moves = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] == ' ':
                    moves.append((r, c))
                else:
                    if self.get_piece_color(self.board[r][c]) != color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc
        return moves
    
    def get_knight_moves(self, row, col, color):
        moves = []
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] == ' ' or self.get_piece_color(self.board[r][c]) != color:
                    moves.append((r, c))
        return moves
    
    def get_bishop_moves(self, row, col, color):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] == ' ':
                    moves.append((r, c))
                else:
                    if self.get_piece_color(self.board[r][c]) != color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc
        return moves
    
    def get_queen_moves(self, row, col, color):
        return self.get_rook_moves(row, col, color) + self.get_bishop_moves(row, col, color)
    
    def get_king_moves(self, row, col, color):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    if self.board[r][c] == ' ' or self.get_piece_color(self.board[r][c]) != color:
                        moves.append((r, c))
        return moves
    
    def make_move(self, from_pos, to_pos):
        if self.game_over:
            return False, "Игра уже окончена"
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.board[from_row][from_col]
        if piece == ' ':
            return False, "Нет фигуры в указанной позиции"
        
        piece_color = self.get_piece_color(piece)
        if piece_color != self.current_turn:
            return False, f"Сейчас ход {self.current_turn}ых"
        
        valid_moves = self.get_valid_moves(from_row, from_col)
        if (to_row, to_col) not in valid_moves:
            return False, "Недопустимый ход"
        
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = ' '
        
        if piece in ['♙', '♟'] and (to_row == 0 or to_row == 7):
            self.board[to_row][to_col] = '♕' if piece == '♙' else '♛'
        
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        self.last_move = (from_pos, to_pos)
        
        if self.check_checkmate():
            self.game_over = True
            self.winner = 'white' if self.current_turn == 'black' else 'black'
        
        return True, "Ход выполнен"
    
    def check_checkmate(self):
        white_king = any('♔' in row for row in self.board)
        black_king = any('♚' in row for row in self.board)
        
        if not white_king:
            self.winner = 'black'
            return True
        if not black_king:
            self.winner = 'white'
            return True
        return False

def format_board(board, selected_piece=None, valid_moves=None):
    result = "  a b c d e f g h\n"
    
    for i in range(8):
        row_num = 8 - i
        result += f"{row_num} "
        
        for j in range(8):
            piece = board[i][j]
            
            if selected_piece and (i, j) == selected_piece:
                result += f"[{piece}]"
            elif valid_moves and (i, j) in valid_moves:
                result += f"·{piece}·" if piece == ' ' else f"({piece})"
            else:
                result += f" {piece} "
        
        result += f" {row_num}\n"
    
    result += "  a b c d e f g h"
    return result

def create_game_keyboard(game_id):
    buttons = []
    
    for i in range(8):
        row_buttons = []
        for j in range(8):
            col_letter = chr(97 + j)
            row_num = 8 - i
            cell = f"{col_letter}{row_num}"
            row_buttons.append(
                InlineKeyboardButton(cell, callback_data=f"chess_move_{game_id}_{i}_{j}")
            )
        buttons.append(row_buttons)
    
    buttons.append([
        InlineKeyboardButton("🔄 Обновить", callback_data=f"chess_refresh_{game_id}"),
        InlineKeyboardButton("❌ Сдаться", callback_data=f"chess_forfeit_{game_id}")
    ])
    
    return InlineKeyboardMarkup(buttons)

# Функция регистрации для HeroKu
def register():
    print("✅ Модуль шахмат загружен!")
    
    # HeroKu ожидает, что функция вернет список хендлеров
    @Client.on_message(filters.command("chess") & filters.private)
    async def chess_command(client, message):
        user_id = message.from_user.id
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Играть с ботом", callback_data="chess_vs_bot")],
            [InlineKeyboardButton("👥 Играть с другом", callback_data="chess_vs_friend")],
            [InlineKeyboardButton("❌ Отмена", callback_data="chess_cancel")]
        ])
        
        await message.reply(
            "♟ **Шахматы** ♟\n\n"
            "Выберите режим игры:",
            reply_markup=keyboard
        )
    
    @Client.on_callback_query(filters.regex("^chess_vs_friend$"))
    async def chess_vs_friend(client, callback_query):
        user_id = callback_query.from_user.id
        
        game = ChessGame(user_id)
        active_games[user_id] = game
        
        await callback_query.message.edit_text(
            "🔗 **Ссылка для приглашения друга:**\n\n"
            f"Отправьте другу эту команду:\n"
            f"`/join_chess {user_id}`\n\n"
            "Ожидание присоединения второго игрока..."
        )
    
    @Client.on_message(filters.command("join_chess") & filters.private)
    async def join_chess(client, message):
        try:
            creator_id = int(message.command[1])
        except (IndexError, ValueError):
            await message.reply("❌ Неверный формат команды. Используйте: /join_chess [id_создателя]")
            return
        
        user_id = message.from_user.id
        
        if creator_id not in active_games:
            await message.reply("❌ Игра не найдена или уже началась")
            return
        
        game = active_games[creator_id]
        
        if game.player2 is not None:
            await message.reply("❌ В этой игре уже есть второй игрок")
            return
        
        if creator_id == user_id:
            await message.reply("❌ Нельзя присоединиться к своей собственной игре")
            return
        
        game.player2 = user_id
        
        await message.reply(
            "✅ **Вы присоединились к игре!**\n\n"
            "Игра начинается...",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("♟ Показать доску", callback_data=f"chess_show_{creator_id}")
            ]])
        )
        
        await client.send_message(
            creator_id,
            f"✅ Игрок {message.from_user.first_name} присоединился к игре!\n\n"
            "Белые фигуры у вас. Ваш ход!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("♟ Показать доску", callback_data=f"chess_show_{creator_id}")
            ]])
        )
    
    @Client.on_callback_query(filters.regex("^chess_vs_bot$"))
    async def chess_vs_bot(client, callback_query):
        user_id = callback_query.from_user.id
        
        game = ChessGame(user_id, "bot")
        active_games[user_id] = game
        
        board_text = format_board(game.board)
        keyboard = create_game_keyboard(user_id)
        
        await callback_query.message.edit_text(
            f"♟ **Игра с ботом** ♟\n\n"
            f"Ваш ход (белые):\n\n"
            f"```\n{board_text}\n```",
            reply_markup=keyboard
        )
    
    @Client.on_callback_query(filters.regex("^chess_move_"))
    async def chess_move(client, callback_query):
        data = callback_query.data.split("_")
        game_id = int(data[2])
        row = int(data[3])
        col = int(data[4])
        
        user_id = callback_query.from_user.id
        
        if game_id not in active_games:
            await callback_query.answer("❌ Игра не найдена")
            return
        
        game = active_games[game_id]
        
        current_player = game.player1 if game.current_turn == 'white' else game.player2
        
        if user_id != current_player and (game.player2 != "bot" or user_id != game.player1):
            await callback_query.answer("⏳ Сейчас не ваш ход!")
            return
        
        if game.game_over:
            await callback_query.answer("🏁 Игра уже окончена")
            return
        
        if game.selected_piece is None:
            piece = game.board[row][col]
            if piece == ' ':
                await callback_query.answer("❌ Здесь нет фигуры")
                return
            
            piece_color = game.get_piece_color(piece)
            if piece_color != game.current_turn:
                await callback_query.answer(f"❌ Сейчас ход {game.current_turn}ых")
                return
            
            game.selected_piece = (row, col)
            game.valid_moves = game.get_valid_moves(row, col)
            
            board_text = format_board(game.board, game.selected_piece, game.valid_moves)
            keyboard = create_game_keyboard(game_id)
            
            await callback_query.message.edit_text(
                f"♟ **Шахматы** ♟\n\n"
                f"Ход: {game.current_turn}\n"
                f"Выбрана фигура на {chr(97+col)}{8-row}\n\n"
                f"```\n{board_text}\n```",
                reply_markup=keyboard
            )
        else:
            from_pos = game.selected_piece
            to_pos = (row, col)
            
            success, message_text = game.make_move(from_pos, to_pos)
            
            if success:
                game.selected_piece = None
                game.valid_moves = []
                
                board_text = format_board(game.board)
                keyboard = create_game_keyboard(game_id)
                
                turn_text = f"Ход: {game.current_turn}"
                if game.game_over:
                    turn_text = f"🏁 Игра окончена! Победили {game.winner}"
                
                await callback_query.message.edit_text(
                    f"♟ **Шахматы** ♟\n\n"
                    f"{turn_text}\n\n"
                    f"```\n{board_text}\n```",
                    reply_markup=keyboard
                )
                
                if game.player2 == "bot" and not game.game_over and game.current_turn == 'black':
                    await asyncio.sleep(1)
                    await make_bot_move(client, game_id, callback_query.message)
            else:
                await callback_query.answer(f"❌ {message_text}")
                game.selected_piece = None
                game.valid_moves = []
    
    async def make_bot_move(client, game_id, message):
        if game_id not in active_games:
            return
        
        game = active_games[game_id]
        
        if game.game_over or game.current_turn != 'black':
            return
        
        all_moves = []
        for i in range(8):
            for j in range(8):
                piece = game.board[i][j]
                if piece != ' ' and game.get_piece_color(piece) == 'black':
                    moves = game.get_valid_moves(i, j)
                    for move in moves:
                        all_moves.append(((i, j), move))
        
        if all_moves:
            from_pos, to_pos = random.choice(all_moves)
            
            game.selected_piece = from_pos
            success, _ = game.make_move(from_pos, to_pos)
            
            if success:
                game.selected_piece = None
                
                board_text = format_board(game.board)
                keyboard = create_game_keyboard(game_id)
                
                turn_text = f"Ход: {game.current_turn}"
                if game.game_over:
                    turn_text = f"🏁 Игра окончена! Победили {game.winner}"
                
                await message.edit_text(
                    f"♟ **Шахматы** ♟\n\n"
                    f"{turn_text}\n\n"
                    f"```\n{board_text}\n```",
                    reply_markup=keyboard
                )
    
    @Client.on_callback_query(filters.regex("^chess_refresh_"))
    async def chess_refresh(client, callback_query):
        game_id = int(callback_query.data.split("_")[2])
        
        if game_id not in active_games:
            await callback_query.answer("❌ Игра не найдена")
            return
        
        game = active_games[game_id]
        
        board_text = format_board(game.board)
        keyboard = create_game_keyboard(game_id)
        
        turn_text = f"Ход: {game.current_turn}"
        if game.game_over:
            turn_text = f"🏁 Игра окончена! Победили {game.winner}"
        
        await callback_query.message.edit_text(
            f"♟ **Шахматы** ♟\n\n"
            f"{turn_text}\n\n"
            f"```\n{board_text}\n```",
            reply_markup=keyboard
        )
    
    @Client.on_callback_query(filters.regex("^chess_forfeit_"))
    async def chess_forfeit(client, callback_query):
        game_id = int(callback_query.data.split("_")[2])
        user_id = callback_query.from_user.id
        
        if game_id not in active_games:
            await callback_query.answer("❌ Игра не найдена")
            return
        
        game = active_games[game_id]
        
        if user_id not in [game.player1, game.player2]:
            await callback_query.answer("❌ Вы не участвуете в этой игре")
            return
        
        winner = "черные" if user_id == game.player1 else "белые"
        game.game_over = True
        game.winner = winner
        
        board_text = format_board(game.board)
        
        await callback_query.message.edit_text(
            f"♟ **Шахматы** ♟\n\n"
            f"🏁 Игрок сдался!\n"
            f"Победили {winner}!\n\n"
            f"```\n{board_text}\n```",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 Новая игра", callback_data="chess_new")
            ]])
        )
        
        del active_games[game_id]
    
    @Client.on_callback_query(filters.regex("^chess_new$"))
    async def chess_new(client, callback_query):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Играть с ботом", callback_data="chess_vs_bot")],
            [InlineKeyboardButton("👥 Играть с другом", callback_data="chess_vs_friend")],
            [InlineKeyboardButton("❌ Отмена", callback_data="chess_cancel")]
        ])
        
        await callback_query.message.edit_text(
            "♟ **Шахматы** ♟\n\n"
            "Выберите режим игры:",
            reply_markup=keyboard
        )
    
    @Client.on_callback_query(filters.regex("^chess_cancel$"))
    async def chess_cancel(client, callback_query):
        await callback_query.message.edit_text("❌ Игра отменена")
    
    @Client.on_callback_query(filters.regex("^chess_show_"))
    async def chess_show(client, callback_query):
        game_id = int(callback_query.data.split("_")[2])
        
        if game_id not in active_games:
            await callback_query.answer("❌ Игра не найдена")
            return
        
        game = active_games[game_id]
        
        board_text = format_board(game.board)
        
        turn_text = f"Ход: {game.current_turn}"
        if game.game_over:
            turn_text = f"🏁 Игра окончена! Победили {game.winner}"
        
        await callback_query.message.edit_text(
            f"♟ **Шахматы** ♟\n\n"
            f"{turn_text}\n\n"
            f"```\n{board_text}\n```",
            reply_markup=create_game_keyboard(game_id)
        )
    
    # HeroKu ожидает, что функция вернет список хендлеров
    return [
        chess_command,
        chess_vs_friend,
        join_chess,
        chess_vs_bot,
        chess_move,
        chess_refresh,
        chess_forfeit,
        chess_new,
        chess_cancel,
        chess_show
    ]
