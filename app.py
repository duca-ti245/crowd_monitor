from flask import Flask, render_template, Response, request, redirect, url_for, session, flash, jsonify
from camera import VideoCamera
import secrets
import os

import winsound

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Global camera instance (simple singleton for demo purposes)
# In production, this might be handled differently to avoid multi-user conflict
camera = None

def get_camera():
    global camera
    if camera is None:
        camera = VideoCamera()
    return camera

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Hardcoded credentials for demonstration
        if username == 'admin' and password == '123456':
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            # SECURITY ALERT LOGIC
            print(f"[SECURITY ALERT] FAILED LOGIN ATTEMPT: User '{username}'")
            try:
                # Play siren-like sound (high-low pattern)
                winsound.Beep(1000, 200)
                winsound.Beep(800, 200)
                winsound.Beep(1000, 200)
            except:
                pass # Ignore if sound fails (e.g. no audio device)
                
            # Flashing support requires secret_key
            flash('SYSTEM BREACH DETECTED: Invalid Credentials', 'error')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is None:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    if 'user' not in session:
        return redirect(url_for('login'))
    return Response(gen(get_camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/data')
def api_data():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    camera = get_camera()
    return jsonify({
        'count': camera.person_count,
        'status': camera.status,
        'threshold': camera.THRESHOLD,
        'trend': camera.trend,
        'last_alert': camera.last_alert_time
    })

@app.route('/toggle_heatmap')
def toggle_heatmap():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    camera = get_camera()
    camera.SHOW_HEATMAP = not camera.SHOW_HEATMAP
    return jsonify({'heatmap': camera.SHOW_HEATMAP})

if __name__ == '__main__':
    # Automatically open the browser
    import webbrowser
    from threading import Timer

    def open_browser():
        if not os.environ.get("WERKZEUG_RUN_MAIN"):
            webbrowser.open_new('http://127.0.0.1:8090/')

    Timer(1, open_browser).start()
    
    # Run the server
    # host='0.0.0.0' allows access from other devices on the network
    app.run(host='0.0.0.0', port=8090, debug=True)
