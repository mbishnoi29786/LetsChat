import os

from cs50 import SQL
from datetime import datetime, timedelta
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from cryptography.fernet import Fernet
from dotenv import load_dotenv

from helpers import apology, login_required, validate_password, validate_email, get_chat_day, allowed_file

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SECRET_KEY'] = 'ManishBishnoi!'
app.config['UPLOAD_FOLDER'] = 'static/images/profile_pictures'
socketio = SocketIO(app, cors_allowed_origins="*")
Session(app)

load_dotenv()
key = os.getenv("ENCRYPTION_KEY")
if not key:
    raise ValueError("Encryption key is missing. Set the ENCRYPTION_KEY in your .env file.")
cipher_suite = Fernet(key)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///letschat.db")

MAX_FILE_SIZE = 5 * 1024 * 1024

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET","POST"])
@login_required
def index():
    if request.method == "POST":
        user_id = session["user_id"]
        user = db.execute("""
                          SELECT username, profile_picture, account_status, status
                          FROM users
                          WHERE users.id = ?""", user_id)
        return render_template("index.html", user = user[0])

    else:
        user_id = session["user_id"]
        user = db.execute("SELECT username, profile_picture, account_status, status FROM users WHERE users.id = ?", user_id)
        # Step 1: Get all friend IDs for the logged-in user (user_id)
        friend_ids_data = db.execute("""
                                     SELECT
                                     CASE
                                        WHEN sender_id = ? THEN receiver_id
                                        WHEN receiver_id = ? THEN sender_id
                                     END AS friend_id
                                     FROM friendships
                                     WHERE (sender_id = ? OR receiver_id = ?) AND status = 'accepted';
                                     """, user_id, user_id, user_id, user_id)

        # If no friends found
        friends_details = {}
        if not friend_ids_data:
            return render_template("index.html", friends=friends_details, user=user[0])

        # Extract friend IDs
        friend_ids = [friend["friend_id"] for friend in friend_ids_data]

        # Fetch user details for all friends in one query
        friends_details = db.execute("""
                                     SELECT id, username, status, account_status, profile_picture
                                     FROM users
                                     WHERE id IN ({})
                                     """.format(",".join("?" * len(friend_ids))), *friend_ids)

        return render_template("index.html", friends= friends_details, user=user[0])


