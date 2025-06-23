from PIL import Image, ImageColor
from rembg import remove
import os
import uuid

def process_image(input_path, action, background=None, bg_type=None, fill_color=None, background_folder=None, history_folder=None):
    """
    Processes the uploaded image by removing the background or replacing it
    with a background image or a solid color.

    Parameters:
    - input_path: path to the uploaded image
    - action: 'remove', 'replace_image', or 'replace_color'
    - background: file path or hex color code
    - bg_type: 'image' or 'color'
    - fill_color: optional (not used currently)
    - background_folder: path to predefined background images
    - history_folder: output folder for processed images

    Returns:
    - relative_output_path: relative path to the processed image (for Flask static route)
    """

    # Load and remove background
    original = Image.open(input_path).convert("RGBA")
    no_bg_image = remove(original).convert("RGBA")
    result = no_bg_image

    # Replace background with image
    if action == 'replace_image' and background and bg_type == 'image':
        # Use full path if uploaded, or predefined if just filename
        if os.path.isfile(background):
            bg_path = background
        else:
            bg_path = os.path.join(background_folder or 'static/background_samples', background)

        try:
            background_img = Image.open(bg_path).convert("RGBA")
            background_img = background_img.resize(result.size)
            background_img.paste(result, (0, 0), result)
            result = background_img
        except Exception as e:
            print(f"Failed to open background image: {e}")

    # Replace background with solid color
    elif action == 'replace_color' and background and bg_type == 'color':
        try:
            color = ImageColor.getrgb(background)
        except ValueError:
            color = (255, 255, 255)  # fallback to white
        solid_bg = Image.new("RGBA", result.size, color + (255,))
        solid_bg.paste(result, (0, 0), result)
        result = solid_bg

    # Save processed image
    output_filename = f"processed_{uuid.uuid4().hex}.png"
    save_folder = history_folder or 'static/history'
    os.makedirs(save_folder, exist_ok=True)
    output_path = os.path.join(save_folder, output_filename)
    result.save(output_path, format='PNG')

    # Return relative path to the processed image (for use in templates)
    return os.path.join("static", "history", output_filename)
