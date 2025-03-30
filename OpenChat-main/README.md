# OpenChat

A real-time chat application built with Python Flask and Socket.IO that allows users to create and join chat rooms for instant messaging.

## Features

- Create and join chat rooms
- Real-time messaging
- Simple and intuitive user interface
- Multiple users can chat simultaneously
- Cross-browser compatibility

## Requirements

- Python 3.x
- Flask
- Flask-SocketIO
- eventlet

## Installation

1. Clone the repository
2. Navigate to the project directory:
   ```
   cd OpenChat-main/chat_app
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Double-click on `start_chat.bat` or run:
   ```
   python app.py
   ```
2. Open your web browser and navigate to `http://localhost:5000`
3. Create or join a chat room and start chatting!

## Project Structure

```
chat_app/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── start_chat.bat     # Windows startup script
└── templates/         # HTML templates
    ├── index.html    # Home page
    └── room.html     # Chat room page
```

## License

This project is open source and available under the MIT License.