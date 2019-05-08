# https://github.com/UB-Mannheim/tesseract/wiki
# pip install Pillow
# pip install opencv-python
# pip install pytesseract

# import the necessary packages
from PIL import Image, ImageFilter, ImageEnhance, ImageColor
import pytesseract
import os

# Enablee tesseract usage
pytesseract.pytesseract.tesseract_cmd = r'tesseract\tesseract.exe'


 
def extract_text(im_file, display=False, thresh=False, blur=False):
    # convert image to grayscale
    im = Image.open(im_file)

    # ENHANCE         
    im = im.convert('L')
    im = ImageEnhance.Sharpness(im).enhance(2)

    # apply OCR and delete temp file
    text = pytesseract.image_to_string(im)

    im.show()
    
    return text

def is_mail(path):
    ## Get image data
    im = Image.open(path).convert('RGB')
    im = im.filter(ImageFilter.MedianFilter(7))
    im_data = list(im.getdata())
    width, height = im.size 
    print("Width:", width, "Height:", height)

    colours = {
            "black" : (0, 0, 0),
            "white" : (200, 200, 200),
            "red" : (255, 0, 0),
            "green": (0, 255, 0),
            "blue" : (0, 0, 255)
        }

    ## Is this pixel within an outside border?
    def in_border(position, tolerance):
        # Get positions
        if type(position) == tuple:
            x_pos = position[0]
            y_pos = position[1]
        elif type(position) == int:
            x_pos = position % width
            y_pos = position // width
        else:
            raise(TypeError, "Position must be an (x, y) tuple or int")

        # Get border tolerances
        if type(tolerance) == tuple:
            x_tol = tolerance[0]
            y_tol = tolerance[1]
        elif type(tolerance) == int:
            x_tol = tolerance
            y_tol = tolerance
        else:
            raise(TypeError, "Tolerance must be an (x, y) tuple or int")

        return not (x_pos > x_tol and y_pos > y_tol and x_pos < width - x_tol and y_pos < height - y_tol)
    
    ## Is a pixel within the range of the background?
    def is_background(pixel):
        return (pixel in border_pixels) or (pixel in border_pixels_off)

    def classify(pixel):
        manhattan = lambda x, y: abs(x[0] - y[0]) + abs(x[1] - y[1]) + abs(x[2] + y[2])
        distances = {k: manhattan(v, pixel) for k, v in colours.items()}
        colour = min(distances, key=distances.get)
        return colour

    ## Get background values
    border_pixels = set([im_data[pixel] for pixel in range(width * height) if in_border(pixel, 5)])
    border_pixels_off = []
    for offset in range(-3, 4):
        border_pixels_off = set([(r+offset, g+offset, b+offset) for r, g, b in border_pixels] + list(border_pixels_off))
        

    ## Remove the background
    pixels = im.load()
    backgrounds = 0
    background_color = (255, 128, 128)

    whites = 0
    reds = 0
    greens = 0
    blues = 0
    
    for i in range(width):
        for j in range(height):
            if is_background(pixels[i,j]): # and in_border((i + 1, j + 1), (width // 6, height // 6)):
                pixels[i, j] = background_color
                backgrounds += 1
                
            elif classify(pixels[i, j]) == "white":
                whites += 1
                pixels[i, j] = colours["white"]
                
            elif classify(pixels[i, j]) == "red":
                reds += 1
                pixels[i, j] = colours["red"]
                
            elif classify(pixels[i, j]) == "green":
                greens += 1
                pixels[i, j] = colours["green"]
                
            elif classify(pixels[i, j]) == "blue":
                blues += 1
                pixels[i, j] = colours["blue"]



    # Get some outputs
    print(str(100 * whites/(len(im_data) - backgrounds)) + "% of pixels are white")
    print(str(100 * reds/(len(im_data) - backgrounds)) + "% of pixels are red")
    print(str(100 * greens/(len(im_data) - backgrounds)) + "% of pixels are green")
    print(str(100 * blues/(len(im_data) - backgrounds)) + "% of pixels are blue")


    im.show()


    
# Main
if __name__ == "__main__":                            
    directories = ["mail", "junk", "other"]
    for directory in directories:
        for im_file in [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]:
            print(directory.upper() + ":", im_file, "\n" + "="*40)
            #print(extract_text(directory + "\\" + im_file))
            is_mail(directory + "\\" + im_file)
            print("\n"*3)
    
