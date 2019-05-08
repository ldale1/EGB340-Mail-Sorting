# https://github.com/UB-Mannheim/tesseract/wiki
# pip install --trusted-host pypi --trusted-host files.pythonhosted.org <**package-name>
# pip install Pillow opencv-python pytesseract

# import the necessary packages
from PIL import Image, ImageFilter, ImageEnhance, ImageColor
import pytesseract
import os
from picamera import PiCamera
import time
import RPi.GPIO as GPIO

# Pins
buttonPin = 10
servoPin = 12

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(servoPin, GPIO.OUT)

# Enablee tesseract usage
pytesseract.pytesseract.tesseract_cmd = r'tesseract\tesseract.exe'
address_list = ["Kauri", "Road"]

# Is there a buzzword to hint at real mail?
def text_genuine(path):
    # pre-process and apply OCR
    def extract_text(path):        
        im = Image.open(path)
        im = im.convert('L')
        im = ImageEnhance.Sharpness(im).enhance(2)
        return pytesseract.image_to_string(im)
    # Extract some text and check for buzzwords
    text = extract_text(path)
    keyword = False
    for buzzword in address_list:
        keyword = keyword or (buzzword in text)
    return keyword
    
def color_genuine(path):
    ## Get image data
    im = Image.open(path).convert('RGB')
    im = im.filter(ImageFilter.MedianFilter(7))
    im_data = list(im.getdata())
    width, height = im.size 
    print("Width:", width, "Height:", height)

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

        # Within any of the boundaries!
        return (x_pos < x_tol or y_pos < y_tol or \
                x_pos > width - x_tol or y_pos > height - y_tol)

        # Not within the center!
        #return not (x_pos > x_tol and y_pos > y_tol and \
        #            x_pos < width - x_tol and y_pos < height - y_tol)

    ## Clean this up!~~ ##
    
    ## Is a pixel within the range of the background?
    def is_background(pixel):
        return (pixel in border_pixels)   

    ## Get background values 
    border_pixels = set([im_data[pixel] for pixel in range(width * height) if in_border(pixel, 5)])     
    
    ## Count how many pixels of each
    whites = 0
    reds = 0
    greens = 0
    blues = 0

    ## Remove the background
    pixels = im.load()
    backgrounds = 0
    background_color = (255, 128, 128)
    for i in range(width):
        for j in range(height):
            r = pixels[i, j][0]
            g = pixels[i, j][1]
            b = pixels[i, j][2]

            # Is this pixel a part of the backgrounds
            if is_background(pixels[i,j]): # and in_border((i + 1, j + 1), (width // 6, height // 6)):
                pixels[i, j] = background_color
                backgrounds += 1

            # If its not a background, what is it???
            elif (r > 190 and g > 190 and b > 190):
                whites += 1
            elif (r > 100 and g < 100 and b < 100):
                reds += 1
            elif (r < 100 and g > 100 and b < 100):
                greens += 1
            elif (r < 100 and g < 100 and b > 100):
                blues += 1

    im.show()

    # More than % white and less than % of other colors
    return (100 * whites/(len(im_data) - backgrounds) > 70) and  \
              (100 * (reds + greens + blues)/(len(im_data) - backgrounds) < 20)


# Returns True if image on path is mail
def is_mail(path):
    t_good = text_genuine(path)
    c_good = color_genuine(path)
    assessment = "JUNK"
    if (t_good or c_good):
        assessment = "GENUINE"
    print("Text says:", t_good, "\nColour says:", c_good, "\n" + assessment, "\n"*3)
    return (t_good or c_good)

# Capture an image and return the path
def capture_image():
    camera = PiCamera()
    path = 'image.jpg'
    camera.start_preview()
    time.sleep(3)
    camera.capture(path)
    camera.stop_preview()
    camera.close()
    return path

# Servo go right
def rotate_right(p):
    for angle in range(75, 101):
        p.ChangeDutyCycle(angle/10)
        time.sleep(0.02)
    time.sleep(3)
    for angle in range(100, 74, -1):
        p.ChangeDutyCycle(angle/10)
        time.sleep(0.02)
# Servo go left
def rotate_left(p):
    for angle in range(75, 49, -1):
        p.ChangeDutyCycle(angle/10)
        time.sleep(0.02)
    time.sleep(3)
    for angle in range(50, 76):
        p.ChangeDutyCycle(angle/10)
        time.sleep(0.02)
    

## Capture an image, process it and rotate the servo
def button_callback():
    # Capture an image
    path = capture_image()    
    time.sleep(0.5)
    
    # Rotate Servo
    p = GPIO.PWM(servoPin, 50)
    p.start(7.5)
    if (is_mail(path)):
        rotate_right(p)
    else:
        rotate_left(p)
    p.stop()


# Main loop
def loop():
    while (True):
        if (GPIO.input(buttonPin)):
            button_callback()
        time.sleep(0.1)

if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
        
        

                
