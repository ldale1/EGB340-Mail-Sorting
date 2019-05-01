# https://github.com/UB-Mannheim/tesseract/wiki
# pip install Pillow
# pip install opencv-python
# pip install pytesseract

# import the necessary packages
from PIL import Image
import pytesseract
import cv2 as cv
import os

# Enablee tesseract usage
pytesseract.pytesseract.tesseract_cmd = r'tesseract\tesseract.exe'


 
def extract_text(im_file, display=False, thresh=False, blur=False):
    # convert image to grayscale
    image = cv.imread(im_file)
    processed_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    # Apply thresholding
    #  segment the foreground from the background
    #  dark text overlaid upon grey shapes
    if (thresh):
        processed_image = cv.threshold(processed_image, 0, 255, \
                            cv.THRESH_BINARY | cv.THRESH_OTSU)[1]

    # Apply blur
    #  blurring reduces salty and pepper noise
    if (blur):
        processed_image = cv.medianBlur(processed_image, 3)
     
    # write the grayscale image to disk as a temporary file so we can apply OCR to it
    im_file_temp = "{}-temp.png".format(im_file)
    cv.imwrite(im_file_temp, processed_image)

    # show the output images
    if (display):
        cv.imshow("Image", image)
        cv.imshow("Output", processed_image)

    # apply OCR and delete temp file
    text = pytesseract.image_to_string(Image.open(im_file_temp))
    os.remove(im_file_temp)
    return text

def is_mail(path):
    ## Get image data
    im = Image.open(path).convert('RGB')
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

            
        return not (x_pos > x_tol and y_pos > y_tol and x_pos < width - x_tol and y_pos < height - y_tol)
    
    ## Is a pixel within the range of the background?
    def is_background(pixel):
        return (r_min <= pixel[0] <= r_max) and \
               (b_min <= pixel[1] <= b_max) and \
               (g_min <= pixel[2] <= g_max)


    ## Threshold values 
    white_thresh = 200

    ## Get background values
    r_arr = [im_data[pixel][0] for pixel in range(width * height) if in_border(pixel, 3)]
    b_arr = [im_data[pixel][1] for pixel in range(width * height) if in_border(pixel, 3)]
    g_arr = [im_data[pixel][2] for pixel in range(width * height) if in_border(pixel, 3)]

    r_max = max(r_arr)
    r_min = min(r_arr)
    b_max = max(b_arr)
    b_min = min(b_arr)
    g_max = max(g_arr)
    g_min = min(g_arr)


    ## Remove the background
    pixels = im.load()
    backgrounds = 0
    background_color = (255, 128, 128)
    for i in range(width):
        for j in range(height):
            if is_background(pixels[i,j]): # and in_border((i + 1, j + 1), (width // 6, height // 6)):
                pixels[i, j] = background_color
                backgrounds += 1


    ## Count how many white pixels
    whites = 0
    for r, g, b in im_data:
        if (r > white_thresh and g > white_thresh and b > white_thresh):
            whites += 1


    # Get some outputs
    print(str(100 * whites/(len(im_data) - backgrounds)) + "% of pixels are white")

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
    
