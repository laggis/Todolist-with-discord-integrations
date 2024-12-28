from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
db = SQLAlchemy(app)

# Get Discord webhook URLs
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
DISCORD_ARCHIVE_WEBHOOK_URL = os.getenv('DISCORD_ARCHIVE_WEBHOOK_URL')

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')  # pending, working, completed, blocked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def get_status_emoji(status):
    status_emojis = {
        'pending': '⏳',
        'working': '🔨',
        'completed': '✅',
        'blocked': '🚫'
    }
    return status_emojis.get(status, '❓')

def get_status_color(status):
    status_colors = {
        'pending': 0xFFA500,  # Orange
        'working': 0x3498DB,  # Blue
        'completed': 0x2ECC71,  # Green
        'blocked': 0xE74C3C   # Red
    }
    return status_colors.get(status, 0x95A5A6)  # Default gray

def send_discord_notification(message, todo=None, use_archive=False):
    webhook_url = DISCORD_ARCHIVE_WEBHOOK_URL if use_archive else DISCORD_WEBHOOK_URL
    if webhook_url:
        webhook_url = webhook_url.replace('discordapp.com', 'discord.com')
        
        status_emoji = get_status_emoji(todo.status) if todo else "📋"
        color = get_status_color(todo.status) if todo else 0x7289DA
        current_time = datetime.utcnow().isoformat()
        
        data = {
            "embeds": [
                {
                    "title": f"{status_emoji} TODO List Update",
                    "description": message,
                    "color": color,
                    "author": {
                        "name": "Task Manager",
                        "icon_url": "https://i.imgur.com/AfFp7pu.png"
                    },
                    "thumbnail": {
                        "url": "https://i.imgur.com/AfFp7pu.png"
                    },
                    "fields": [],
                    "timestamp": current_time,
                    "footer": {
                        "text": "Task Manager Bot",
                        "icon_url": "https://i.imgur.com/AfFp7pu.png"
                    }
                }
            ]
        }
        
        if todo:
            created_time = todo.created_at.strftime('%Y-%m-%d %H:%M') if todo.created_at else "N/A"
            data["embeds"][0]["fields"] = [
                {"name": "📌 Task", "value": f"**{todo.title}**", "inline": True},
                {"name": "🔄 Status", "value": f"{status_emoji} {todo.status.capitalize()}", "inline": True},
                {"name": "⏰ Created", "value": created_time, "inline": True}
            ]
            if todo.description:
                data["embeds"][0]["fields"].append(
                    {"name": "📝 Description", "value": todo.description}
                )
        
        try:
            requests.post(webhook_url, json=data)
        except Exception as e:
            print(f"Error sending Discord notification: {e}")

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return render_template('index.html', todos=todos)

@app.route('/add_todo', methods=['POST'])
def add_todo():
    title = request.form.get('title')
    description = request.form.get('description')
    
    if title:
        todo = Todo(title=title, description=description)
        db.session.add(todo)
        db.session.commit()
        send_discord_notification("🆕 New task added!", todo)
    
    return redirect(url_for('index'))

@app.route('/update_status/<int:todo_id>', methods=['POST'])
def update_status(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    new_status = request.form.get('status')
    old_status = todo.status
    
    valid_statuses = ['pending', 'working', 'completed', 'blocked']
    if new_status in valid_statuses:
        todo.status = new_status
        db.session.commit()
        
        status_emoji = get_status_emoji(new_status)
        message = f"Task status changed from {old_status} to {new_status}"
        
        # Send to archive channel if marked as completed
        use_archive = new_status == 'completed'
        send_discord_notification(f"{status_emoji} {message}", todo, use_archive)
    
    return redirect(url_for('index'))

@app.route('/delete_todo/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    title = todo.title
    description = todo.description
    temp_todo = Todo(title=title, description=description, status="deleted")
    
    db.session.delete(todo)
    db.session.commit()
    
    # Send deletion notification to archive channel
    send_discord_notification("🗑️ Task deleted!", temp_todo, use_archive=True)
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
