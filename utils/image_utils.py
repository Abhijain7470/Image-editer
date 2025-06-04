from PIL import Image, ImageColor
from rembg import remove
import os
import uuid


def process_image(input_path, action, background=None, bg_type=None):
    """
     Processes the uploaded image by removing the background or replacing it
    with either a new background image or a solid color.

    Parameters:
    - input_path: path to the uploaded image
    - action: 'remove', 'replace_image', or 'replace_color'
    - background: filename of background image or hex color code
    - bg_type: 'image' or 'color'

    Returns:
    - output_path: path to the processed image
    """

    # Load the original image
    original = Image.open(input_path).convert("RGBA")

    # Step 1: Remove Background
    no_bg = remove(original)
    result = Image.open(no_bg).convert("RGBA")

    # Step 2: If user chose to replace background
    if action == 'replace_image' and background and bg_type == 'image':
        bg_path = os.path.join('static', 'background_samples', background)
        background_img = Image.open(bg_path).convert("RGBA")
        background_img = background_img.resize(result.size)

        # past foreground (no_bg) onto new background 
        background_img.paste(result, (0, 0), result)
        result = background_img

    elif action == 'replace_color' and background and bg_type == 'color':
        try:
            color = ImageColor.getrgb(background)
        except ValueError:
            color = (255, 255, 255)     # Default to white on error

        bg_color = Image.new("RGBA", result.size, color + (255,))
        bg_color.paste(result, (0, 0), result)
        result = bg_color

    # Step 3: Save result to history folder
    output_filename = f"processed_{uuid.uuid4().hex}.png"
    output_path = os.path.join('static', 'history', output_filename)
    result.save(output_path, format='PNG')

    return output_path