from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import string
import json
from datetime import datetime
import socket
import os
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_room_files(room_code):
    """Clean up all files associated with a room"""
    try:
        room_files = []
        if room_code in rooms:
            # Get all files from room messages
            for message in rooms[room_code]['messages']:
                if message['type'] == 'file':
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], message['content'])
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        room_files.append(message['content'])
        
        print(f"Cleaned up {len(room_files)} files from room {room_code}")
        return room_files
    except Exception as e:
        print(f"Error cleaning up room files: {str(e)}")
        return []

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

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        room_code = request.form.get('room_code')
        
        if not file or not file.filename:
            return jsonify({'error': 'No file selected'}), 400
            
        if not room_code or room_code not in rooms:
            return jsonify({'error': 'Invalid room'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        # Create uploads directory if it doesn't exist
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        filename = secure_filename(file.filename)
        # Add timestamp and room code to filename to make it unique and trackable
        filename = f"{room_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Get user info from session ID
        sid = request.environ.get('HTTP_X_SOCKET_ID') or request.environ.get('HTTP_SID')
        user_name = rooms[room_code]['users'].get(sid, 'Unknown User')
        
        # Create file message
        message = {
            'type': 'file',
            'user': user_name,
            'content': filename,
            'original_name': file.filename,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        
        rooms[room_code]['messages'].append(message)
        socketio.emit('new_message', message, room=room_code)
        
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        return str(e), 404

@socketio.on('join')
def on_join(data):
    try:
        room_code = data.get('room_code')
        user_name = data.get('user_name')  # Get username if provided
        
        if room_code not in rooms:
            return
        
        # If user already exists in room with different session, remove old session
        old_sid = None
        for sid, name in rooms[room_code]['users'].items():
            if name == user_name:
                old_sid = sid
                break
        if old_sid:
            del rooms[room_code]['users'][old_sid]
        
        # Generate a random name for the user if they don't have one
        if not user_name or request.sid not in rooms[room_code]['users']:
            user_name = user_name or generate_random_name()
            rooms[room_code]['users'][request.sid] = user_name
            join_room(room_code)
            
            # Send system message about new user
            message = {
                'type': 'system',
                'content': f'{user_name} joined the room',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            rooms[room_code]['messages'].append(message)
        else:
            # User rejoining with same name
            rooms[room_code]['users'][request.sid] = user_name
            join_room(room_code)
            
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
            
            # If no users left, delete the room and cleanup files
            if not rooms[room_code]['users']:
                cleanup_room_files(room_code)
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