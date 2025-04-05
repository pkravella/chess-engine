from flask import Flask, request, jsonify
from flask_cors import CORS
from chess_engine import ChessEngine
import chess
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.debug = True  # Enable debug mode
engine = ChessEngine()

@app.route('/')
def home():
    return "Chess Engine API is running. Use POST /analyze with a FEN string to analyze positions."

@app.route('/analyze', methods=['POST'])
def analyze_position():
    try:
        data = request.get_json()
        fen = data.get('fen', chess.STARTING_FEN)
        player_color = data.get('player_color', 'white')
        
        logger.debug(f"Analyzing position: {fen}")
        logger.debug(f"Player color: {player_color}")
        
        board = chess.Board(fen)
        top_moves = engine.get_top_moves(board, num_moves=3)
        
        # If playing as black, only show moves when it's black's turn
        # If playing as white, only show moves when it's white's turn
        should_show_moves = (
            (player_color == 'white' and board.turn == chess.WHITE) or
            (player_color == 'black' and board.turn == chess.BLACK)
        )
        
        response = {
            'moves': [
                {
                    'uci': move[0].uci(),
                    'san': board.san(move[0]),
                    'score': float(move[1])
                }
                for move in top_moves
            ] if should_show_moves else []
        }
        
        logger.debug(f"Response: {response}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    logger.info("Starting Chess Engine Server...")
    print("Server will be available at http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    app.run(host='127.0.0.1', port=5001, debug=True) 