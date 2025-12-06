# NeoRadio - Local Development Environment

A Flask-based web server with SQLite database for local prototyping.

## Setup

### 1. Activate Virtual Environment

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
python app.py
```

The server will start at: http://127.0.0.1:5000

## Features

- Flask web framework
- SQLite database (no separate database server needed)
- RESTful API endpoints
- Automatic database initialisation
- Interactive web UI for testing

## Development

The server runs in debug mode, which means:
- Auto-reloads when you change code
- Detailed error messages
- Interactive debugger in the browser

To modify the database schema, edit the `init_db()` function in `app.py`.

## Next Steps

- Add more API endpoints as needed
- Create additional database tables
- Build out your frontend in `templates/`
- Add authentication if needed
- Customize for your specific use case
