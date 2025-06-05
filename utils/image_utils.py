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
    - output_path: path to the processed image
    """

    # Load original image
    original = Image.open(input_path).convert("RGBA")

    # Step 1: Remove background
    no_bg_bytes = remove(original)
    no_bg_image = no_bg_bytes.convert("RGBA")
    result = no_bg_image

    # Step 2: Replace with image or color background
    if action == 'replace_image' and background and bg_type == 'image':
        bg_path = os.path.join(background_folder or 'static/background_samples', background)
        background_img = Image.open(bg_path).convert("RGBA")
        background_img = background_img.resize(result.size)
        background_img.paste(result, (0, 0), result)
        result = background_img

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

    return output_path
