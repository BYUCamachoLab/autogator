from PIL import Image
filename = r'logo.png'
img = Image.open(filename)
img.save('logo.ico')