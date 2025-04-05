// Utility function to get the current FEN position from chess.com
function getChessComPosition() {
    try {
        const moveList = document.querySelector('wc-simple-move-list');
        if (!moveList) {
            return null;
        }

        const moves = [];
        const moveNodes = moveList.querySelectorAll('.node-highlight-content');
        moveNodes.forEach(node => {
            const moveText = node.textContent.trim();
            if (moveText && !moveText.match(/^\d+\./) && moveText !== ':before') {
                moves.push(moveText);
            }
        });

        if (moves.length === 0) {
            return 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';  // Starting position
        }

        // Use chess.js to reconstruct the position
        const chess = new Chess();
        moves.forEach(move => {
            try {
                chess.move(move);
            } catch (e) {
                console.error('Invalid move:', move, e);
            }
        });

        return chess.fen();
    } catch (error) {
        console.error('Error getting position:', error);
        return null;
    }
}

// Helper function to reconstruct position from moves
function reconstructPositionFromMoves(moves) {
    try {
        console.log('Reconstructing position from moves:', moves);
        // Create a Chess.js instance
        const chess = new Chess();
        
        // Apply each move
        moves.forEach(move => {
            try {
                console.log('Applying move:', move);
                chess.move(move, { sloppy: true });
            } catch (e) {
                console.error('Invalid move:', move, e);
            }
        });
        
        // Get the resulting FEN
        const fen = chess.fen();
        console.log('Reconstructed FEN from moves:', fen);
        return fen;
    } catch (error) {
        console.error('Error reconstructing position:', error);
        return null;
    }
}

// Helper function to convert position map to FEN
function convertPositionToFen(position) {
    const pieceMap = {
        'white': {
            'pawn': 'P',
            'knight': 'N',
            'bishop': 'B',
            'rook': 'R',
            'queen': 'Q',
            'king': 'K'
        },
        'black': {
            'pawn': 'p',
            'knight': 'n',
            'bishop': 'b',
            'rook': 'r',
            'queen': 'q',
            'king': 'k'
        }
    };

    let fen = '';
    for (let rank = 0; rank < 8; rank++) {
        let emptySquares = 0;
        for (let file = 0; file < 8; file++) {
            const piece = position[rank][file];
            if (piece) {
                if (emptySquares > 0) {
                    fen += emptySquares;
                    emptySquares = 0;
                }
                fen += pieceMap[piece.color][piece.type];
            } else {
                emptySquares++;
            }
        }
        if (emptySquares > 0) {
            fen += emptySquares;
        }
        if (rank < 7) fen += '/';
    }

    // Add the rest of the FEN string (assuming it's white's turn, all castling rights, no en passant)
    // This is a simplification - ideally we'd get the actual game state
    fen += ' w KQkq - 0 1';
    console.log('Generated FEN:', fen);
    return fen;
}

// Function to get the player's color (true for white, false for black)
function isPlayingWhite() {
    const board = document.querySelector('chess-board');
    return !board || board.getAttribute('board-orientation') !== 'black';
}

