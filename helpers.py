import re

from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime, timedelta

# Allowed image file types
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*()_+=\-[\]{};':\"\\|,.<>?/]", password):
        return False
    return True

# references https://stackoverflow.com/questions/46155/how-can-i-validate-an-email-address-in-javascript
def validate_email(email):
    pattern = r"^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
    return re.match(pattern, email)


def get_chat_day(datetimeObj):
    # Get the current date
    today = datetime.today()
    yesterday = today - timedelta(days=1)

    # Check if the message is from today or yesterday
    if datetimeObj.date() == today.date():
        return "Today"
    elif datetimeObj.date() == yesterday.date():
        return "Yesterday"
    else:
        # If not today or yesterday, return the full date
        return datetimeObj.strftime("%b %d, %Y")  # e.g., "Dec 29, 2024"



def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