@app.route("/logout")
def logout():
    """Log user out"""

    user_id = session["user_id"]

    # Change status and last_login time before logging out
    try:
        db.execute("UPDATE users SET status = ?, last_login = ? WHERE id = ?", "offline",datetime.now(), user_id)
    except Exception as e:
        print(f"Exception: {str(e)}")

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get and Validate user inputs
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        errors = {}

        # Validation
        if not email:
            errors['email'] = "Missing email!"
        elif not validate_email(email):
            errors['email'] = "Invalid email!"

        # Ensure password was submitted
        if not password:
            errors['password'] = "Missing Password!"
        elif not validate_password(password):
            errors['password'] = "Password doesn't meet the required criteria!"


        if errors:
            return render_template("login.html", errors=errors, email=email, password=password)

        # Query database for email
        existing_user = db.execute(
            "SELECT * FROM users WHERE email = ?", email)

        # Ensure email exists and password is correct
        if not existing_user:
            errors["email"] = "Email doesn't exists!"
        else:
            for user in existing_user:
                if not check_password_hash(existing_user[0]["password_hash"], password):
                    errors["password"] = "Incorrect Password!"

        if errors:
            return render_template("login.html", errors=errors, email=email, password=password)

        try:
            db.execute("UPDATE users SET status = 'online' WHERE id = ?", existing_user[0]["id"])
        except Exception as e:
            print(f"Error {str(e)}")

        # Remember which user has logged in
        session["user_id"] = existing_user[0]["id"]
        session["username"] = existing_user[0]["username"]
        session["email"] = existing_user[0]["email"]
        session["profile_picture"] = existing_user[0].get("profile_picture")
        session["account_type"] = existing_user[0]["account_type"]
        session["csrf_token"] = os.urandom(16).hex()  # For CSRF protection
        session["ip_address"] = request.remote_addr
        session["user_agent"] = request.user_agent.string

        # Redirect user to home page
        flash("Welcome back!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Clear any existing session
    session.clear()

    if request.method == "POST":
        # Get and Validate user inputs
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirmation = request.form.get("confirmation", "").strip()

        errors = {}

        # Validation
        if not username:
            errors['username'] = "Missing username!"

        if not email:
            errors['email'] = "Missing Email!"
        elif not validate_email(email):
            errors['email'] = "Invalid email!"

        if not password:
            errors['password'] = "Missing Password!"

        if password != confirmation:
            errors['confirmation'] = "Password doesn't match!"
        elif not validate_password(password):
            errors['password'] = "Password doesn't meet the required criteria!"

        # If any errors, re-render form with errors
        if errors:
            return render_template("register.html", errors=errors, username=username, email=email, password=password, confirmation=confirmation)

        # Check for username or email conflicts
        existing_user = db.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?", username, email)

        if existing_user:
            for user in existing_user:
                if user['username'] == username:
                    errors['username'] = "Username already taken!"
                if user['email'] == email:
                    errors['email'] = "Email already registered!"

            return render_template("register.html", errors=errors, username=username, email=email, password=password, confirmation=confirmation)

        # Insert new user if no conflicts
        # Hash password
        hash_password = generate_password_hash(password)
        try:
            user_id = db.execute(
                "INSERT INTO users (username, email, password_hash, status) VALUES(?, ?, ?, 'online')", username, email, hash_password)

            session["user_id"] = user_id
            session["username"] = username
            session["email"] = email
            session["profile_picture"] = None
            session["account_type"] = "public"
            session["csrf_token"] = os.urandom(16).hex()
            session["ip_address"] = request.remote_addr
            session["user_agent"] = request.user_agent.string
            flash("Registered!")
            return redirect("/")
        except Exception as e:
            return apology(f"An error occurred: {str(e)}", 400)

    return render_template("register.html")



@app.route("/friends", methods=["GET"])
@login_required
def friends():
    user_id = session["user_id"]

    friend_ids_data = db.execute("""
                                     SELECT
                                     CASE
                                        WHEN sender_id = ? THEN receiver_id
                                        WHEN receiver_id = ? THEN sender_id
                                     END AS friend_id
                                     FROM friendships
                                     WHERE (sender_id = ? OR receiver_id = ?) AND status = 'accepted';
                                     """, user_id, user_id, user_id, user_id)


    # to extract friend IDs
    friend_ids = [friend["friend_id"] for friend in friend_ids_data]

    # to fetch user details for all friends in one query
    friends = db.execute("""
                         SELECT id, username, status, account_status, profile_picture
                         FROM users
                         WHERE id IN ({})
                         """.format(",".join("?" * len(friend_ids))), *friend_ids)

    # to get pending friend requests
    requests = db.execute("""
                          SELECT users.id, users.username, users.profile_picture, users.status
                          FROM users
                          WHERE users.id IN (
                          SELECT friendships.sender_id
                          FROM friendships
                          WHERE friendships.receiver_id = ?
                          AND status = 'pending'
                          )""", user_id)

    # Fetch users with public profiles who are not friends, not the current user, and not already in pending/accepted requests
    potential_friends = db.execute("""
                                   SELECT id, username, profile_picture, status
                                   FROM users
                                   WHERE account_type = 'public'
                                   AND id NOT IN ({})
                                   AND id != ?
                                   AND id NOT IN (
                                        SELECT sender_id
                                        FROM friendships
                                        WHERE receiver_id = ? AND status IN ('accepted', 'pending')
                                    )
                                   AND id NOT IN (
                                        SELECT receiver_id
                                        FROM friendships
                                        WHERE sender_id = ? AND status IN ('accepted', 'pending')
                                    )
                                   """.format(",".join("?" * len(friend_ids))), *friend_ids, user_id, user_id, user_id)

    return render_template("friends.html", friends=friends, requests=requests, potential_friends = potential_friends)

@app.route("/add_friend", methods=["POST"])
@login_required
def add_friend():
    if request.method == "POST":
        # Get the friend's username from the request body
        friend_username = request.json.get("friend_username", "").strip()
        user_id = session["user_id"]
        username = session["username"]

        # Validate input
        if not friend_username:
            return jsonify({"success": False, "message": "Username cannot be empty!"}), 400

        if friend_username == username:
            return jsonify({"success": False, "message": "You can't send request to yourself!"}), 400

        # Get friend's ID
        friend = db.execute("SELECT * FROM users WHERE username = ?", friend_username)
        if not friend:
            return jsonify({"success": False, "message": "User Not Found!"}), 404

        friend_id = friend[0]["id"]

        # Check if there is a rejected friendship (either as sender or receiver)
        existing_rejection = db.execute("""
                                        SELECT * FROM friendships
                                        WHERE (sender_id = ? AND receiver_id = ? AND status = 'rejected')
                                        OR (sender_id = ? AND receiver_id = ? AND status = 'rejected')
                                        """, user_id, friend_id, friend_id, user_id)

        if existing_rejection:
            # if the user by mistake rejected the request than he/she can send request again with no delay
            if existing_rejection[0]["sender_id"] != user_id:
                db.execute("""
                           DELETE FROM friendships
                           WHERE sender_id = ? AND receiver_id = ? AND status = 'rejected'
                           """, existing_rejection[0]["sender_id"], existing_rejection[0]["receiver_id"])

                # Add the new pending request by the user
                db.execute("""
                           INSERT INTO friendships (sender_id, receiver_id, status, updated_at)
                           VALUES (?, ?, 'pending', ?)
                           """, user_id, friend_id, datetime.now())

                return jsonify({"success": True, "message": "Friend request sent!"}), 200

            # If it's the user who got rejected
            # Check if enough time has passed since the rejection (24 hours)
            rejection_time = existing_rejection[0]["updated_at"]
            if rejection_time:
                time_diff = datetime.now() - datetime.strptime(rejection_time, "%Y-%m-%d %H:%M:%S")
                if time_diff < timedelta(days=1):
                    return jsonify({
                        "success": False,
                        "message": "Request rejected. Please wait 24 hours before sending a new request."
                        }), 400

                # If more than 24 hours have passed, update the status from 'rejected' to 'pending'
                db.execute("""
                           UPDATE friendships
                           SET status = 'pending', updated_at = ?
                           WHERE sender_id = ? AND receiver_id = ? AND status = 'rejected'
                           """, datetime.now(), user_id, friend_id)

                # friend request is sent again
                return jsonify({"success": True, "message": "Friend request is send again."}), 200

        # Check if the users have already become friends
        existing_friendship = db.execute("""
                                         SELECT * FROM friendships
                                         WHERE (sender_id = ? AND receiver_id = ? AND status = 'accepted')
                                         OR (receiver_id = ? AND sender_id = ? AND status = 'accepted')
                                         """, user_id, friend_id, user_id, friend_id)

        if existing_friendship:
            return jsonify({"success": False, "message": "You are already friends."}), 400

        # Check if there's an existing pending request (either direction)
        existing_pending = db.execute("""
                                      SELECT * FROM friendships
                                      WHERE (sender_id = ? AND receiver_id = ? AND status = 'pending')
                                      OR (receiver_id = ? AND sender_id = ? AND status = 'pending')
                                      """, user_id, friend_id, user_id, friend_id)

        if existing_pending:
            # If the request is in pending and the user send it.
            return jsonify({"success": False, "message": "Friend Request is in pending."}), 400

        # If there's no pending or accepted request, create a new one
        try:
            db.execute("""
                       INSERT INTO friendships (sender_id, receiver_id, status, updated_at)
                       VALUES (?, ?, 'pending', ?)
                       """, user_id, friend_id, datetime.now())
            return jsonify({"success": True, "message": "Friend request sent!"}), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"There was an error while sending friend request: {str(e)}"
                }), 500



