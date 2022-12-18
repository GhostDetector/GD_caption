import os
import tkinter as tk
from tkinter import messagebox as mb
from PIL import Image, ImageTk

# Initialize the index of the current image
global image_index
MAX_WIDTH = 512
MAX_HEIGHT = 512

image_index = 0
root = tk.Tk()
root.geometry('1024x1024')

##-------- Image System


# Set the directory containing the images
entrytitle = tk.Label(root, text="Enter Directory", width=64).pack()

# Initialize the entry widget
entrylabel = tk.Entry(root, textvariable="C:\\Users\\kaddo\\Desktop\\New folder\\Raw\\",width=64)
entrylabel.pack()

# Get the contents of the entry widget and assign it to the image_dir variable
# Get a list of the images in the directory

iteration_label= tk.Label(root)
iteration_label.pack
image_index = 0

def loadimages():
    
    image_dir = entrylabel.get()
    print("Loading Images")
    global image_filenames
    image_filenames = os.listdir(image_dir)
    file_types = (".png",".jpg")
    global imagelist
    imagelist = []
    for f in image_filenames:
        if f.endswith(file_types):
            # Open the image and scale it down using thumbnail()
            image = Image.open(os.path.join(image_dir, f))
            image.thumbnail((MAX_WIDTH, MAX_HEIGHT))
            imagelist.append(image)
    next_image()
    

export= tk.Button(root,text="load",command=loadimages).pack()
    
# Create a function to update the image
def next_image(event=None):
    global image_index
    # Get the image object for the current image
    images = imagelist;
    image = images[image_index]
    
    # Get the file name of the image

    
    # Create a PhotoImage object
    photo_image = ImageTk.PhotoImage(image)
    
    # Update the image displayed in the label
    image_label.configure(image=photo_image)
    image_label.image = photo_image
    
    
    image_path = image_filenames[image_index]
    image_path2 = os.path.basename(image_path)
    image_name, image_ext = os.path.splitext(image_path2)
    
    # Update the iteration label with the current iteration number and total
    iteration_label.configure(text="Iteration: {} / {}".format(image_index + 1, len(images)))
    # Increment the index of the current image
    
    image_index = (image_index + 1) % len(images)
    print("loading Image: {0} : {1} ".format(image_index,image_name))
    
    # Clear the entry widget
    entry.delete(0, 'end')
    
image_label = tk.Label(root)
image_label.pack()

# Create a button to update the image
button = tk.Button(root, text="Next", command=next_image)
root.bind_all("<Right>", next_image)
button.pack()

def previous_image(event=None):
    global image_index
    # Get the image object for the current image
    images = imagelist;
    image = images[image_index]
    
    # Get the file name of the image

    
    # Create a PhotoImage object
    photo_image = ImageTk.PhotoImage(image)
    
    # Update the image displayed in the label
    image_label.configure(image=photo_image)
    image_label.image = photo_image
    
    
    image_path = image_filenames[image_index]
    image_path2 = os.path.basename(image_path)
    image_name, image_ext = os.path.splitext(image_path2)
    
    # Update the iteration label with the current iteration number and total
    iteration_label.configure(text="Iteration: {} / {}".format(image_index + 1, len(images)))
    # Increment the index of the current image
    
    image_index = (image_index - 1) % len(images)
    print("loading Image: {0} : {1} ".format(image_index,image_name))
    
    # Clear the entry widget
    entry.delete(0, 'end')
    
image_label = tk.Label(root)
image_label.pack()

# Create a button to update the image
button = tk.Button(root, text="Previous", command=previous_image)
root.bind_all("<Left>", previous_image)
button.pack()

##------------ Prompt System


entryLabel = tk.Label(root, text="Enter Prompt Below").pack()

entry = tk.Entry(root, width=100)
entry.pack()

# Create a function to export the contents of the Entry widget to a .txt file
def export_to_txt(event):
    # Get the contents of the Entry widget
    text = entry.get()
    imgpath = entrylabel.get()
    print(imgpath)
    image_path = image_filenames[image_index-1]
    image_path2 = os.path.basename(image_path)
    image_name, image_ext = os.path.splitext(image_path2)

    # Print out the file name
    print("Path {0} : Image {1}".format(image_path2,image_name))
    # Use the image name as the file name for the text file
    text_file_name = image_name + ".txt"
    
    
    # Open a file for writing === Will need to parse file_name
    with open(os.path.join(imgpath, "{0}.txt".format(image_name)), "w") as f:
        # Write the contents of the Entry widget to the file
        print(text)
        f.write(text)
    
    next_image()
    
    
export= tk.Button(root,text="Export",command=export_to_txt)
root.bind_all("<Return>", export_to_txt)
export.pack();

def delete_txt_files():

    result = mb.askquestion('Purge txt files', 'Do you really want delete txt files?')

    # If the user clicks "Yes"
    if result:
        # Iterate through the files in the directory
        image_dir = entrylabel.get()
        for file in os.listdir(image_dir):
            # Check if the file is a .txt file
            if file.endswith('.txt'):
                # Delete the file
                print("Removing {0}".format(file))
                os.remove(os.path.join(image_dir, file))


# Create a button to delete the .txt files
purge = tk.Button(root, text='Delete .txt files', command=delete_txt_files)
purge.pack()

## Exit
root.mainloop()