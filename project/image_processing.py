from PIL import Image, ImageFilter

def apply_grayscale(image_path, output_path):
    image = Image.open(image_path)
    gray_image = image.convert("L")
    gray_image.save(output_path)

def apply_blur(image_path, output_path):
    image = Image.open(image_path)
    blurred_image = image.filter(ImageFilter.BLUR)
    blurred_image.save(output_path)

def apply_glitch(image_path, output_path):
    image = Image.open(image_path)
    pixels = image.load()
    width, height = image.size
    for y in range(height):
        offset = int((y % 10) * 5)
        for x in range(width):
            if x + offset < width:
                pixels[x, y] = pixels[x + offset, y]
    image.save(output_path)
    
#############################################
def apply_invert(image_path, output_path):
    image = Image.open(image_path)
    inverted_image = Image.eval(image, lambda x: 255 - x)  # Invert each pixel
    inverted_image.save(output_path)
    
def apply_sepia(image_path, output_path):
    """Apply a sepia effect to the image."""
    image = Image.open(image_path)
    width, height = image.size
    pixels = image.load()

    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]

            if len(pixel) == 3:  # RGB
                r, g, b = pixel
            elif len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:
                raise ValueError("Format d'image non supporté")

            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
            pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))

    image.save(output_path)
    
def apply_pixelate(image_path, output_path, pixel_size=10):
    image = Image.open(image_path)
    small_image = image.resize(
        (image.width // pixel_size, image.height // pixel_size),
        resample=Image.NEAREST
    )
    pixelated_image = small_image.resize(
        (image.width, image.height),
        resample=Image.NEAREST
    )
    pixelated_image.save(output_path)