@app.route("/friend_requests", methods=["POST"])
@login_required
def friend_request():
    sender_username = request.form.get("sender_username")
    action = request.form.get("action")
    user_id = session["user_id"]

    print(sender_username)

    # Find the sender (who sent the request) and receiver (current user)
    sender_details = db.execute("SELECT id FROM users WHERE username = ?", sender_username)
    if not sender_details:
        flash("Invalid Username.")
        return redirect("/friends")

    sender_id = sender_details[0]["id"]
    print(sender_details)
    request_data = db.execute("""
                              SELECT id
                              FROM friendships
                              WHERE sender_id = ? AND receiver_id = ?
                              AND status = 'pending'
                              """, sender_id, user_id)

    if not request_data:
        flash("Invalid request.")
        return redirect("/friends")

    friendship_request_id = request_data[0]["id"]

    print(request_data, datetime.now())
    try:
        # Start the transaction
        db.execute("BEGIN TRANSACTION;")

        if action == "accept":
            # Update the friend_requests table to mark the request as accepted
            db.execute("""
                       UPDATE friendships
                       SET status = 'accepted', updated_at = ?, accepted_at = ?
                       WHERE id = ?
                       """, datetime.now(), datetime.now(), friendship_request_id)

            flash("Friend request accepted!")

        elif action == "reject":
            # Update the request to be rejected
            db.execute("""
                       UPDATE friendships SET status = 'rejected'
                       WHERE id = ?
                       """, friendship_request_id)
            flash("Friend request rejected.")

        # Commit the transaction if everything is successful
        db.execute("COMMIT")

    except Exception as e:
        # Rollback if there's an error
        db.execute("ROLLBACK")
        flash(f"An error occurred: {str(e)}")
        return apology(f"{str(e)}", 400)

    return redirect("/friends")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]
    user = db.execute("""
        SELECT username, email, profile_picture, bio, gender, date_of_birth, account_type, account_status, status
        FROM users WHERE id = ?
    """, user_id)

    if request.method == "POST":
        # to handle the section update
        section = request.form.get("section")

        if section == "edit-profile":
            return render_template("profile/edit_profile.html", user=user[0])
        elif section == "change-profile-picture":
            return render_template("profile/change_profile_picture.html", user=user[0])
        elif section == "change-password":
            return render_template("profile/change_password.html")
        elif section == "delete-account":
            return render_template("profile/delete_account.html")

        # Get the new profile data from the form
        username = request.form.get("username")
        gender = request.form.get("gender")
        bio = request.form.get("bio")
        date_of_birth = request.form.get("date_of_birth")
        account_type = request.form.get("account_type")
        profile_picture = request.files.get("profile_picture")
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_new_password = request.form.get("confirm_new_password")
        delete_account = request.form.get("delete_account")

        # Validate Date of Birth (age must be 16 or older)
        if date_of_birth:
            dob = datetime.strptime(date_of_birth, "%Y-%m-%d")
            today = datetime.today()
            age = (today - dob).days // 365  # estimate of age in years
            if age < 16:
                flash("You must be at least 16 years old.", "error")
                return render_template("profile.html", user=user[0])

        # Username uniqueness check
        if username != user[0]['username']:
            existing_user = db.execute("SELECT * FROM users WHERE username = ?", username)
            if existing_user:
                flash("Username already exists. Please choose a different one.", "error")
                return render_template("profile.html", user=user[0])

        # Handle profile picture upload
        if profile_picture:
            if allowed_file(profile_picture.filename):
                # Read the file and check size
                file_data = profile_picture.read()
                if len(file_data) > MAX_FILE_SIZE:
                    flash("Profile picture is too large. Maximum size is 5MB.", "error")
                    return render_template("profile.html", user=user[0])
                # Rewind the file pointer before saving
                profile_picture.seek(0)

                # Save the profile picture
                filename = f"{user_id}_{secure_filename(profile_picture.filename)}"
                upload_folder = os.path.join(app.config['UPLOAD_FOLDER'])
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)  # Create the folder if it doesn't exist

                filepath = os.path.join(upload_folder, filename)
                try:
                    profile_picture.save(filepath)
                    print(f"File {filename} saved successfully.")
                except Exception as e:
                    print(f"Error saving file: {e}")
                    flash("An error occurred while uploading the file.", "error")
                    return render_template("profile.html", user=user[0])

                # Update profile picture in the database and session
                db.execute("UPDATE users SET profile_picture = ? WHERE id = ?", filename, user_id)
                session["profile_picture"] = filename
                flash("Profile Picture Updated!")
                return redirect(url_for("profile"))
            else:
                flash("Invalid file type. Only JPG, PNG, and GIF images are allowed.", "error")
                return render_template("profile.html", user=user[0])

        # Update user profile details
        if username:
            db.execute("""
                UPDATE users
                SET username = ?, gender = ?, bio = ?, date_of_birth = ?, account_type = ?
                WHERE id = ?
            """, username, gender, bio, date_of_birth, account_type, user_id)

            # update details in the session
            session["username"] = username
            session["account_type"] = account_type
            session["bio"] = bio
            session["user_gender"] = gender

        # Change password if requested
        if old_password and new_password and new_password == confirm_new_password:
            user_data = db.execute("SELECT password_hash FROM users WHERE id = ?", user_id)[0]
            if check_password_hash(user_data['password_hash'], old_password):
                new_password_hash = generate_password_hash(new_password)
                db.execute("UPDATE users SET password_hash = ? WHERE id = ?", new_password_hash, user_id)
            else:
                flash("Old password is incorrect.", "error")
                return redirect(url_for("profile"))

        # Handle account suspension (when user wants to delete account)
        if delete_account:
            db.execute("""
                UPDATE users
                SET account_status = 'deactivated', status = 'offline', account_type = 'deactivated', last_login = ?
                WHERE id = ?
            """, datetime.now(), user_id)
            session.clear()  # Clear the session to log out the user
            flash("Your account has been deactivated.", "success")
            return redirect(url_for("index"))  # Redirect to the homepage

        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    # Display user profile for GET request
    return render_template("profile.html", user=user[0])

