from PIL import Image, ImageColor
from rembg import remove
import os
import uuid
import io

def process_image(input_path, action, background=None, bg_type=None, fill_color=None, background_folder=None, history_folder=None):
    """
    Processes the uploaded image by removing the background or replacing it
    with either a new background image or a solid color.

    Parameters:
    - input_path: path to the uploaded image
    - action: 'remove', 'replace_image', or 'replace_color'
    - background: filename of background image or hex color code
    - bg_type: 'image' or 'color'
    - fill_color: optional solid color (used if bg_type is 'color')
    - background_folder: directory containing background images
    - history_folder: where to save the processed output

     Returns:
    - relative_output_path: relative URL path to the processed image for Flask
    """

    # Load original image
    original = Image.open(input_path).convert("RGBA")

    # Step 1: Remove background
    no_bg_image = remove(original).convert("RGBA")
    result = no_bg_image

    # Step 2: Replace with image or color background
    if action == 'replace_image' and background and bg_type == 'image':
        # Determine if background is a path or a filename
        if os.path.isfile(background):      # It's a full path (uploaded background)
            bg_path = background
        else:   # It's a predefined filename
            bg_path = os.path.join(background_folder or 'static/background_samples',background)

        try:
            background_img = Image.open(bg_path).convert("RGBA")
            background_img = background_img.resize(result.size)
            background_img.paste(result, (0, 0), result)
            result = background_img
        except Exception as e:
            print(f"Failed to open background image: {e}")

    elif action == 'replace_color' and background and bg_type == 'color':
        try:
            color = ImageColor.getrgb(background)
        except ValueError:
            color = (255, 255, 255)  # default to white

        solid_bg = Image.new("RGBA", result.size, color + (255,))
        solid_bg.paste(result, (0, 0), result)
        result = solid_bg

    # Step 3: Save output
    output_filename = f"processed_{uuid.uuid4().hex}.png"
    save_folder = history_folder or 'static/history'
    os.makedirs(save_folder, exist_ok=True)

    output_path = os.path.join(save_folder, output_filename)
    result.save(output_path, format='PNG')


    # ✅ Return relative path so Flask can serve it
    return os.path.join("static", "history", output_filename)

    return output_path
