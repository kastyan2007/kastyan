# plugins/chess_game.py

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
        self.current_turn = 'white'  # Белые ходят первыми
        self.player1 = player1_id  # Белые
        self.player2 = player2_id  # Черные (может быть None для игры с ботом)
        self.selected_piece = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.last_move = None
        
    def create_initial_board(self):
        # Создаем начальную доску
        board = [[' ' for _ in range(8)] for _ in range(8)]
        
        # Расставляем пешки
        for i in range(8):
            board[1][i] = '♟'  # Черные пешки
            board[6][i] = '♙'  # Белые пешки
        
        # Расставляем остальные фигуры
        pieces = ['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜']
        for i in range(8):
            board[0][i] = pieces[i]  # Черные фигуры
            board[7][i] = pieces[i].upper()  # Белые фигуры (заглавные символы)
            
        # Заменяем заглавные на белые фигуры
        white_pieces = ['♖', '♘', '♗', '♕', '♔', '♗', '♘', '♖']
        for i in range(8):
            board[7][i] = white_pieces[i]
            
        return board
    
    def get_piece_color(self, piece):
        if piece == ' ':
            return None
        # Белые фигуры (U+2654 - U+2659)
        if piece in ['♔', '♕', '♖', '♗', '♘', '♙']:
            return 'white'
        # Черные фигуры (U+265A - U+265F)
        elif piece in ['♚', '♛', '♜', '♝', '♞', '♟']:
            return 'black'
        return None
    
    def get_valid_moves(self, row, col):
        piece = self.board[row][col]
        if piece == ' ':
            return []
        
        color = self.get_piece_color(piece)
        moves = []
        
        # Определение доступных ходов для каждой фигуры (упрощенная версия)
        if piece in ['♙', '♟']:  # Пешка
            moves = self.get_pawn_moves(row, col, color)
        elif piece in ['♖', '♜']:  # Ладья
            moves = self.get_rook_moves(row, col, color)
        elif piece in ['♘', '♞']:  # Конь
            moves = self.get_knight_moves(row, col, color)
        elif piece in ['♗', '♝']:  # Слон
            moves = self.get_bishop_moves(row, col, color)
        elif piece in ['♕', '♛']:  # Ферзь
            moves = self.get_queen_moves(row, col, color)
        elif piece in ['♔', '♚']:  # Король
            moves = self.get_king_moves(row, col, color)
            
        return moves
    
    def get_pawn_moves(self, row, col, color):
        moves = []
        direction = -1 if color == 'white' else 1
        start_row = 6 if color == 'white' else 1
        
        # Движение вперед
        if 0 <= row + direction < 8 and self.board[row + direction][col] == ' ':
            moves.append((row + direction, col))
            # Двойной ход с начальной позиции
            if row == start_row and self.board[row + 2*direction][col] == ' ':
                moves.append((row + 2*direction, col))
        
        # Взятие фигур
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
        
        # Проверяем, является ли ход допустимым
        valid_moves = self.get_valid_moves(from_row, from_col)
        if (to_row, to_col) not in valid_moves:
            return False, "Недопустимый ход"
        
        # Выполняем ход
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = ' '
        
        # Проверка на превращение пешки
        if piece in ['♙', '♟'] and (to_row == 0 or to_row == 7):
            # Превращаем в ферзя (для упрощения)
            self.board[to_row][to_col] = '♕' if piece == '♙' else '♛'
        
        # Меняем очередь
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        self.last_move = (from_pos, to_pos)
        
        # Проверка на мат (упрощенная)
        if self.check_checkmate():
            self.game_over = True
            self.winner = 'white' if self.current_turn == 'black' else 'black'
        
        return True, "Ход выполнен"
    
    def check_checkmate(self):
        # Упрощенная проверка - просто проверяем, есть ли король на доске
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
    """Форматирует доску для отображения в Telegram"""
    result = "  a b c d e f g h\n"
    
    for i in range(8):
        row_num = 8 - i
        result += f"{row_num} "
        
        for j in range(8):
            piece = board[i][j]
            
            # Подсветка выбранной фигуры и доступных ходов
            if selected_piece and (i, j) == selected_piece:
                result += f"[{piece}]"
            elif valid_moves and (i, j) in valid_moves:
                result += f"·{piece}·" if piece == ' ' else f"({piece})"
            else:
                result += f" {piece} "
        
        result += f" {row_num}\n"
    
    result += "  a b c d e f g h"
    return result

# Обработчик команды /chess
@Client.on_message(filters.command("chess") & filters.private)
async def chess_command(client, message):
    user_id = message.from_user.id
    
    # Создаем клавиатуру для выбора режима игры
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

# Обработчик создания игры с другом
@Client.on_callback_query(filters.regex("^chess_vs_friend$"))
async def chess_vs_friend(client, callback_query):
    user_id = callback_query.from_user.id
    
    # Создаем игру
    game = ChessGame(user_id)
    active_games[user_id] = game
    
    await callback_query.message.edit_text(
        "🔗 **Ссылка для приглашения друга:**\n\n"
        f"Отправьте другу эту команду:\n"
        f"`/join_chess {user_id}`\n\n"
        "Ожидание присоединения второго игрока..."
    )