@app.route("/load_chat", methods=["POST"])
@login_required
def load_chat():
    data = request.get_json()
    username = data.get("username")
    user_id = session["user_id"]

    friend = db.execute("SELECT * FROM users WHERE username = ?", username)
    if not friend:
        return jsonify({"error": "User not found"}), 404

    messages = db.execute("""
                          SELECT m.id, m.sender_id, m.receiver_id, m.content, m.created_at, m.is_read, m.is_delivered, u.username AS sender_username, u.profile_picture AS sender_profile_picture
                          FROM messages m
                          JOIN users u ON m.sender_id = u.id
                          WHERE (m.sender_id = ? AND m.receiver_id = ?)
                          OR (m.sender_id = ? AND m.receiver_id = ?)
                          ORDER BY m.created_at ASC
                          """, user_id, friend[0]["id"], friend[0]["id"], user_id)

    # Decrypt messages
    for message in messages:
        try:
            message["content"] = cipher_suite.decrypt(message["content"].encode()).decode()
        except Exception:
            print(f"Failed to decrypt message with ID: {message}")
            message["content"] = "[Decryption Failed]"

        # to ensure created_at is a datetime object before calling strftime
        created_at = datetime.strptime(message["created_at"], "%Y-%m-%d %H:%M:%S")

        # Format the time to 12-hour format (e.g., 3:45 PM)
        message["time"] = created_at.strftime("%I:%M %p")

        # Add the chat day (Today, Yesterday, etc.)
        message["chat_day"] = get_chat_day(created_at)

    print(messages)
    return jsonify({
        "user_id": user_id,
        "username": friend[0]["username"],
        "profile_picture": friend[0]["profile_picture"],
        "status":friend[0]["status"],
        "messages": messages
    })