// Function to create and add an SVG arrow to the board
function createArrow(from, to, color = '#00ff00', width = 8) {
    // Find the chess board using the same method that works in getChessComPosition
    console.log('Searching for chess board...');
    
    // Wait a short moment to ensure the board is fully loaded
    setTimeout(() => {
        const board = document.querySelector('chess-board');
        console.log('Board element found:', board);

        if (!board) {
            console.log('Could not find chess board for arrow creation');
            return;
        }

        // Find the game container (this is where we'll add our SVG)
        const gameContainer = document.querySelector('.board-layout-chessboard');
        if (!gameContainer) {
            console.log('Could not find game container');
            return;
        }

        // Get board dimensions from the game container
        const boardRect = gameContainer.getBoundingClientRect();
        console.log('Board dimensions:', boardRect);

        // Ensure we have valid board dimensions
        if (boardRect.width < 100 || boardRect.height < 100) {
            console.log('Invalid board dimensions, retrying in 500ms');
            setTimeout(() => createArrow(from, to, color, width), 500);
            return;
        }

        // Get board orientation
        const isFlipped = board.getAttribute('board-orientation') === 'black';
        console.log('Board orientation:', isFlipped ? 'black' : 'white');

        const squareSize = boardRect.width / 8;
        console.log('Square size:', squareSize);

        // Convert chess squares to coordinates
        function squareToCoords(square) {
            const file = square.charCodeAt(0) - 'a'.charCodeAt(0);
            const rank = 8 - parseInt(square[1]);
            
            // Adjust for board orientation
            const x = isFlipped ? 7 - file : file;
            const y = isFlipped ? 7 - rank : rank;
            
            const coords = {
                x: (x * squareSize) + (squareSize / 2),
                y: (y * squareSize) + (squareSize / 2)
            };
            console.log(`Square ${square} coordinates:`, coords);
            return coords;
        }

        // Clear any existing arrows first
        clearArrows();

        // Create SVG element with explicit dimensions
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', 'chess-arrow');
        svg.setAttribute('width', boardRect.width);
        svg.setAttribute('height', boardRect.height);
        svg.style.position = 'absolute';
        svg.style.top = '0';
        svg.style.left = '0';
        svg.style.pointerEvents = 'none';
        svg.style.zIndex = '1000';

        // Calculate coordinates
        const fromCoords = squareToCoords(from);
        const toCoords = squareToCoords(to);

        // Create arrow path
        const arrowPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        
        // Calculate arrow parameters
        const dx = toCoords.x - fromCoords.x;
        const dy = toCoords.y - fromCoords.y;
        const angle = Math.atan2(dy, dx);
        const headLength = squareSize * 0.3;
        const headAngle = Math.PI / 6;

        // Calculate arrow head coordinates
        const headX1 = toCoords.x - headLength * Math.cos(angle - headAngle);
        const headY1 = toCoords.y - headLength * Math.sin(angle - headAngle);
        const headX2 = toCoords.x - headLength * Math.cos(angle + headAngle);
        const headY2 = toCoords.y - headLength * Math.sin(angle + headAngle);

        // Create the path
        const pathD = `M ${fromCoords.x} ${fromCoords.y} 
                       L ${toCoords.x} ${toCoords.y}
                       M ${toCoords.x} ${toCoords.y}
                       L ${headX1} ${headY1}
                       M ${toCoords.x} ${toCoords.y}
                       L ${headX2} ${headY2}`;

        arrowPath.setAttribute('d', pathD);
        arrowPath.setAttribute('stroke', color);
        arrowPath.setAttribute('stroke-width', width);
        arrowPath.setAttribute('fill', 'none');
        arrowPath.style.opacity = '0.8';

        svg.appendChild(arrowPath);

        // Add the SVG to the game container
        console.log('Adding arrow to game container');
        gameContainer.appendChild(svg);
        console.log('Arrow added successfully');
    }, 100);  // Small delay to ensure board is ready
}

// Function to clear all arrows
function clearArrows() {
    const arrows = document.querySelectorAll('.chess-arrow');
    arrows.forEach(arrow => arrow.remove());
}

// Function to draw the best move
function drawBestMove(move) {
    if (!move || !move.uci) return;
    const from = move.uci.substring(0, 2);
    const to = move.uci.substring(2, 4);
    createArrow(from, to, '#00ff00', 8);
}

// Function to display analysis results
function displayAnalysisResults(move) {
    // Remove any existing analysis display
    const existingDisplay = document.querySelector('.chess-analysis-container');
    if (existingDisplay) {
        existingDisplay.remove();
    }

    // Create container for analysis results
    const container = document.createElement('div');
    container.className = 'chess-analysis-container';

    // Create content
    let content = '';
    if (move && move.uci) {
        const from = move.uci.substring(0, 2);
        const to = move.uci.substring(2, 4);
        content = `Best move: ${from}-${to} (Score: ${move.score})`;
    } else {
        content = 'No recommended moves';
    }

    container.textContent = content;

    // Find the game container and add our display
    const gameContainer = document.querySelector('.board-layout-chessboard');
    if (gameContainer) {
        gameContainer.parentElement.appendChild(container);
    }
}

