# 🧪 Web Cache Poisoning → Stored XSS → Session Hijacking Lab

## 📌 Overview

This project demonstrates a sophisticated web security exploit chain:
**Web Cache Poisoning → Stored Cross-Site Scripting (XSS) → Session/Credential Hijacking**.

The vulnerability arises from an **improper cache key design** in an **Nginx reverse proxy** combined with **unsafe header reflection** in a **Flask backend**. By poisoning the shared cache, an attacker can inject malicious JavaScript that is later served to legitimate users—without any direct interaction.

---

## 🏗️ Technology Stack

* **Reverse Proxy:** Nginx (`proxy_cache`)
* **Backend Framework:** Flask (Python)
* **Templating Engine:** Jinja2
* **Containerization:** Docker & Docker Compose
* **Exploit Tools:** Python (`requests`), cURL

---

## 📁 Project Structure

```text
web-cache-poisoning-lab/
├── app.py                  # Vulnerable Flask application logic
├── exploit.py              # All-in-one exploit (poisoning + XSS + hijacking)
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── profile.html
│   ├── profile_public.html # TARGET: cache-poisoned endpoint
│   └── collect.html        # Attacker cookie exfiltration dashboard
├── nginx.conf              # Misconfigured Nginx reverse proxy
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## ⚠️ Vulnerability Analysis

### 1️⃣ Nginx Cache Key Misconfiguration

The reverse proxy is configured with an **unsafe cache key** and trusts attacker-controlled headers.

* Cache key does not normalize request headers
* Poisoned responses can be stored and reused

**Impact:**
A single malicious request can poison the cache for all users.

---

### 2️⃣ Unsafe Header Reflection (Stored XSS)

The Flask application reflects the `X-Forwarded-Host` header directly into HTML without escaping.

```python
# Vulnerable code snippet (app.py)
region = request.headers.get('X-Forwarded-Host', 'Global')
return render_template('profile_public.html', region=region)
```

**Impact:**
Injected JavaScript becomes persistent once cached.

---

### 3️⃣ Missing Cookie Security Flags

Session cookies are not protected with `HttpOnly`.

* JavaScript can read cookies via `document.cookie`
* Enables session hijacking after XSS

**Impact:**
Full account compromise.

---

## ⚔️ Attack Flow

1. **Poisoning** – Attacker sends a request with a malicious script in `X-Forwarded-Host`
2. **Storage** – Nginx caches the poisoned response
3. **Victim Access** – A legitimate user visits `/profile-public`
4. **Execution** – The cached JavaScript executes in the browser
5. **Exfiltration** – Session cookie is sent to `/collect`

---

## 🚀 Installation & Setup

### ✅ Prerequisites

Ensure the following are installed:

* Docker
* Docker Compose
* Python 3.x (for running the exploit)

Verify:

```bash
docker --version
docker-compose --version
python3 --version
```

---

### 📥 Clone the Repository

```bash
git clone https://github.com/RobZ578/vulnerable-cache-app.git
cd vulnerable-cache-app
```

---

### 🐳 Build and Run the Lab

From the project root directory:

```bash
docker-compose up --build
```

This will:

* Build the Flask application container
* Start Nginx as a reverse proxy
* Expose the application on **port 8080**

---

## 🌐 Access the Application

| Service        | URL                                                                          |
| -------------- | ---------------------------------------------------------------------------- |
| Home Page      | [http://localhost:8080](http://localhost:8080)                               |
| Login          | [http://localhost:8080/login](http://localhost:8080/login)                   |
| Public Profile | [http://localhost:8080/profile-public](http://localhost:8080/profile-public) |
| Attacker Panel | [http://localhost:8080/collect](http://localhost:8080/collect)               |

---

## 👤 Test Accounts

| Username | Password |
| -------- | -------- |
| alice    | alice    |
| bob      | bob      |
| robel    | robel    |

---

## ☠️ Running the Exploit (PoC)

In a **new terminal (outside Docker)**:

```bash
python3 exploit.py
```

### Expected Behavior

* Cache is poisoned using a malicious header
* Stored XSS becomes active on `/profile-public`
* Victim session cookies appear at:

```
http://localhost:8080/collect
```

---

## 🛑 Stopping the Lab

```bash
docker-compose down
```

To remove cached data completely:

```bash
docker-compose down -v
```

---

## 🛡️ Detailed Mitigation Guide

Security must be enforced at **multiple layers**.

---

### 1️⃣ Infrastructure (Nginx)

**Fix cache key hygiene:**

```nginx
proxy_cache_key "$scheme$proxy_host$request_uri";
```

**Sanitize forwarded headers:**

```nginx
proxy_set_header X-Forwarded-Host "";
proxy_set_header Host $host;
```

---

### 2️⃣ Application (Flask / Jinja2)

**Context-aware output encoding:**

```html
<p>Your Current Region: {{ region | e }}</p>
```

**Input validation:**
Allow-list expected header values.

---

### 3️⃣ Session Security (Cookies)

```python
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,  # Requires HTTPS
    SESSION_COOKIE_SAMESITE='Lax',
)
```

---

### 4️⃣ Content Security Policy (CSP)

Deploy a CSP header to block inline scripts and prevent injected JavaScript execution.

---

## ⚖️ Educational Disclaimer

⚠️ **This project is strictly for educational and research purposes.**

It demonstrates how small misconfigurations can lead to critical security vulnerabilities.
**Do NOT deploy these configurations in production environments.**

---