# Обработчик присоединения к игре
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
    
    # Присоединяем игрока
    game.player2 = user_id
    
    await message.reply(
        "✅ **Вы присоединились к игре!**\n\n"
        "Игра начинается...",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("♟ Показать доску", callback_data=f"chess_show_{creator_id}")
        ]])
    )
    
    # Уведомляем создателя
    await client.send_message(
        creator_id,
        f"✅ Игрок {message.from_user.first_name} присоединился к игре!\n\n"
        "Белые фигуры у вас. Ваш ход!",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("♟ Показать доску", callback_data=f"chess_show_{creator_id}")
        ]])
    )

# Обработчик игры с ботом
@Client.on_callback_query(filters.regex("^chess_vs_bot$"))
async def chess_vs_bot(client, callback_query):
    user_id = callback_query.from_user.id
    
    # Создаем игру с ботом
    game = ChessGame(user_id, "bot")
    active_games[user_id] = game
    
    # Отправляем доску
    board_text = format_board(game.board)
    keyboard = create_game_keyboard(user_id)
    
    await callback_query.message.edit_text(
        f"♟ **Игра с ботом** ♟\n\n"
        f"Ваш ход (белые):\n\n"
        f"```\n{board_text}\n```",
        reply_markup=keyboard
    )

def create_game_keyboard(game_id):
    """Создает клавиатуру для игры"""
    buttons = []
    
    # Создаем кнопки для каждого ряда
    for i in range(8):
        row_buttons = []
        for j in range(8):
            # Каждая клетка - кнопка с координатами
            col_letter = chr(97 + j)  # a, b, c, ...
            row_num = 8 - i
            cell = f"{col_letter}{row_num}"
            row_buttons.append(
                InlineKeyboardButton(cell, callback_data=f"chess_move_{game_id}_{i}_{j}")
            )
        buttons.append(row_buttons)
    
    # Добавляем кнопки управления
    buttons.append([
        InlineKeyboardButton("🔄 Обновить", callback_data=f"chess_refresh_{game_id}"),
        InlineKeyboardButton("❌ Сдаться", callback_data=f"chess_forfeit_{game_id}")
    ])
    
    return InlineKeyboardMarkup(buttons)

# Обработчик ходов
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
    
    # Проверяем, чей ход
    current_player = game.player1 if game.current_turn == 'white' else game.player2
    
    if user_id != current_player and (game.player2 != "bot" or user_id != game.player1):
        await callback_query.answer("⏳ Сейчас не ваш ход!")
        return
    
    if game.game_over:
        await callback_query.answer("🏁 Игра уже окончена")
        return
    
    # Если фигура еще не выбрана
    if game.selected_piece is None:
        piece = game.board[row][col]
        if piece == ' ':
            await callback_query.answer("❌ Здесь нет фигуры")
            return
        
        piece_color = game.get_piece_color(piece)
        if piece_color != game.current_turn:
            await callback_query.answer(f"❌ Сейчас ход {game.current_turn}ых")
            return
        
        # Выбираем фигуру
        game.selected_piece = (row, col)
        game.valid_moves = game.get_valid_moves(row, col)
        
        # Показываем доску с подсветкой
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
        # Совершаем ход
        from_pos = game.selected_piece
        to_pos = (row, col)
        
        success, message_text = game.make_move(from_pos, to_pos)
        
        if success:
            # Сбрасываем выбор
            game.selected_piece = None
            game.valid_moves = []
            
            # Показываем обновленную доску
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
            
            # Если игра с ботом и не закончена, делаем ход бота
            if game.player2 == "bot" and not game.game_over and game.current_turn == 'black':
                await asyncio.sleep(1)  # Небольшая задержка
                await make_bot_move(client, game_id, callback_query.message)
        else:
            await callback_query.answer(f"❌ {message_text}")
            # Сбрасываем выбор при ошибке
            game.selected_piece = None
            game.valid_moves = []

async def make_bot_move(client, game_id, message):
    """Делает случайный ход за бота"""
    if game_id not in active_games:
        return
    
    game = active_games[game_id]
    
    if game.game_over or game.current_turn != 'black':
        return
    
    # Собираем все возможные ходы для черных
    all_moves = []
    for i in range(8):
        for j in range(8):
            piece = game.board[i][j]
            if piece != ' ' and game.get_piece_color(piece) == 'black':
                moves = game.get_valid_moves(i, j)
                for move in moves:
                    all_moves.append(((i, j), move))
    
    if all_moves:
        # Выбираем случайный ход
        from_pos, to_pos = random.choice(all_moves)
        
        # Делаем ход
        game.selected_piece = from_pos
        success, _ = game.make_move(from_pos, to_pos)
        
        if success:
            game.selected_piece = None
            
            # Обновляем доску
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

# Обработчик обновления доски
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

# Обработчик сдачи
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
    
    # Определяем победителя
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
    
    # Удаляем игру
    del active_games[game_id]

# Обработчик новой игры
@Client.on_callback_query(filters.regex("^chess_new$"))
async def chess_new(client, callback_query):
    user_id = callback_query.from_user.id
    
    # Создаем клавиатуру для выбора режима игры
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

# Обработчик отмены
@Client.on_callback_query(filters.regex("^chess_cancel$"))
async def chess_cancel(client, callback_query):
    await callback_query.message.edit_text("❌ Игра отменена")

# Обработчик показа доски
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