// Function to analyze the current position
async function analyzePosition() {
    try {
        console.log('Starting position analysis...');
        const fen = getChessComPosition();
        console.log('Current FEN:', fen);
        
        if (!fen) {
            console.error('Could not get FEN position');
            displayAnalysisResults(null);
            return;
        }

        const response = await fetch('http://localhost:5001/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                fen: fen,
                player_color: isPlayingWhite() ? 'white' : 'black'
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Analysis response:', data);
        
        if (data.moves && data.moves.length > 0) {
            displayAnalysisResults(data.moves[0]);
        } else {
            displayAnalysisResults(null);
        }
    } catch (error) {
        console.error('Error during analysis:', error);
        displayAnalysisResults(null);
    }
}

// Function to check if we're in a chess game
function isInChessGame() {
    return window.location.hostname.includes('chess.com') && 
           (window.location.pathname.includes('/game/') || 
            window.location.pathname.includes('/play/'));
}

// Function to wait for the chess board to be ready
function waitForChessBoard() {
    return new Promise((resolve) => {
        const checkBoard = () => {
            // Try multiple selectors that could identify the chess board
            const board = document.querySelector('chess-board, .board, [data-board], .board-layout-chessboard');
            const gameContainer = document.querySelector('.board-layout-chessboard');
            
            if (board && gameContainer) {
                console.log('Chess board found:', board);
                console.log('Game container found:', gameContainer);
                resolve({ board, gameContainer });
            } else {
                console.log('Waiting for chess board...');
                console.log('Current selectors found:', {
                    'chess-board': document.querySelector('chess-board'),
                    '.board': document.querySelector('.board'),
                    '[data-board]': document.querySelector('[data-board]'),
                    '.board-layout-chessboard': document.querySelector('.board-layout-chessboard')
                });
                setTimeout(checkBoard, 1000); // Increased delay to 1 second
            }
        };
        checkBoard();
    });
}

// Initialize the extension
async function initializeExtension() {
    console.log('Initializing chess analysis extension...');
    
    try {
        // Wait for the chess board to be ready
        const { board, gameContainer } = await waitForChessBoard();
        
        // Create analyze button if it doesn't exist
        let analyzeButton = document.querySelector('.analyze-button');
        if (!analyzeButton) {
            analyzeButton = document.createElement('button');
            analyzeButton.className = 'analyze-button';
            analyzeButton.textContent = 'Analyze Position';
            
            // Add click handler
            analyzeButton.addEventListener('click', analyzePosition);
            
            // Insert the button next to the board
            if (gameContainer && gameContainer.parentElement) {
                gameContainer.parentElement.appendChild(analyzeButton);
                console.log('Analysis button added successfully');
            } else {
                console.error('Could not find appropriate container for button');
            }
        }
    } catch (error) {
        console.error('Error initializing extension:', error);
    }
}

// Function to initialize the extension with retries
function initialize() {
    if (isInChessGame()) {
        console.log('Chess game detected, initializing extension...');
        initializeExtension().catch(error => {
            console.error('Failed to initialize extension:', error);
        });
    } else {
        console.log('Not a chess game page, current path:', window.location.pathname);
    }
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', initialize);

// Also try after the page has loaded
if (document.readyState === 'complete') {
    initialize();
}

// Watch for URL changes (for single-page app navigation)
let lastUrl = location.href;
new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
        lastUrl = url;
        console.log('URL changed, reinitializing...');
        setTimeout(initialize, 1000); // Wait a second after URL change
    }
}).observe(document, { subtree: true, childList: true });

// Try multiple times during page load
const initializationAttempts = [0, 1000, 2000, 3000]; // Try at 0s, 1s, 2s, and 3s
initializationAttempts.forEach(delay => {
    setTimeout(initialize, delay);
}); 