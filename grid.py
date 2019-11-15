import io
import subprocess
import tempfile

from PIL import Image, ImageFont, ImageDraw

font = ImageFont.truetype("SourceSansPro-Semibold.otf", 32)
margin = 16


def create_grid(letters) -> bytes:
    image = Image.new("L", (212, 212), "white")

    draw = ImageDraw.Draw(image)

    for i in range(5):
        for j in range(5):
            draw.text((40 * i + margin, 40 * j), letters[i * 5 + j].upper(), font=font)

    f = io.BytesIO()
    image.save(f, format="png")
    return f.getvalue()


def grid_to_video(image, out=tempfile.NamedTemporaryFile()):
    with tempfile.NamedTemporaryFile() as f:
        f.write(image)
        f.flush()
        subprocess.run(
            [
                "ffmpeg",
                "-loop",
                "1",
                "-i",
                f.name,
                "-t",
                "1",
                "-f",
                "mp4",
                "-pix_fmt",
                "yuv420p",
                "-y",
                out.name,
            ],
            input=image,
        )
    return out
