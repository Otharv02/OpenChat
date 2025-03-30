from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import string
import json
from datetime import datetime
import socket

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# List of adjectives and nouns for random names
ADJECTIVES = ['Happy', 'Clever', 'Brave', 'Gentle', 'Swift', 'Bright', 'Kind', 'Wise', 'Quick', 'Cool']
NOUNS = ['Panda', 'Fox', 'Eagle', 'Tiger', 'Dolphin', 'Wolf', 'Bear', 'Lion', 'Hawk', 'Owl']

# Store rooms and their data
rooms = {}

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_random_name():
    return f"{random.choice(ADJECTIVES)}{random.choice(NOUNS)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_room', methods=['POST'])
def create_room():
    try:
        room_code = generate_room_code()
        rooms[room_code] = {
            'users': {},  # Changed to dict to store user names
            'messages': [],  # Added to store chat messages
            'created_at': datetime.now().isoformat()
        }
        return jsonify({'room_code': room_code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/join_room/<room_code>')
def join_room_page(room_code):
    if room_code in rooms:
        return render_template('room.html', room_code=room_code)
    return "Room not found", 404

@socketio.on('join')
def on_join(data):
    try:
        room_code = data.get('room_code')
        if room_code not in rooms:
            return
        
        # Generate a random name for the user if they don't have one
        if request.sid not in rooms[room_code]['users']:
            user_name = generate_random_name()
            rooms[room_code]['users'][request.sid] = user_name
            join_room(room_code)
            
            # Send system message about new user
            message = {
                'type': 'system',
                'content': f'{user_name} joined the room',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            rooms[room_code]['messages'].append(message)
            
            # Emit room data to all users
            emit('room_data', {
                'users': list(rooms[room_code]['users'].values()),
                'messages': rooms[room_code]['messages']
            }, room=room_code)
            
            # Send user their assigned name
            emit('status', {'user_name': user_name})

    except Exception as e:
        print(f"Error in on_join: {str(e)}")
        emit('error', {'message': 'Failed to join room'})

@socketio.on('leave')
def on_leave(data):
    try:
        room_code = data['room_code']
        if room_code in rooms and request.sid in rooms[room_code]['users']:
            user_name = rooms[room_code]['users'][request.sid]
            leave_room(room_code)
            
            # Add system message about user leaving
            leave_message = {
                'type': 'system',
                'content': f'{user_name} left the room',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            rooms[room_code]['messages'].append(leave_message)
            
            del rooms[room_code]['users'][request.sid]
            emit('status', {'msg': 'Left room'})
            
            # Broadcast updated user list and leave message
            emit('room_update', {
                'users': list(rooms[room_code]['users'].values()),
                'message': leave_message
            }, room=room_code)
            
            # If no users left, delete the room
            if not rooms[room_code]['users']:
                del rooms[room_code]
    except Exception as e:
        emit('status', {'msg': f'Error leaving room: {str(e)}'})

@socketio.on('send_message')
def on_message(data):
    try:
        room_code = data['room_code']
        content = data['content']
        if room_code in rooms and request.sid in rooms[room_code]['users']:
            user_name = rooms[room_code]['users'][request.sid]
            message = {
                'type': 'user',
                'user': user_name,
                'content': content,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            rooms[room_code]['messages'].append(message)
            emit('new_message', message, room=room_code)
    except Exception as e:
        emit('status', {'msg': f'Error sending message: {str(e)}'})

def get_local_ip():
    try:
        interfaces = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
        for interface in interfaces:
            ip = interface[4][0]
            if not ip.startswith('127.'):
                return ip
    except:
        pass
    return '0.0.0.0'

if __name__ == '__main__':
    port = 8080
    local_ip = get_local_ip()
    print("\n=== Network Information ===")
    print(f"Local IP Address: {local_ip}")
    print(f"Port: {port}")
    print(f"\nTo access from your phone, use one of these URLs:")
    print(f"http://{local_ip}:{port}")
    print(f"http://localhost:{port}")
    print("========================\n")
    socketio.run(app, host='0.0.0.0', port=port, debug=True) 