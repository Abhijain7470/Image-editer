from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os
from werkzeug.utils import secure_filename
from utils.image_utils import process_image  # Custom function for image editing
import uuid

# initialize flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key' #Needed for session managemenr (can be changed)

#configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'                  # Where uploaded images are stored\app.config['HISTORY_FOLDER'] = 'static/history'               # Where processed images are saved
app.config['HISTORY_FOLDER'] = 'static/history'
app.config['BACKGROUND_FOLDER'] = 'static/background_samples'   # Predefined backgrounds
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}       # Allowed file types

#Dummy user for now
DUMMY_USER = {
    'username': 'John Doe',
    'email': 'john@example.com'
}

# Utility to check allowed extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# -------------------- ROUTES --------------------

@app.route('/')
def index():
    return redirect(url_for('dashboard'))


# 1. Home Page Route
@app.route('/dashboard')
def dashboard():
    session['username'] = DUMMY_USER['username']
    session['email'] = DUMMY_USER['email']
    return render_template(
        'dashboard.html',
        username=session['username'],
        email=session['email']
    )

# 2. Replace Background Page
@app.route('/replace_background')
def replace_background():
    """
    Displays the home page where user can upload image,
    choose to remove/replace background, and view background options.
    """
    background_images = os.listdir(app.config['BACKGROUND_FOLDER'])
    return render_template('replace_background.html', backgrounds=background_images,
                           username=session.get('username'), email=session.get('email'))


# 3. Upload Background Page
@app.route('/upload_background', methods=['GET', 'POST'])
def upload_background():
    if request.method == 'POST':
        if 'background_image' not in request.files:
            return redirect(request.url)

        file = request.files['background_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['BACKGROUND_FOLDER'], filename)
            file.save(save_path)
            return redirect(url_for('upload_background'))

    uploaded_backgrounds = os.listdir(app.config['BACKGROUND_FOLDER'])
    return render_template('upload_background.html', backgrounds=uploaded_backgrounds,
                           username=session.get('username'), email=session.get('email'))




# 4. Image Processing Route
@app.route('/process', methods=['POST'])
def process():
    if 'image' not in request.files:
        return redirect(request.url)

    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)

        # Get action and background
        action = request.form.get('action')
        bg_type = request.form.get('bg_type')
        selected_bg = request.form.get('background')
        background_path = None

        # Handle uploaded background image if any
        if action == 'replace_image':
            bg_file = request.files.get('background_image')
            if bg_file and allowed_file(bg_file.filename):
                bg_filename = secure_filename(bg_file.filename)
                unique_bg_name = f"{uuid.uuid4().hex}_{bg_filename}"
                bg_filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_bg_name)
                bg_file.save(bg_filepath)
                background_path = bg_filepath
                bg_type = 'image'
            else:
                background_path = selected_bg
                bg_type = 'image'
        elif action == 'replace_color':
            background_path = request.form.get('background_color')
            bg_type = 'color'

        # Call your custom image processor
        output_path = process_image(
            input_path=filepath,
            action=action,
            background=background_path,
            bg_type=bg_type,
            history_folder=app.config['HISTORY_FOLDER'],
            background_folder=app.config['BACKGROUND_FOLDER']
        )

        relative_output = os.path.relpath(output_path, app.static_folder).replace('\\', '/')
        return render_template('result.html', output_image=relative_output,
                               username=session.get('username'), email=session.get('email'))

    return redirect(url_for('replace_background'))


# 5. History Page
@app.route('/history')
def history():
    images = os.listdir(app.config['HISTORY_FOLDER'])
    return render_template('history.html', images=images,
                           username=session.get('username'), email=session.get('email'))


# 6. Serve Uploaded Files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 7. logout for user
@app.route('/logout/')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('dashboard'))


# ------------------ MAIN ENTRY ------------------
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['HISTORY_FOLDER'], exist_ok=True)
    os.makedirs(app.config['BACKGROUND_FOLDER'], exist_ok=True)
    app.run(debug=True)