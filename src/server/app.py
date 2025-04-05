from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class ImprovedChessEngine:
    def __init__(self):
        # Material values
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        # Common opening moves for white (from e4 or d4)
        self.opening_moves = {
            'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1': ['e2e4', 'd2d4'],  # Starting position
            'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1': ['e7e5', 'e7e6', 'c7c5'],  # After 1.e4
            'rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1': ['d7d5', 'g8f6', 'e7e6'],  # After 1.d4
        }
        
        # Position values for each piece type
        self.pawn_position_values = [
            0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5,  5, 10, 25, 25, 10,  5,  5,
            0,  0,  0, 20, 20,  0,  0,  0,
            5, -5,-10,  0,  0,-10, -5,  5,
            5, 10, 10,-20,-20, 10, 10,  5,
            0,  0,  0,  0,  0,  0,  0,  0
        ]
        
        self.knight_position_values = [
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50
        ]
        
        self.bishop_position_values = [
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20
        ]
        
        self.rook_position_values = [
            0,  0,  0,  0,  0,  0,  0,  0,
            5, 10, 10, 10, 10, 10, 10,  5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            0,  0,  0,  5,  5,  0,  0,  0
        ]
        
        self.queen_position_values = [
            -20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5,  5,  5,  5,  0,-10,
            -5,  0,  5,  5,  5,  5,  0, -5,
            0,  0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0,-10,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20
        ]
        
        self.king_position_values_middlegame = [
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -10,-20,-20,-20,-20,-20,-20,-10,
            20, 20,  0,  0,  0,  0, 20, 20,
            20, 30, 10,  0,  0, 10, 30, 20
        ]

    def get_position_value(self, piece, square, is_endgame=False):
        """Get the position value for a piece on a given square."""
        piece_type = piece.piece_type
        is_white = piece.color == chess.WHITE
        square_idx = square if is_white else 63 - square

        if piece_type == chess.PAWN:
            return self.pawn_position_values[square_idx]
        elif piece_type == chess.KNIGHT:
            return self.knight_position_values[square_idx]
        elif piece_type == chess.BISHOP:
            return self.bishop_position_values[square_idx]
        elif piece_type == chess.ROOK:
            return self.rook_position_values[square_idx]
        elif piece_type == chess.QUEEN:
            return self.queen_position_values[square_idx]
        elif piece_type == chess.KING:
            return self.king_position_values_middlegame[square_idx]
        return 0

    def evaluate_center_control(self, board):
        """Evaluate control of the center squares."""
        center_squares = [chess.E4, chess.E5, chess.D4, chess.D5]
        score = 0
        
        for square in center_squares:
            # Add points for pieces controlling center
            attackers = board.attackers(chess.WHITE, square)
            score += len(attackers) * 10
            attackers = board.attackers(chess.BLACK, square)
            score -= len(attackers) * 10
            
            # Additional points for occupying center
            piece = board.piece_at(square)
            if piece:
                if piece.color == chess.WHITE:
                    score += 30
                else:
                    score -= 30
        
        return score

    def evaluate_development(self, board):
        """Evaluate piece development in the opening."""
        score = 0
        
        # Check if pieces have moved from their starting squares
        if board.fullmove_number <= 10:  # Only consider in the opening
            # Knights and Bishops should be developed
            if not board.piece_at(chess.B1) and not board.piece_at(chess.G1):
                score += 20  # White knights are developed
            if not board.piece_at(chess.B8) and not board.piece_at(chess.G8):
                score -= 20  # Black knights are developed
                
            if not board.piece_at(chess.C1) and not board.piece_at(chess.F1):
                score += 20  # White bishops are developed
            if not board.piece_at(chess.C8) and not board.piece_at(chess.F8):
                score -= 20  # Black bishops are developed
                
            # Penalize early queen moves
            if not board.piece_at(chess.D1):
                score -= 10
            if not board.piece_at(chess.D8):
                score += 10
        
        return score

    def evaluate_material(self, board):
        """Evaluate material balance and piece activity."""
        score = 0
        
        # Count material and evaluate piece positions
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if not piece:
                continue
                
            value = self.piece_values[piece.piece_type]
            
            # Basic position evaluation
            if piece.piece_type == chess.PAWN:
                # Reward advanced pawns
                rank = chess.square_rank(square)
                if piece.color == chess.WHITE:
                    value += rank * 10
                else:
                    value += (7 - rank) * 10
                    
                # Penalize doubled pawns
                file = chess.square_file(square)
                pawns_in_file = sum(1 for r in range(8) if 
                    board.piece_at(chess.square(file, r)) and 
                    board.piece_at(chess.square(file, r)).piece_type == chess.PAWN and
                    board.piece_at(chess.square(file, r)).color == piece.color)
                if pawns_in_file > 1:
                    value -= 20
                    
            elif piece.piece_type == chess.KNIGHT:
                # Knights are better in the center
                file = chess.square_file(square)
                rank = chess.square_rank(square)
                center_distance = abs(3.5 - file) + abs(3.5 - rank)
                value -= int(center_distance * 10)
                
            elif piece.piece_type == chess.BISHOP:
                # Reward bishops for controlling many squares
                mobility = len(list(board.attacks(square)))
                value += mobility * 5
                
            elif piece.piece_type == chess.ROOK:
                # Rooks on open files
                file = chess.square_file(square)
                pawns_in_file = sum(1 for r in range(8) if 
                    board.piece_at(chess.square(file, r)) and 
                    board.piece_at(chess.square(file, r)).piece_type == chess.PAWN)
                if pawns_in_file == 0:
                    value += 30
                    
            elif piece.piece_type == chess.QUEEN:
                # Queens should have good mobility
                mobility = len(list(board.attacks(square)))
                value += mobility * 2
            
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value
                
        return score

    def evaluate_king_safety(self, board):
        """Evaluate king safety and threats."""
        score = 0
        
        for color in [chess.WHITE, chess.BLACK]:
            king_square = board.king(color)
            if king_square is None:
                continue
            
            # Check pawn shield
            king_file = chess.square_file(king_square)
            king_rank = chess.square_rank(king_square)
            shield_score = 0
            
            for f in [max(0, king_file - 1), king_file, min(7, king_file + 1)]:
                pawn_rank = king_rank + (1 if color == chess.WHITE else -1)
                if 0 <= pawn_rank <= 7:
                    pawn = board.piece_at(chess.square(f, pawn_rank))
                    if pawn and pawn.piece_type == chess.PAWN and pawn.color == color:
                        shield_score += 30
            
            # Count attackers near king
            danger_zone = [s for s in chess.SQUARES if abs(chess.square_file(s) - king_file) <= 2
                          and abs(chess.square_rank(s) - king_rank) <= 2]
            
            attackers = 0
            for square in danger_zone:
                attackers_to_square = board.attackers(not color, square)
                attackers += len(attackers_to_square)
            
            king_danger = attackers * 20
            
            if color == chess.WHITE:
                score += shield_score - king_danger
            else:
                score -= shield_score - king_danger
        
        return score

    def evaluate_threats(self, board):
        """Evaluate immediate threats and hanging pieces."""
        score = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if not piece:
                continue
                
            # Count attackers and defenders
            attackers = board.attackers(not piece.color, square)
            defenders = board.attackers(piece.color, square)
            
            if attackers:
                # Piece is under attack
                piece_value = self.piece_values[piece.piece_type]
                
                # Find the lowest value attacker
                min_attacker_value = min(self.piece_values[board.piece_at(attacker).piece_type] 
                                       for attacker in attackers)
                
                if not defenders:
                    # Hanging piece
                    if piece.color == chess.WHITE:
                        score -= piece_value
                    else:
                        score += piece_value
                elif min_attacker_value < piece_value:
                    # Piece is inadequately defended
                    if piece.color == chess.WHITE:
                        score -= (piece_value - min_attacker_value) // 2
                    else:
                        score += (piece_value - min_attacker_value) // 2
        
        return score

    def evaluate_position(self, board):
        """Evaluate the current position."""
        if board.is_checkmate():
            return -20000 if board.turn else 20000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
            
        # Material and piece activity
        score = self.evaluate_material(board)
        
        # King safety
        score += self.evaluate_king_safety(board)
        
        # Threats and hanging pieces
        score += self.evaluate_threats(board)
        
        # Mobility (weighted by game phase)
        piece_count = len(board.piece_map())
        mobility_weight = piece_count / 32.0  # More important in endgame
        
        if board.turn == chess.WHITE:
            score += len(list(board.legal_moves)) * 5 * mobility_weight
        else:
            score -= len(list(board.legal_moves)) * 5 * mobility_weight
        
        return score

    def get_best_move(self, board, depth=4):
        """Find the best move using minimax with alpha-beta pruning."""
        def quiescence_search(board, alpha, beta, depth=4):
            """Search captures until a quiet position."""
            stand_pat = self.evaluate_position(board)
            
            if depth == 0:
                return stand_pat
                
            if stand_pat >= beta:
                return beta
                
            alpha = max(alpha, stand_pat)
            
            # Look at captures only
            for move in board.legal_moves:
                if not board.is_capture(move):
                    continue
                    
                board.push(move)
                score = -quiescence_search(board, -beta, -alpha, depth - 1)
                board.pop()
                
                if score >= beta:
                    return beta
                alpha = max(alpha, score)
                
            return alpha

        def minimax(board, depth, alpha, beta, maximizing_player):
            """Minimax with alpha-beta pruning and quiescence search."""
            if depth == 0:
                return quiescence_search(board, alpha, beta)
                
            if board.is_game_over():
                if board.is_checkmate():
                    return -20000 if maximizing_player else 20000
                return 0
            
            if maximizing_player:
                max_eval = float('-inf')
                for move in self.order_moves(board):
                    board.push(move)
                    eval = minimax(board, depth - 1, alpha, beta, False)
                    board.pop()
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                return max_eval
            else:
                min_eval = float('inf')
                for move in self.order_moves(board):
                    board.push(move)
                    eval = minimax(board, depth - 1, alpha, beta, True)
                    board.pop()
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                return min_eval

        # Check opening book first
        fen = board.fen()
        if fen in self.opening_moves:
            move_uci = random.choice(self.opening_moves[fen])
            return chess.Move.from_uci(move_uci), 100

        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None, 0

        best_move = None
        best_eval = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Search each move
        for move in self.order_moves(board):
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            
            if eval > best_eval:
                best_eval = eval
                best_move = move
                
        return best_move, best_eval

    def order_moves(self, board):
        """Order moves for better alpha-beta pruning efficiency."""
        def move_value(move):
            value = 0
            
            # Captures are searched first, ordered by MVV/LVA
            if board.is_capture(move):
                victim_square = move.to_square
                victim = board.piece_at(victim_square)
                attacker = board.piece_at(move.from_square)
                if victim and attacker:
                    value = 10 * self.piece_values[victim.piece_type] - self.piece_values[attacker.piece_type]
            
            # Promotions are also valuable
            if move.promotion:
                value += self.piece_values[move.promotion]
            
            # Check moves
            if board.gives_check(move):
                value += 300
                
            # Control of center in opening/middlegame
            if board.fullmove_number <= 20:
                to_file = chess.square_file(move.to_square)
                to_rank = chess.square_rank(move.to_square)
                if 2 <= to_file <= 5 and 2 <= to_rank <= 5:
                    value += 50
                    
            return value
            
        moves = list(board.legal_moves)
        moves.sort(key=move_value, reverse=True)
        return moves

# Add root route to show server status
@app.route('/')
def index():
    return "Chess Analysis Server is running! Version 1.0"

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        fen = data.get('fen')
        player_color = data.get('player_color', 'white')
        
        logger.info(f"Received analysis request - FEN: {fen}, Player Color: {player_color}")
        
        if not fen:
            return jsonify({'error': 'No FEN position provided'}), 400

        # Create a board from the FEN
        board = chess.Board(fen)
        
        # Initialize our custom engine
        engine = ImprovedChessEngine()
        
        # Get the best move
        best_move, evaluation = engine.get_best_move(board)
        
        if best_move:
            # Convert evaluation to be from the player's perspective
            if player_color == 'black':
                evaluation = -evaluation
                
            # Format the evaluation as a string
            eval_str = f"{evaluation/100:+.2f}"
            
            logger.info(f"Analysis complete - Best move: {best_move.uci()}, Evaluation: {eval_str}")
            
            return jsonify({
                'moves': [{
                    'uci': best_move.uci(),
                    'score': eval_str
                }]
            })
        else:
            logger.warning("No legal moves found")
            return jsonify({'moves': []})
            
    except Exception as e:
        logger.error(f"Error analyzing position: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001) 