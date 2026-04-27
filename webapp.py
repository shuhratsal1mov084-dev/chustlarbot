from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import uuid
from auth import session_manager, require_auth
from db import db

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not session_manager.verify_session(session_id):
        return RedirectResponse(url="/login", status_code=302)
    
    players = db.get_players()
    players_html = ""
    for player in players:
        players_html += f"""
        <div class="player-card">
            <div class="player-header">
                <h3>{player['name']}</h3>
                <button class="delete-btn" onclick="deletePlayer({player['id']})">🗑️</button>
            </div>
            <p class="player-text">{player['text']}</p>
        </div>
        """
    
    if not players_html:
        players_html = '<div class="empty-state">No players yet. Add one to get started! 🎮</div>'
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PUBG Bot Admin Panel</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            html, body {{
                width: 100%;
                height: 100%;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                min-height: 100vh;
                padding: 20px;
                color: #e2e8f0;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 1px solid rgba(226, 232, 240, 0.1);
            }}
            
            .header h1 {{
                font-size: 32px;
                font-weight: 700;
                background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .logout-btn {{
                padding: 10px 20px;
                background: rgba(239, 68, 68, 0.2);
                border: 1px solid rgba(239, 68, 68, 0.5);
                color: #fca5a5;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                transition: all 0.3s ease;
            }}
            
            .logout-btn:hover {{
                background: rgba(239, 68, 68, 0.3);
                border-color: rgba(239, 68, 68, 0.7);
            }}
            
            .add-player-section {{
                background: rgba(30, 41, 59, 0.8);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(226, 232, 240, 0.1);
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 40px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }}
            
            .add-player-section h2 {{
                font-size: 20px;
                margin-bottom: 20px;
                color: #60a5fa;
            }}
            
            .form-group {{
                margin-bottom: 15px;
            }}
            
            .form-group label {{
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
                font-size: 14px;
                color: #cbd5e1;
            }}
            
            .form-group input,
            .form-group textarea {{
                width: 100%;
                padding: 12px;
                background: rgba(15, 23, 42, 0.5);
                border: 1px solid rgba(226, 232, 240, 0.2);
                border-radius: 8px;
                color: #e2e8f0;
                font-family: inherit;
                font-size: 14px;
                transition: all 0.3s ease;
            }}
            
            .form-group input:focus,
            .form-group textarea:focus {{
                outline: none;
                border-color: rgba(96, 165, 250, 0.5);
                background: rgba(15, 23, 42, 0.8);
                box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
            }}
            
            .form-group textarea {{
                resize: vertical;
                min-height: 100px;
            }}
            
            .add-btn {{
                padding: 12px 30px;
                background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
                border: none;
                color: white;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .add-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 16px rgba(96, 165, 250, 0.3);
            }}
            
            .add-btn:active {{
                transform: translateY(0);
            }}
            
            .players-section {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 20px;
            }}
            
            .player-card {{
                background: rgba(30, 41, 59, 0.8);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(226, 232, 240, 0.1);
                border-radius: 12px;
                padding: 20px;
                transition: all 0.3s ease;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }}
            
            .player-card:hover {{
                transform: translateY(-4px);
                border-color: rgba(96, 165, 250, 0.3);
                box-shadow: 0 12px 48px rgba(96, 165, 250, 0.15);
            }}
            
            .player-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 15px;
            }}
            
            .player-header h3 {{
                font-size: 18px;
                color: #60a5fa;
                word-break: break-word;
            }}
            
            .delete-btn {{
                background: rgba(239, 68, 68, 0.2);
                border: 1px solid rgba(239, 68, 68, 0.5);
                color: #fca5a5;
                padding: 6px 12px;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.3s ease;
                white-space: nowrap;
                margin-left: 10px;
            }}
            
            .delete-btn:hover {{
                background: rgba(239, 68, 68, 0.3);
                border-color: rgba(239, 68, 68, 0.7);
            }}
            
            .player-text {{
                color: #cbd5e1;
                line-height: 1.5;
                word-wrap: break-word;
            }}
            
            .empty-state {{
                grid-column: 1 / -1;
                text-align: center;
                padding: 60px 20px;
                color: #94a3b8;
                font-size: 16px;
            }}
            
            .message {{
                padding: 12px 16px;
                border-radius: 8px;
                margin-bottom: 20px;
                text-align: center;
                font-weight: 500;
            }}
            
            .message.success {{
                background: rgba(34, 197, 94, 0.2);
                border: 1px solid rgba(34, 197, 94, 0.5);
                color: #86efac;
            }}
            
            .message.error {{
                background: rgba(239, 68, 68, 0.2);
                border: 1px solid rgba(239, 68, 68, 0.5);
                color: #fca5a5;
            }}
            
            @media (max-width: 768px) {{
                .header {{
                    flex-direction: column;
                    gap: 15px;
                }}
                
                .header h1 {{
                    font-size: 24px;
                }}
                
                .players-section {{
                    grid-template-columns: 1fr;
                }}
                
                .add-player-section {{
                    padding: 20px;
                }}
                
                body {{
                    padding: 10px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎮 Admin Panel</h1>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
            
            <div id="message"></div>
            
            <div class="add-player-section">
                <h2>Add New Player</h2>
                <form onsubmit="addPlayer(event)">
                    <div class="form-group">
                        <label for="name">Player Name</label>
                        <input type="text" id="name" required placeholder="Enter player name">
                    </div>
                    <div class="form-group">
                        <label for="text">Player Description</label>
                        <textarea id="text" required placeholder="Enter player description"></textarea>
                    </div>
                    <button type="submit" class="add-btn">Add Player 🚀</button>
                </form>
            </div>
            
            <div class="players-section">
                {players_html}
            </div>
        </div>
        
        <script>
            async function addPlayer(e) {{
                e.preventDefault();
                const name = document.getElementById('name').value;
                const text = document.getElementById('text').value;
                
                try {{
                    const response = await fetch('/api/players', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{name, text}})
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok) {{
                        showMessage('Player added successfully! ✅', 'success');
                        document.getElementById('name').value = '';
                        document.getElementById('text').value = '';
                        setTimeout(() => location.reload(), 1000);
                    }} else {{
                        showMessage(data.detail || 'Error adding player', 'error');
                    }}
                }} catch (error) {{
                    showMessage('Error: ' + error.message, 'error');
                }}
            }}
            
            async function deletePlayer(id) {{
                if (confirm('Are you sure you want to delete this player?')) {{
                    try {{
                        const response = await fetch(`/api/players/${{id}}`, {{
                            method: 'DELETE'
                        }});
                        
                        if (response.ok) {{
                            showMessage('Player deleted successfully! ✅', 'success');
                            setTimeout(() => location.reload(), 1000);
                        }} else {{
                            showMessage('Error deleting player', 'error');
                        }}
                    }} catch (error) {{
                        showMessage('Error: ' + error.message, 'error');
                    }}
                }}
            }}
            
            function logout() {{
                window.location.href = '/logout';
            }}
            
            function showMessage(text, type) {{
                const msgDiv = document.getElementById('message');
                msgDiv.textContent = text;
                msgDiv.className = `message ${{type}}`;
                msgDiv.style.display = 'block';
            }}
        </script>
    </body>
    </html>
    """
    return html_content


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Login</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            html, body {
                width: 100%;
                height: 100%;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                color: #e2e8f0;
            }
            
            .login-container {
                background: rgba(30, 41, 59, 0.8);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(226, 232, 240, 0.1);
                border-radius: 16px;
                padding: 40px;
                width: 100%;
                max-width: 400px;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
            }
            
            .login-container h1 {
                font-size: 28px;
                margin-bottom: 10px;
                background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-align: center;
            }
            
            .login-container p {
                text-align: center;
                color: #cbd5e1;
                margin-bottom: 30px;
                font-size: 14px;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
                color: #cbd5e1;
            }
            
            .form-group input {
                width: 100%;
                padding: 12px;
                background: rgba(15, 23, 42, 0.5);
                border: 1px solid rgba(226, 232, 240, 0.2);
                border-radius: 8px;
                color: #e2e8f0;
                font-size: 14px;
                transition: all 0.3s ease;
            }
            
            .form-group input:focus {
                outline: none;
                border-color: rgba(96, 165, 250, 0.5);
                background: rgba(15, 23, 42, 0.8);
                box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
            }
            
            .login-btn {
                width: 100%;
                padding: 12px;
                background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
                border: none;
                color: white;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 16px;
            }
            
            .login-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 16px rgba(96, 165, 250, 0.3);
            }
            
            .login-btn:active {
                transform: translateY(0);
            }
            
            .message {
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 20px;
                text-align: center;
                font-weight: 500;
                display: none;
            }
            
            .message.error {
                background: rgba(239, 68, 68, 0.2);
                border: 1px solid rgba(239, 68, 68, 0.5);
                color: #fca5a5;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h1>🎮</h1>
            <p>Admin Panel Login</p>
            
            <div id="message" class="message"></div>
            
            <form onsubmit="handleLogin(event)">
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" required placeholder="Enter admin password" autofocus>
                </div>
                <button type="submit" class="login-btn">Login</button>
            </form>
        </div>
        
        <script>
            async function handleLogin(e) {
                e.preventDefault();
                const password = document.getElementById('password').value;
                
                try {
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({password})
                    });
                    
                    if (response.ok) {
                        window.location.href = '/';
                    } else {
                        const msgDiv = document.getElementById('message');
                        msgDiv.textContent = 'Invalid password';
                        msgDiv.className = 'message error';
                        msgDiv.style.display = 'block';
                    }
                } catch (error) {
                    const msgDiv = document.getElementById('message');
                    msgDiv.textContent = 'Error: ' + error.message;
                    msgDiv.className = 'message error';
                    msgDiv.style.display = 'block';
                }
            }
        </script>
    </body>
    </html>
    """


@app.post("/api/auth/login")
async def login(request: Request, response: Response):
    data = await request.json()
    password = data.get("password")
    
    if not password:
        raise HTTPException(status_code=400, detail="Password required")
    
    session_id = str(uuid.uuid4())
    if session_manager.create_session(session_id, password):
        response.set_cookie("session_id", session_id, httponly=True, max_age=86400)
        return {"success": True}
    
    raise HTTPException(status_code=401, detail="Invalid password")


@app.get("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id:
        session_manager.destroy_session(session_id)
    response.delete_cookie("session_id")
    return RedirectResponse(url="/login", status_code=302)


@app.post("/api/players")
async def create_player(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not session_manager.verify_session(session_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    data = await request.json()
    name = data.get("name", "").strip()
    text = data.get("text", "").strip()
    
    if not name or not text:
        raise HTTPException(status_code=400, detail="Name and text are required")
    
    if db.add_player(name, text):
        return {"success": True, "message": "Player added"}
    
    raise HTTPException(status_code=400, detail="Player already exists")


@app.delete("/api/players/{player_id}")
async def delete_player(request: Request, player_id: int):
    session_id = request.cookies.get("session_id")
    if not session_id or not session_manager.verify_session(session_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if db.delete_player(player_id):
        return {"success": True, "message": "Player deleted"}
    
    raise HTTPException(status_code=404, detail="Player not found")


@app.get("/api/players")
async def get_players(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not session_manager.verify_session(session_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return {"players": db.get_players()}
