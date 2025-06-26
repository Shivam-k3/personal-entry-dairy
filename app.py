from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from textblob import TextBlob
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# File to store journal entries
JOURNAL_FILE = 'journal_entries.json'

def load_entries():
    """Load journal entries from JSON file"""
    if os.path.exists(JOURNAL_FILE):
        try:
            with open(JOURNAL_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_entries(entries):
    """Save journal entries to JSON file"""
    with open(JOURNAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

def analyze_sentiment(text):
    """Analyze sentiment using TextBlob with improved thresholds and crisis detection"""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    # Check for serious negative thoughts first
    serious_negative_words = [
        'suicide', 'kill myself', 'end my life', 'want to die', 'better off dead',
        'no reason to live', 'give up', 'can\'t take it anymore', 'hopeless',
        'worthless', 'burden', 'everyone would be better off', 'no point'
    ]
    
    text_lower = text.lower()
    for word in serious_negative_words:
        if word in text_lower:
            return 'Crisis'  # Special category for serious thoughts
    
    # More sensitive thresholds for better detection
    if polarity > 0.05:  # Lowered from 0.1
        return 'Positive'
    elif polarity < -0.05:  # Raised from -0.1
        return 'Negative'
    else:
        return 'Neutral'

def get_suggestion(mood):
    """Get personalized suggestion based on mood with crisis support"""
    import random
    
    suggestions = {
        'Crisis': [
            "You are not alone. Please call 988 (Suicide & Crisis Lifeline) right now - they're available 24/7 and want to help.",
            "These feelings are temporary, even if they don't feel that way. Please reach out to a crisis counselor at 988.",
            "You matter and your life has value. Please talk to someone you trust or call 988 for immediate support.",
            "It's okay to ask for help. Please call 988 or text HOME to 741741 for crisis support.",
            "You don't have to face this alone. Professional help is available and can make a huge difference.",
            "Please reach out to someone you trust or call 988. You deserve support and care.",
            "These thoughts are serious and you deserve professional help. Please call 988 immediately.",
            "You are stronger than you think. Please get help - call 988 or go to the nearest emergency room."
        ],
        'Positive': [
            "Keep up the great energy! Your positive mindset is contagious.",
            "Celebrate your wins today! You're doing amazing.",
            "Share your joy with others - happiness multiplies when shared.",
            "Take a moment to appreciate how far you've come.",
            "Your positive attitude will help you overcome any challenges.",
            "Great job maintaining such a positive outlook!",
            "Remember this feeling - you're capable of amazing things.",
            "Your happiness is well-deserved. Keep shining!"
        ],
        'Negative': [
            "It's okay to feel this way. Tomorrow is a new day.",
            "Consider talking to a friend or family member about your feelings.",
            "Try taking a walk or doing something you usually enjoy.",
            "Remember that difficult times are temporary. You're stronger than you think.",
            "Be gentle with yourself today. You're doing the best you can.",
            "Consider writing down what's bothering you - it can help clarify your thoughts.",
            "Sometimes a good cry or a long shower can help reset your mood.",
            "You don't have to face this alone. Reach out to someone you trust."
        ],
        'Neutral': [
            "Take a moment to reflect on what could make your day even better.",
            "Consider trying something new or reaching out to someone you haven't talked to in a while.",
            "Sometimes neutral days are perfect for planning and setting new goals.",
            "Use this calm energy to organize your thoughts and priorities.",
            "A neutral day can be a good opportunity to practice mindfulness.",
            "Consider what small changes might bring more joy to your day.",
            "Use this balanced state to make thoughtful decisions.",
            "Sometimes the best days start neutral and get better as they go."
        ]
    }
    
    return random.choice(suggestions.get(mood, ["Reflect on your day and see what insights you can gain."]))

@app.route('/api/journal', methods=['POST'])
def add_entry():
    """Add a new journal entry"""
    try:
        data = request.get_json()
        entry_text = data.get('entry', '').strip()
        
        if not entry_text:
            return jsonify({'error': 'Entry text is required'}), 400
        
        # Analyze sentiment
        mood = analyze_sentiment(entry_text)
        suggestion = get_suggestion(mood)
        
        # Create entry
        entry = {
            'id': int(datetime.now().timestamp() * 1000),  # Unique ID
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'entry': entry_text,
            'mood': mood,
            'suggestion': suggestion
        }
        
        # Load existing entries and add new one
        entries = load_entries()
        entries.insert(0, entry)  # Add to beginning
        
        # Keep only last 50 entries to prevent file from getting too large
        entries = entries[:50]
        
        # Save to file
        save_entries(entries)
        
        return jsonify({
            'success': True,
            'entry': entry,
            'message': 'Entry added successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/journal', methods=['GET'])
def get_entries():
    """Get all journal entries (or last N entries)"""
    try:
        entries = load_entries()
        
        # Get limit from query parameter (default 7)
        limit = request.args.get('limit', 7, type=int)
        entries = entries[:limit]
        
        return jsonify({
            'success': True,
            'entries': entries,
            'count': len(entries)
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/journal/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    """Delete a specific journal entry"""
    try:
        entries = load_entries()
        
        # Find and remove entry
        original_count = len(entries)
        entries = [entry for entry in entries if entry.get('id') != entry_id]
        
        if len(entries) == original_count:
            return jsonify({'error': 'Entry not found'}), 404
        
        save_entries(entries)
        
        return jsonify({
            'success': True,
            'message': 'Entry deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get journal statistics"""
    try:
        entries = load_entries()
        
        if not entries:
            return jsonify({
                'success': True,
                'stats': {
                    'total_entries': 0,
                    'mood_distribution': {},
                    'average_mood': 'No data'
                }
            })
        
        # Count mood distribution
        mood_counts = {}
        for entry in entries:
            mood = entry.get('mood', 'Unknown')
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        # Calculate average mood
        mood_values = {'Positive': 1, 'Neutral': 0, 'Negative': -1}
        total_mood_value = sum(mood_values.get(entry.get('mood', 'Neutral'), 0) for entry in entries)
        avg_mood_value = total_mood_value / len(entries)
        
        if avg_mood_value > 0.3:
            average_mood = 'Positive'
        elif avg_mood_value < -0.3:
            average_mood = 'Negative'
        else:
            average_mood = 'Neutral'
        
        return jsonify({
            'success': True,
            'stats': {
                'total_entries': len(entries),
                'mood_distribution': mood_counts,
                'average_mood': average_mood
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/index.html')
def serve_index():
    """Serve the main journal app"""
    return send_from_directory('.', 'index.html')

@app.route('/')
def home():
    """Serve the main page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Journal API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            code { background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>📖 Personal Daily Journal API</h1>
        <p>Your journal backend is running successfully!</p>
        
        <h2>Available Endpoints:</h2>
        
        <div class="endpoint">
            <h3>POST /api/journal</h3>
            <p>Add a new journal entry</p>
            <code>{"entry": "Your journal text here"}</code>
        </div>
        
        <div class="endpoint">
            <h3>GET /api/journal</h3>
            <p>Get all journal entries</p>
            <code>Optional: ?limit=7</code>
        </div>
        
        <div class="endpoint">
            <h3>DELETE /api/journal/&lt;id&gt;</h3>
            <p>Delete a specific entry</p>
        </div>
        
        <div class="endpoint">
            <h3>GET /api/stats</h3>
            <p>Get journal statistics</p>
        </div>
        
        <p><a href="/index.html">Open Journal App</a></p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🚀 Starting Personal Daily Journal API...")
    print("📖 Open http://localhost:5000 in your browser")
    print("📝 API will be available at http://localhost:5000/api/journal")
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Get port from environment variable (for Railway/Heroku) or use 5000 for local
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 