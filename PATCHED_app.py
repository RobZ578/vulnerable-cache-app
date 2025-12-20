from flask import (
    Flask,
    request,
    session,
    redirect,
    make_response,
    render_template
)
from datetime import datetime

app = Flask(__name__)

# 🔐 SECURE CONFIGURATION
app.secret_key = 'use-a-strong-random-secret-key'
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,    # JS CANNOT read cookies
    SESSION_COOKIE_SECURE=True,      # HTTPS only
    SESSION_COOKIE_SAMESITE="Strict"
)

# Mock user data
users = {
    'alice': 'alice',
    'bob': 'bob',
    'robel': 'robel'
}

# Storage for stolen cookies (lab only — REMOVE in prod)
stolen_data = []


# =====================
# HOME
# =====================
@app.route('/')
def home():
    return render_template('home.html')


# =====================
# LOGIN
# =====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username] == password:
            session['username'] = username
            return redirect('/profile')

        return "Invalid credentials", 401

    return render_template('login.html')


# =====================
# PRIVATE PROFILE
# =====================
@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect('/login')

    return render_template(
        'profile.html',
        username=session['username']
    )


# =====================
# PUBLIC PROFILE (FIXED)
# =====================
@app.route('/profile-public')
def profile_public():

    response = make_response(
        render_template(
            'profile_public.html',
            region="Default-Zone"
        )
    )

    # 🚫 Explicitly disable caching
    response.headers['Cache-Control'] = 'no-store'
    return response


# =====================
# COLLECTOR (REMOVED / HARDENED)
# =====================
@app.route('/collect', methods=['GET'])
def collect():
    """
    ⚠ Lab endpoint removed in secure version
    """
    return "Not Found", 404


# =====================
# APP ENTRY
# =====================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
