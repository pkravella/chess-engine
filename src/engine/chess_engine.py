import chess
import numpy as np

class ChessEngine:
    def __init__(self):
        # Piece values for material evaluation
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        # Position weights for piece-square tables
        self.pawn_weights = np.array([
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ])

    def evaluate_position(self, board):
        """
        Evaluates the current position on the board.
        Returns a score from white's perspective.
        """
        if board.is_checkmate():
            return -np.inf if board.turn else np.inf
        
        score = 0
        
        # Material evaluation
        for piece_type in chess.PIECE_TYPES:
            score += len(board.pieces(piece_type, chess.WHITE)) * self.piece_values[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.piece_values[piece_type]
        
        # Position evaluation (only pawns for now)
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None:
                if piece.piece_type == chess.PAWN:
                    rank = chess.square_rank(square)
                    file = chess.square_file(square)
                    if piece.color == chess.WHITE:
                        score += self.pawn_weights[rank][file]
                    else:
                        score -= self.pawn_weights[7-rank][file]
        
        return score

    def get_best_move(self, board, depth=3):
        """
        Returns the best move for the current position using minimax algorithm.
        """
        def minimax(board, depth, alpha=-np.inf, beta=np.inf, maximizing_player=True):
            if depth == 0 or board.is_game_over():
                return self.evaluate_position(board)
            
            if maximizing_player:
                max_eval = -np.inf
                for move in board.legal_moves:
                    board.push(move)
                    eval = minimax(board, depth-1, alpha, beta, False)
                    board.pop()
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                return max_eval
            else:
                min_eval = np.inf
                for move in board.legal_moves:
                    board.push(move)
                    eval = minimax(board, depth-1, alpha, beta, True)
                    board.pop()
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                return min_eval

        best_move = None
        best_value = -np.inf if board.turn else np.inf
        
        for move in board.legal_moves:
            board.push(move)
            value = minimax(board, depth-1, -np.inf, np.inf, not board.turn)
            board.pop()
            
            if board.turn and value > best_value:
                best_value = value
                best_move = move
            elif not board.turn and value < best_value:
                best_value = value
                best_move = move
                
        return best_move

    def get_top_moves(self, board, num_moves=3, depth=3):
        """
        Returns the top N best moves for the current position.
        """
        moves = []
        for move in board.legal_moves:
            board.push(move)
            value = self.evaluate_position(board)
            moves.append((move, value))
            board.pop()
            
        moves.sort(key=lambda x: x[1], reverse=board.turn)
        return moves[:num_moves] 