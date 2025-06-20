from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from utils.image_utils import process_image  # Custom function for image editing
import uuid

# initialize flask app
app = Flask(__name__)

#configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'                  # Where uploaded images are stored\app.config['HISTORY_FOLDER'] = 'static/history'               # Where processed images are saved
app.config['HISTORY_FOLDER'] = 'static/history'
app.config['BACKGROUND_FOLDER'] = 'static/background_samples'   # Predefined backgrounds
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}       # Allowed file types

# Utility to check allowed extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# -------------------- ROUTES --------------------

# 1. Home Page Route
@app.route('/')
def index():
    """
    Displays the home page where user can upload image,
    choose to remove/replace background, and view background options.
    """
    background_images = os.listdir(app.config['BACKGROUND_FOLDER'])
    return render_template('index.html', backgrounds=background_images)


# 2. Image Processing Route
@app.route('/process', methods=['POST'])
def process():
    """
    Handles image upload and calls process_image()
    for background removal or replacement (image or color).
    """
    if 'image' not in request.files:
        return redirect(request.url)
    
    file = request.files['image']
    if file and allowed_file(file.filename):
        # Save uploaded main image with a unique name
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)

        # Get action and background type
        action = request.form.get('action')             # 'remove', 'replace_image', 'replace_color'
        bg_type = request.form.get('bg_type')           # 'image' or 'color'
        selected_bg = request.form.get('background')    # used for predefined image or color hex

        background_path = None  # Default to None

        # Handle uploaded background image if action is 'replace_image'
        if action == 'replace_image':
            bg_file = request.files.get('background_image')
            if bg_file and allowed_file(bg_file.filename):
                bg_filename = secure_filename(bg_file.filename)
                unique_bg_name = f"{uuid.uuid4().hex}_{bg_filename}"
                bg_filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_bg_name)
                bg_file.save(bg_filepath)

                background_path = bg_filepath  # full path to uploaded background
                bg_type = 'image'
            else:
                # fallback to selected predefined background
                background_path = selected_bg
                bg_type = 'image'

        elif action == 'replace_color':
            background_path = request.form.get('background_color')  # hex value
            bg_type = 'color'

        # Process the image
        output_path = process_image(
            input_path=filepath,
            action=action,
            background=background_path,
            bg_type=bg_type,
            history_folder=app.config['HISTORY_FOLDER'],
            background_folder=app.config['BACKGROUND_FOLDER']
        )

        # Return relative path to the image (inside /static/history/)
        relative_output = os.path.relpath(output_path, app.static_folder).replace('\\', '/')
        return render_template('result.html', output_image=relative_output)

    return redirect(url_for('index'))


# 3. History Page
@app.route('/history')
def history():
    """
    Displays a gallery of previously processed images from the history folder.
    """
    images = os.listdir(app.config['HISTORY_FOLDER'])
    return render_template('history.html', images=images)


# 4. Show Processed Result Page
#@app.route('/result/<filename>')
#def result(filename):
 #   return render_template('result.html', filename=filename)


# 5. Serve Uploaded Files (Optional)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Serves uploaded files from the uploads folder.
    Useful for displaying them on the frontend.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ------------------ MAIN ENTRY ------------------
if __name__ == '__main__':
    # Ensure necessary folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['HISTORY_FOLDER'], exist_ok=True)
    os.makedirs(app.config['BACKGROUND_FOLDER'], exist_ok=True)

    # Run Flask app
    app.run(debug=True)