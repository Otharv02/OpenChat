# OpenChat

A real-time chat application with a classic Windows-style interface built using Flask and Socket.IO.

## Features

- **Classic Windows UI**: Retro-style interface with traditional Windows elements
- **Real-time Chat**: Instant messaging using WebSocket technology
- **Room Management**: Create and join chat rooms with unique codes
- **File Sharing**: 
  - Upload and share files in chat rooms
  - Supported formats: txt, pdf, png, jpg, jpeg, gif, doc, docx
  - 16MB file size limit
  - Automatic file cleanup when rooms are closed
- **User System**:
  - Random username generation
  - Real-time user list updates
  - Join/leave notifications
- **Message Types**:
  - Text messages
  - System notifications
  - File attachments with download links

## Setup

1. **Requirements**:
   ```
   Python 3.7+
   
   Root directory requirements:
   - Flask==3.0.0
   - Flask-SocketIO==5.3.6
   - python-socketio==5.11.1
   - python-engineio==4.8.2
   - Werkzeug==3.0.1
   
   chat_app directory requirements: (additional dependencies)
   See chat_app/requirements.txt
   ```

2. **Installation**:
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/OpenChat.git
   cd OpenChat

   # Install dependencies from root requirements.txt
   pip install -r requirements.txt

   # Change to chat_app directory and install its requirements
   cd chat_app
   pip install -r requirements.txt
   ```

3. **Running the Application**:
   
   Option 1 - Using batch file (Windows):
   ```bash
   cd OpenChat-main/chat_app
   start_chat.bat
   ```
   This will automatically install requirements and start the server.

   Option 2 - Manual start:
   ```bash
   cd chat_app
   python app.py
   ```
   The server will start on `http://localhost:8080`

## Usage

1. **Creating a Room**:
   - Visit the homepage
   - Click "Create Room"
   - Share the room code with others

2. **Joining a Room**:
   - Enter the 6-digit room code
   - Click "Join Room"

3. **Chatting**:
   - Type messages in the input field
   - Press Enter or click Send
   - Your random username will be displayed

4. **File Sharing**:
   - Click the "Attach" button
   - Select a file (supported formats only)
   - File appears in chat with download link
   - Files are automatically deleted when room closes

5. **Leaving a Room**:
   - Click "Leave Room" button
   - Or simply close the browser tab

## Technical Details

- Backend: Python Flask
- Real-time: Flask-SocketIO
- Frontend: HTML, CSS, JavaScript
- Storage: In-memory for messages, local file system for uploads
- Security: 
  - Secure filename handling
  - File type validation
  - Automatic file cleanup
  - Room validation

## Browser Support

- Chrome
- Firefox
- Edge
- Safari

## Troubleshooting

1. **Bad Request Errors (400)**:
   - Clear your browser cache and refresh the page
   - Make sure all dependencies are installed with correct versions:
     ```bash
     pip list | findstr "Flask Socket engineio Werkzeug"
     ```
   - Expected versions:
     ```
     Flask==3.0.0
     Flask-SocketIO==5.3.6
     python-socketio==5.11.1
     python-engineio==4.8.2
     Werkzeug==3.0.1
     ```

## License

MIT License - Feel free to use and modify for your own projects.