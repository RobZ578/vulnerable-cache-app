# Web Cache Poisoning


## 📌 Overview
This project demonstrates a sophisticated web security exploit chain: **Web Cache Poisoning** escalating into **Stored Cross-Site Scripting (XSS)**, and culminating in **Session/Credential Hijacking**.

The vulnerability arises from an improper cache key design in an Nginx reverse proxy combined with unsafe header reflection in a Flask backend. By manipulating the cache, an attacker can serve a malicious payload to legitimate users without ever interacting with them directly.



---

## 🏗️ Technology Stack
* **Reverse Proxy:** Nginx (configured with `proxy_cache`)
* **Backend Framework:** Flask (Python)
* **Templating Engine:** Jinja2
* **Containerization:** Docker & Docker Compose
* **Exploit Tools:** Python (Requests), cURL

---

## 📁 Project Structure
```text
web-cache-poisoning-lab/
├── app.py                # Vulnerable Flask application logic
├── exploit.py            # ALL-IN-ONE exploit script (Poisoning + XSS + Hijacking)
├── templates/            # Frontend Jinja2 templates
│   ├── base.html         # Main layout
│   ├── login.html        # Login form
│   ├── home.html         # Home page
│   ├── profile.html      # Profile page
│   ├── profile_public.html # TARGET: The cache-poisoned endpoint
│   └── collect.html      # Attacker's cookie exfiltration dashboard
├── nginx.conf            # Misconfigured Nginx reverse proxy
├── Dockerfile            # Container definition
└── docker-compose.yml    # Multi-container orchestration

___


⚠️ Vulnerability Analysis
1. Nginx Cache Key Misconfiguration
The proxy is configured to trust the X-Forwarded-Host header. Because this header is included in the cache key but not validated, an attacker can create a "unique" poisoned entry in the cache.

2. Unsafe Header Reflection
The Flask application reads the X-Forwarded-Host header and renders it directly into the HTML template without escaping.

Python

# Vulnerable Code Snippet in app.py
region = request.headers.get('X-Forwarded-Host', 'Global')
return render_template('profile_public.html', region=region)
3. Missing Cookie Security
The session cookies lack the HttpOnly flag. This is the final "green light" for the attacker, as it allows JavaScript (document.cookie) to access sensitive session identifiers once XSS is achieved.

⚔️ Attack Flow
The Poisoning: The attacker sends a request with a malicious script in the X-Forwarded-Host header.

The Storage: Nginx sees a "new" version of the page and caches it because the X-Forwarded-Host is part of the cache key.

The Victim: A legitimate user visits the public profile. Nginx serves the cached version containing the attacker's script.

The Exfiltration: The script runs in the user's browser, stealing their cookie and sending it to the attacker's /collect endpoint.

🚀 Getting Started
Prerequisites
Docker and Docker Compose installed.

Python 3.x (for running the exploit script).

Installation & Execution
Clone and Build:

Bash

'''docker-compose up --build'''
Access the Application:

App URL: http://localhost:8080

Attacker Dashboard: http://localhost:8080/collect

Running the Exploit
The provided exploit.py is a centralized script designed to automate the entire attack chain. It performs all three phases in a single execution:

Stage 1: Injects the payload via X-Forwarded-Host to poison the Nginx cache.

Stage 2: Confirms the Stored XSS is active on the /profile-public endpoint.

Stage 3: Prepares the listener to receive and display hijacked session cookies.

To run the full exploit:

Bash

python3 exploit.py
🛡️ Detailed Mitigation Guide
To secure this environment, defenses must be implemented at the infrastructure, application, and browser levels.

1. Infrastructure (Nginx)
The primary goal is to ensure that unvalidated input cannot influence the cache key.

Restrict Cache Keys: Avoid using request headers in the proxy_cache_key. A secure key should only use internal, immutable variables.

Nginx

# SECURE CONFIG
proxy_cache_key "$scheme$proxy_host$request_uri";
Header Sanitization: Strip sensitive or untrusted headers before passing the request to the backend.

Nginx

proxy_set_header X-Forwarded-Host "";
proxy_set_header Host $host;
2. Application (Flask/Jinja2)
The application must treat all headers as untrusted user input.

Context-Aware Output Encoding: Ensure Jinja2 is configured to auto-escape, or manually use the escape filter for reflected values.

HTML

<p>Your Current Region: {{ region | e }}</p>
Input Validation: Validate headers against an allow-list of expected values before processing.

3. Session Security (Cookies)
Implement "defense in depth" to prevent credential theft even if an XSS vulnerability exists.

HttpOnly Flag: Prevents JavaScript from accessing the cookie via document.cookie.

Python

# SECURE FLASK SESSION CONFIG
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True, # Requires HTTPS
    SESSION_COOKIE_SAMESITE='Lax',
)
4. Content Security Policy (CSP)
Implement a CSP header to restrict where scripts can be loaded from and prevent the execution of inline scripts injected by an attacker.

⚖️ Educational Disclaimer
This project is intended strictly for educational and academic purposes. It demonstrates how misconfigurations lead to critical vulnerabilities. Do not deploy these configurations in a production environment. Unauthorized access to computer systems is illegal.