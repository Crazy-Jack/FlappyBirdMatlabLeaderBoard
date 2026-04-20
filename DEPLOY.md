# FlappyBird Leaderboard - Deployment Guide

## Overview

The FlappyBird leaderboard is a Django web application for CMU 15-386/686 that allows students to upload their trained neural network `.mat` files and compete on a public leaderboard.

The app is configured to run behind a reverse proxy (e.g., Caddy or Nginx) at the `/flappybird` sub-path.

---

## Prerequisites

- Python 3.9+
- A reverse proxy (Caddy or Nginx) with HTTPS
- (Optional) MySQL if you want to switch from SQLite

---

## Quick Deploy Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Crazy-Jack/FlappyBirdMatlabLeaderBoard.git
cd FlappyBirdMatlabLeaderBoard/flappy
```

### 2. Create Virtual Environment & Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install "Django>=3.0,<4.0" gunicorn scipy cryptography Pillow
```

### 3. Initialize the Database

```bash
python manage.py migrate
```

This creates an SQLite database (`db.sqlite3`) with all required tables.

### 4. Create an Admin User (Optional)

```bash
python manage.py createsuperuser
```

### 5. Start the Application with Gunicorn

```bash
gunicorn --bind 127.0.0.1:8001 flappy.wsgi:application
```

The app listens on `127.0.0.1:8001` and expects to be served behind a reverse proxy at the `/flappybird` path.

---

## Reverse Proxy Configuration

### Option A: Caddy

Add this to your `Caddyfile`:

```
yourdomain.com {
    # Static files - served directly by Caddy for performance
    handle /flappybird/static/* {
        uri strip_prefix /flappybird
        root * /path/to/FlappyBirdMatlabLeaderBoard/flappy
        file_server
    }
    handle /flappybird/media/* {
        uri strip_prefix /flappybird
        root * /path/to/FlappyBirdMatlabLeaderBoard/flappy
        file_server
    }
    # Dynamic requests - proxy to Django
    handle /flappybird* {
        reverse_proxy 127.0.0.1:8001
    }
}
```

Make sure Caddy has read access to the static files:

```bash
chmod o+x /home/youruser /path/to/FlappyBirdMatlabLeaderBoard /path/to/FlappyBirdMatlabLeaderBoard/flappy /path/to/FlappyBirdMatlabLeaderBoard/flappy/static
```

### Option B: Nginx

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    location /flappybird/static/ {
        alias /path/to/FlappyBirdMatlabLeaderBoard/flappy/static/;
    }
    location /flappybird/media/ {
        alias /path/to/FlappyBirdMatlabLeaderBoard/flappy/media/;
    }
    location /flappybird/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## How the Sub-Path Deployment Works

The app uses a WSGI middleware wrapper (`flappy/wsgi.py`) that:

1. Sets `SCRIPT_NAME = '/flappybird'` for all requests
2. Strips the `/flappybird` prefix from `PATH_INFO` before Django's URL resolver processes it
3. Django's `{% url %}` and `{% static %}` template tags automatically prepend `/flappybird` to all generated URLs

This means all internal links, redirects, and static file paths include the `/flappybird` prefix, while Django's URL patterns remain unchanged.

---

## Running as a Systemd Service (Production)

Create `/etc/systemd/system/flappybird.service`:

```ini
[Unit]
Description=FlappyBird Leaderboard (Gunicorn)
After=network.target

[Service]
User=youruser
Group=yourgroup
WorkingDirectory=/path/to/FlappyBirdMatlabLeaderBoard/flappy
ExecStart=/path/to/FlappyBirdMatlabLeaderBoard/flappy/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8001 \
    flappy.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl enable flappybird
sudo systemctl start flappybird
```

---

## Student Instructions

### Registering

1. Visit `https://yourdomain.com/flappybird/`
2. Click the **Sign In** icon in the top-right corner
3. Register with your **CMU Andrew email** and a password (8+ characters)

### Submitting a Model

1. Log in and click **Submit** in the navigation bar
2. Select a **Category** (1, 2, or 3)
3. Enter your **YouTube Video ID** (e.g., from `https://www.youtube.com/watch?v=XXXXXXXXX`, the ID is `XXXXXXXXX`)
4. Enter the **Number of Parameters** in your model
5. Upload your `nn.mat` file
6. Click **Submit**

The system will automatically extract your training stats (`trainTime`, `EPISODES`, `deaths`, `highScore`) from the `.mat` file and add your entry to the leaderboard.

### Enabling YouTube Video Embedding

Your video **must** allow embedding, otherwise it will show **Error 153** on the leaderboard:

1. Go to [YouTube Studio](https://studio.youtube.com)
2. Click **Content** from the left menu
3. Find your video and click **Details** (pencil icon)
4. Scroll down and click **Show More**
5. Under **License and rights ownership**, check **"Allow embedding"**
6. Click **Save**
7. Make sure your video is set to **"Not made for kids"** (Settings -> Audience)

---

## File Structure

```
flappy/
├── flappy/              # Django project settings
│   ├── settings.py      # DB, static files, middleware config
│   ├── wsgi.py          # WSGI with /flappybird SCRIPT_NAME wrapper
│   ├── urls.py          # Root URL configuration
│   └── __init__.py
├── tools/               # Leaderboard app
│   ├── views.py         # Upload, login, register, leaderboard views
│   ├── models.py        # SubmissionTable model
│   ├── forms.py         # Upload form
│   ├── urls.py          # URL patterns for tools app
│   └── templates/       # HTML templates
├── information/         # Info pages app
├── static/              # CSS, JS, images
├── media/               # Uploaded .mat files
├── templates/           # Base template
└── manage.py
```

---

## Switching to MySQL (Optional)

If you prefer MySQL over SQLite, modify `flappy/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'flappybird',
        'USER': 'bird_agent',
        'PASSWORD': 'your_password',
        'HOST': '127.0.0.1',
        'PORT': 3306,
    }
}
```

Also restore `flappy/__init__.py`:

```python
import pymysql
pymysql.install_as_MySQLdb()
```

And install pymysql: `pip install pymysql`
