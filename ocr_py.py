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
pytesseract.pytesseract.tesseract_cmd = \
                                      r'C:\Program Files\Tesseract-OCR\tesseract.exe'
 
def extract_text(im_file, display=False, thresh=False, blur=False):
    # convert image to grayscale
    image = cv.imread(im_file)
    processed_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
##    ##https://medium.freecodecamp.org/getting-started-with-tesseract-part-ii-f7f9a0899b3f
##    
##    # Rescale the image, if needed.
##    image = cv.resize(image, None, fx=1.5, fy=1.5, interpolation=cv.INTER_CUBIC) #larger
##    img = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA) #smaller
##    
##    # Convert to gray
##    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
##
##    # Apply dilation and erosion to remove some noise
##    kernel = np.ones((1, 1), np.uint8)
##    img = cv2.dilate(img, kernel, iterations=1)
##    img = cv2.erode(img, kernel, iterations=1)
##
##    # Apply blur to smooth out the edges
##    img = cv.bilateralFilter(img,9,75,75)
##    img = cv.blur(img,(5,5))
##    img = cv2.GaussianBlur(img, (5, 5), 0)
##    img = cv2.medianBlur(img, 3)
##
##     
##    # Apply threshold to get image with only b&w (binarization)
##    cv.threshold(img,127,255,cv.THRESH_BINARY)
##    cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
##    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
##


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


# Main
if __name__ == "__main__":
    directories = ["mail", "junk", "other"]
    for directory in directories:
        for im_file in [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]:
            print(directory.upper() + ":", im_file, \
                  "\n" + "="*40, \
                  "\n" + extract_text(directory + "\\" + im_file), \
                  "\n"*3)
    
