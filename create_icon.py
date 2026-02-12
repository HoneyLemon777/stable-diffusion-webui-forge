from PIL import Image, ImageDraw, ImageFont, ImageColor
import os

# Settings
size = (256, 256)
bg_color_start = "#4158D0"
bg_color_end = "#C850C0"
text_color = "white"
text = "SD"
output_png = "sd_icon.png"
output_ico = "sd_icon.ico"

def create_gradient(width, height, start_hex, end_hex):
    base = Image.new('RGBA', (width, height), start_hex)
    top = Image.new('RGBA', (width, height), end_hex)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        for x in range(width):
            mask_data.append(int(255 * (x + y) / (width + height)))
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def create_icon():
    # Create background
    img = create_gradient(size[0], size[1], bg_color_start, bg_color_end)
    draw = ImageDraw.Draw(img)

    # Load font (try to find a nice bold font, fallback to default)
    try:
        # Try a few common windows fonts
        font_path = "C:\\Windows\\Fonts\\arialbd.ttf" # Arial Bold
        font = ImageFont.truetype(font_path, 160)
    except:
        font = ImageFont.load_default()

    # Calculate text layout
    # textbbox is available in newer Pillow, otherwise use textsize (deprecated but potential fallback)
    try:
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        text_width = right - left
        text_height = bottom - top
    except AttributeError:
        # Fallback for older Pillow
        text_width, text_height = draw.textsize(text, font=font)
    
    # Position text in center
    x = (size[0] - text_width) / 2
    y = (size[1] - text_height) / 2 - (text_height * 0.1) # slight adjustment up

    # Draw text
    draw.text((x, y), text, fill=text_color, font=font)
    
    # Save as PNG
    img.save(output_png)
    print(f"Generated {output_png}")
    
    # Save as ICO
    img.save(output_ico, format='ICO', sizes=[(256, 256)])
    print(f"Generated {output_ico}")

if __name__ == "__main__":
    create_icon()
