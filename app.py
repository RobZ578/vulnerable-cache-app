from flask import Flask, request, session, redirect, make_response, render_template_string

app = Flask(__name__)

# ⚠️ INSECURE CONFIGURATION FOR LAB PURPOSES
app.secret_key = 'insecure-secret-key'
app.config.update(
    SESSION_COOKIE_HTTPONLY=False,  # Allows JS to read the session cookie
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE="Lax"
)

# Mock user data
users = {'alice': 'alice', 'bob': 'bob', 'robel': 'robel'}
# Storage for stolen cookies
stolen_data = []

@app.route('/')
def home():
    return '''
    <h1>Lab Home</h1>
    <a href="/login">Login</a> | 
    <a href="/profile">Private Profile</a> | 
    <a href="/profile-public">Public Cached Page (VULNERABLE)</a> | 
    <a href="/collect">Attacker Log</a>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Check if user exists and password matches
        if username in users and users[username] == password:
            session['username'] = username
            # SUCCESS: Redirect to the PRIVATE profile page
            return redirect('/profile')
        return "Invalid credentials", 401
    return '''
    <form method="POST">
        <h3>Login</h3>
        <input name="username" placeholder="username">
        <input name="password" type="password" placeholder="password">
        <button type="submit">Login</button>
    </form>
    '''

@app.route('/profile')
def profile():
    # Check if the user is logged in via session
    if 'username' not in session:
        return redirect('/login')
    
    username = session['username']
    return f'''
    <h1>Private Profile</h1>
    <h2>Welcome, {username}!</h2>
    <p>Your sensitive data is safe here because this page is NOT cached by Nginx.</p>
    <hr>
    <a href="/profile-public">Go to Public Directory</a> | <a href="/">Home</a>
    '''

@app.route('/profile-public')
def profile_public():
    # VULNERABILITY: This header is reflected but NOT in the Nginx cache key
    # This remains unchanged as requested.
    poison = request.headers.get('X-Forwarded-Host', 'Default-Zone')
    
    html = f"""
    <html>
        <body>
            <h1>Public Profile</h1>
            <p>Region: {poison}</p>
            <hr>
            <p><small>This content is currently cached by Nginx.</small></p>
        </body>
    </html>
    """
    response = make_response(render_template_string(html))
    response.headers['Cache-Control'] = 'public, max-age=60'
    return response

@app.route('/collect')
def collect():
    key = request.args.get('c')
    if key:
        stolen_data.append(key)
    
    log_html = "".join([f"<li><code>{item}</code></li>" for item in stolen_data])
    return f"""
    <h1>Attacker Dashboard</h1>
    <h3>Stolen Cookies:</h3>
    <h2><ul>{log_html if stolen_data else 'No data captured yet.'}</ul></h2>
    <br><a href='/collect'>Refresh</a> | <a href='/'>Home</a>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)