@app.route('/api/get_user_info', methods=['GET'])
@login_required
def get_user_info():
    user_id = session['user_id']
    username = session['username']
    profile_picture = session['profile_picture']
    return jsonify({
        'user_id': user_id,
        'username': username,
        'profile_picture': profile_picture
        })



# Join room on chat load
@socketio.on('join_chat')
def handle_join_chat(data):
    friend_username = data["username"]
    friend = db.execute("SELECT id FROM users WHERE username = ?", friend_username)

    if not friend:
        return

    friend_id = friend[0]["id"]
    user_id = session["user_id"]
    room = f"{min(user_id, friend_id)}-{max(user_id, friend_id)}"

    join_room(room)
    emit('joined_chat', {"room": room})

# Leave room when chat is closed
@socketio.on('leave_chat')
def handle_leave_chat(data):
    leave_room(data["room"])


# Socket event for sending message
@socketio.on('send_message')
def handle_send_message(data):
    sender_id = session["user_id"]
    receiver_username = data["receiver"]
    message = data["message"]

    # Encrypt message
    encrypted_message = cipher_suite.encrypt(message.encode()).decode()

    # Fetch receiver's ID
    receiver = db.execute("SELECT id FROM users WHERE username = ?", receiver_username)
    if not receiver:
        emit('error', {'message': 'User not found'})
        return

    receiver_id = receiver[0]["id"]

    # Save message to DB
    message_id = db.execute("""
                            INSERT INTO messages (sender_id, receiver_id, content, created_at)
                            VALUES (?, ?, ?, ?)
                            """, sender_id, receiver_id, encrypted_message, datetime.now())

    print(message_id)
    # Emit message to both sender and receiver
    emit("receive_message", {
        "message_id":message_id,
        "sender": session["user_id"],
        "message": message,
        "time": datetime.now().strftime("%I:%M %p"),
        "chat_day": get_chat_day(datetime.now()),
        "senderProfilePic": session["profile_picture"],
        "senderUsername": session["username"],
        "is_read": False,
        "is_delivered": False
    }, room=f"{min(sender_id, receiver_id)}-{max(sender_id, receiver_id)}")



@socketio.on('message_read')
def handle_read_message(data):
    print(f" read data {data}")
    message_id = data['message_id']
    print(message_id)
    # Update the message status to read
    db.execute("UPDATE messages SET is_read = 1 WHERE id = ?", message_id)

    # Emit an event to notify that the message was read
    emit('message_read', {'message_id': message_id})


@socketio.on('message_delivered')
def handle_message_delivered(data):
    print(data)
    message_id = data['message_id']
    db.execute("""
        UPDATE messages
        SET is_delivered = ?
        WHERE id = ?
    """, 1, message_id)

    # emit back to the sender that the message has been delivered
    emit("message_delivered", {"message_id": message_id}, room=data['sender_room'])


