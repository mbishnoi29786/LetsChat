# Let'sChat – Real-time Messaging with Encryption

#### Video Demo: [Let's Chat | Manish Bishnoi | GitHub: mbishnoi29786](https://youtu.be/TVvT2vOVDzE)


---

### Description:
Let'sChat is a real-time chat application built using Flask, SQLite, and Flask-SocketIO. Inspired by my CS50 coursework and a desire to understand the mechanics behind chat applications, Let'sChat allows users to connect, add friends, and engage in secure one-on-one conversations. The UI is designed to resemble popular messaging platforms like WhatsApp, providing a familiar and intuitive user experience.

In addition to real-time messaging, users can edit their profiles, change profile pictures, and manage friend lists. All user profile pictures are stored securely in a designated directory. End-to-end encryption is integrated to ensure privacy and security in communication.

---

### Features:
- **Real-time Messaging** – Powered by Flask-SocketIO for instant communication.
- **Friend System** – Users can add and manage friends to initiate private chats.
- **Profile Management** – Editable user profiles with customizable profile pictures.
- **Secure Messaging** – End-to-end encryption for all messages.
- **Responsive UI** – Familiar chat application design inspired by WhatsApp.
- **Persistent Storage** – User data and chat logs stored in SQLite.

---

### Project Structure:
``` bash
/project
├── app.py                 # Main server and route handling
├── helpers.py             # Utility functions for encryption and data processing
├── letschat.db            # SQLite database
├── requirements.txt       # Project dependencies
│
├── static/                # Static files (CSS, JS, Images)
│   ├── css/               # Page-specific CSS files
│   ├── js/                # Page-specific JavaScript files
│   └── images/            # Website images and profile pictures
│       └── profile_pictures/  # User profile images
│
├── flask_session/         # Flask session storage
│
└── templates/             # HTML templates for rendering views
    ├── layout.html        # Base layout for pages
    ├── index.html         # Chat interface (main page)
    ├── login.html         # Login page
    ├── register.html      # Registration page
    ├── friends.html       # Friends list and management
    ├── profile.html       # User profile page
    └── profile/           # Additional profile sections
```

---

## Usage Instructions:

### Download and Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mbishnoi29786/LetsChat.git
   cd LetsChat
   ```
2. **Install Dependencies**: Create and activate a virtual environment (optional but recommended):
    - On Linux/Mac:
        ```bash
        python -m venv venv
        source venv/bin/activate
        ```
    - On Windows:
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```

    - Install the required dependencies:
        ```bash
        pip install -r requirements.txt
        ```

3. **Set Up the Database**: Run the commands in letschat.txt to create the SQLite database and required tables:
```bash
sqlite3 letschat.db
```
Copy and paste the SQL commands from letschat.txt to create tables.

4. **Run the Application**: Start the Flask application:
```bash
flask run
```
Open your browser and navigate to http://127.0.0.1:5000 to start using Let'sChat.

---

## Usage Instructions:
- **Register/Login** – Users must register or log in to access the chat.
- **Add Friends** – Navigate to the friends page to add users to your friend list.
- **Start Chatting** – Click on a friend's name to initiate a private chat.
- **Edit Profile** – Visit the profile page to update personal information and change profile pictures.

---

## Technologies Used:
- **Backend:** Flask, Flask-SocketIO
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **Security:** End-to-end encryption using cryptography library

---

## Challenges and Learnings:
- Throughout the development of **Let'sChat**, I explored real-time communication protocols, encryption methods, and Flask’s session management.
- One significant challenge was implementing **Flask-SocketIO** for seamless bi-directional communication.
- Watching tutorials on creating message rooms in Flask helped me understand the nuances of WebSockets and real-time server-client interactions.

---

## Future Improvements:
- **Group Chats** – Enable users to create and join group conversations.
- **Media Sharing** – Allow file and media sharing across different social media platforms.
- **Notifications** – Implement in-app and push notifications for new messages.

---

## Credits/Acknowledgements:
- **CS50** – Fundamental learning source.
- **YouTube Tutorials** – For guidance on Flask-SocketIO implementation.
- **Flask Documentation** – Reference for Flask session and routing features.

