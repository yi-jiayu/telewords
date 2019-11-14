import io

from PIL import Image, ImageFont, ImageDraw, ImageChops, ImageOps
from letters import get_letters

font = ImageFont.truetype("SourceSansPro-Semibold.otf", 32)
margin = 16


def create_grid(letters):
    image = Image.new('L', (212, 212), 'white')

    draw = ImageDraw.Draw(image)

    for i in range(5):
        for j in range(5):
            draw.text((40 * i, 40 * j), letters[i * 5 + j].upper(), font=font)

    bg = Image.new('L', (212, 212), 'white')
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    crop = image.crop(bbox)
    image = ImageOps.expand(crop, border=margin, fill='white')

    f = io.BytesIO()
    image.save(f, format='png')
    return f
