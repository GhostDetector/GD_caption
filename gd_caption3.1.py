import os
import tkinter as tk
from tkinter import messagebox as mb
from PIL import Image, ImageTk
from glob import glob
import whisper
import sounddevice as sd
import soundfile as sf
import re
import clip
from aesthetic_predictor import predict_aesthetic

clip_model, preprocess = clip.load("ViT-B/32", device="cpu")

model = whisper.load_model('medium')
fs = 41400


class ImageAnnotationProgram:
    MAX_WIDTH = 512
    MAX_HEIGHT = 512

    def __init__(self):
        self.image_index = 0
        self.root = tk.Tk()
        self.root.geometry('1024x1024')
        self.image_filenames = []
        self.imagelist = []
        self.deleted_image_paths = []
        self.create_widgets()


    def create_widgets(self):
        self.header = tk.Frame(self.root)
        self.header.pack()
        self.entry_title = tk.Label(self.header, text="Enter Directory", width=64)
        self.entry_title.pack()

        self.entrylabel = tk.Entry(self.header, width=64)
        self.entrylabel.pack()

        self.iteration_label = tk.Label(self.header)
        self.iteration_label.pack(side='right')
        self.dimensions = tk.Label(self.header)
        self.dimensions.pack(side='right')
        self.scoreLabel = tk.Label(self.header)
        self.scoreLabel.pack(side='right')
        

        self.load_images_button = tk.Button(self.header, text="Load", command=self.load_images)
        self.load_images_button.pack(side='left')
        
        self.unload_images_button = tk.Button(self.header, text="Unload", command=self.unload_images)
        self.unload_images_button.pack(side='left')


        self.body = tk.Frame(self.root)
        self.body.pack()
        self.image_name = tk.Label(self.body,font=("Arial", 20))
        self.image_name.pack()
        self.image_label = tk.Label(self.body,font=("Arial", 20))
        self.image_label.pack()
        
        self.body2 = tk.Frame(self.root)
        self.body2.pack()
        
        self.next_image_button = tk.Button(self.body2, text="Next", command=self.next_image)
        self.next_image_button.pack(side='left')

        self.previous_image_button = tk.Button(self.body2, text="Previous", command=self.previous_image)
        self.previous_image_button.pack(side='left')
                # Create a button for deleting images
        self.delete_button = tk.Button(self.body2, text="DELETE", command=self.delete_image)
        self.delete_button.pack(side='right')

        self.save_button = tk.Button(self.body2, text="Save Caption", command=self.export_to_txt)
        self.save_button.pack(side='left')
        self.rad = tk.Frame(self.root)
        self.rad.pack()
        self.quality_selection = tk.StringVar()
        self.quality_selection.set(" ")

        self.quality=[' ','masterpiece','high quality','medium quality','low quality']
        self.create_radio_buttons(self.rad, self.quality, self.quality_selection)
        self.end = tk.Frame(self.root)
        self.end.pack()
        self.classes = [' ',"barbarian", "bard", "cleric", "druid", 
        "fighter",'monk','paladin','ranger','rogue',
        'sorcerer','warlock','wizard','artificer']

        self.classes.sort()


        self.class_selection = tk.StringVar()


        self.class_selection.set(" ")  # Default selection


        self.class_frame = tk.Frame(self.root)

        self.create_radio_buttons(self.class_frame, self.classes, self.class_selection)

        self.class_frame.pack()

        prompt = "[Mood][Media][Adjectives][Subject][Action][Style]"
        tk.Label(self.end, text=f"Enter Prompt Below {prompt}").pack()
        self.entry = tk.Entry(self.end, width=100)
        self.entry.pack()
        tk.Label(self.end, text=f"Static Prompt").pack()
        self.entrystatic = tk.Entry(self.end, width=100)
        self.entrystatic.pack()

        self.clear_button = tk.Button(self.end, text="Clear", command=self.clear_entry)
        self.clear_button.pack()
        self.is_recording = False
        self.recording = None
        
        self.root.bind("<KeyPress-Shift_L>", self.start_recording)
        self.root.bind("<KeyRelease-Shift_L>", self.stop_recording) 
        
        self.root.bind("<Right>", self.next_image)
        self.root.bind("<Return>", self.next_save)
        self.root.bind("<Left>", self.previous_image)
        self.clip = tk.Button(self.end, text="Caption", command=self.get_aesthetic_score)
        self.clip.pack(side='left')

#######


        self.classes_entry = tk.Entry(self.root, width=64)
        self.classes_entry.pack()

        self.update_classes_button = tk.Button(self.root, text="Update Classes", command=self.update_classes)
        self.update_classes_button.pack()
    '''       
     self.undo_button = tk.Button(self.root, text="Undo_DEL", command=self.undo_delete)
        self.undo_button.pack(pady=5)
    '''
    def update_radio_buttons(self, frame, options, variable):
        variable.set(" ")  # Reset the selection
        radio_buttons = frame.grid_slaves()  # Get the existing radio buttons

        # Remove the existing radio buttons
        for button in radio_buttons:
            button.grid_forget()

        # Create new radio buttons with the updated options
        num_columns = 7  # Number of columns for grid layout
        for i, option in enumerate(options):
            radio_button = tk.Radiobutton(frame, text=option, variable=variable, value=option, bg=frame["bg"])
            radio_button.grid(row=i // num_columns, column=i % num_columns, sticky='w')


    def update_classes(self):
        # Get the classes from the entry label, split by commas
        classes_text = self.classes_entry.get()
        new_classes = [' '] + [class_name.strip() for class_name in classes_text.split(' ')]

        # Call the update_radio_buttons method
        self.update_radio_buttons(self.class_frame, new_classes, self.class_selection)

    def create_radio_buttons(self, frame, options, variable):
        num_columns = 7  # Number of columns for grid layout
        for i, option in enumerate(options):
            radio_button = tk.Radiobutton(frame, text=option, variable=variable, value=option, bg=frame["bg"])
            radio_button.grid(row=i // num_columns, column=i % num_columns, sticky='w')


    def get_dir(self):
        return self.entrylabel.get()

    def clear_entry(self):
        self.entry.delete(0, 'end')

    def load_caption(self):
        caption = self.get_dir()
        image_path = self.image_filenames[self.image_index]
        image_name, image_ext = os.path.splitext(os.path.basename(image_path))
        caption_file = os.path.join(caption, image_name + '.txt')
        try:
            with open(caption_file, 'r') as f:
                
                caption = f.read()
                print(f"Caption : {caption}")
                self.entry.delete(0, 'end')
                self.entry.insert(0, caption)
                #caption_file.close()
        except:
            print("Empty")
            self.clear_entry()


    def load_images(self):
        image_dir = self.entrylabel.get()
        if not os.path.isdir(image_dir):
            mb.showerror("Invalid directory", "Please enter a valid directory.")
            return

        try:
            image_files = glob(os.path.join(image_dir, "*.png")) + glob(os.path.join(image_dir, "*.jpg"))
            image_files.sort()
            self.image_filenames = []
            self.imagelist = []
            for f in image_files:
                try:
                    img = Image.open(f)
                    img.thumbnail((self.MAX_WIDTH, self.MAX_HEIGHT))
                    self.imagelist.append(img)
                    self.image_filenames.append(f)
                except:
                    continue

            self.next_image()
            self.previous_image()
        except Exception as e:
            mb.showerror("Error", f"An error occurred while loading images: {e}")
        print(self.image_filenames)

    def updateinfo(self):
        image = self.imagelist[self.image_index]

        photo_image = ImageTk.PhotoImage(image)

        self.image_label.configure(image=photo_image)
        self.image_label.image = photo_image
        
        # Get the file name of the image
        image_path = self.image_filenames[self.image_index]
        image_name, image_ext = os.path.splitext(os.path.basename(image_path))
        self.image_name.configure(text=image_name)
      
        self.iteration_label.configure(text="Iteration: {} / {}".format(self.image_index + 1, len(self.imagelist)))
        score = self.get_aesthetic_score(image).item()
        self.scoreLabel.configure(text=f"Score: {round(score,2)}")
        self.dimensions.configure(text=f'{photo_image.width()}x{photo_image.height()}')
        print("loading Image: {0} : {1} ".format(self.image_index,image_name))
        #self.quality.set(" ")
        self.clear_entry()
        self.load_caption()
   

    def next_image(self, event=None):
        self.image_index = (self.image_index + 1) % len(self.imagelist)
        self.updateinfo()



    def next_save(self, event=None):
        self.export_to_txt()
        self.next_image()

    def previous_image(self, event=None):
        if not self.imagelist:
            return

        self.image_index = (self.image_index - 1) % len(self.imagelist)
        self.updateinfo()

    def export_to_txt(self):
        caption = self.entry.get()
        caption2 = self.entrystatic.get()
        image_path = self.image_filenames[self.image_index]
        image_dir = self.get_dir()
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        text_file = os.path.join(image_dir, f"{image_name}.txt")
        print(f'txt: {text_file}')
        qual = self.quality_selection.get()
        with open(text_file, 'w') as f:
            f.write(f'{caption} {caption2} {qual}')
        print(f'Save Caption: {caption}') 
        self.clear_entry()

        
    def unload_images(self):
        # Clear the image_filenames and imagelist lists
        self.image_filenames.clear()
        self.imagelist.clear()
        
        # Remove the current image from the GUI
        self.image_label.configure(image='')
        self.iteration_label.configure(text='')
        
    def delete_image(self):
        current_image_path = self.image_filenames[self.image_index]
        current_image_index = self.image_index

        # Move the image file to the trash directory
        image_dir = self.get_dir()
        trash_dir = os.path.join(image_dir, "trash")
        os.makedirs(trash_dir, exist_ok=True)
        image_name = os.path.basename(current_image_path)
        trash_path = os.path.join(trash_dir, image_name)
        os.rename(current_image_path, trash_path)

        # Update the image list and index
        self.image_filenames.pop(current_image_index)
        self.imagelist.pop(current_image_index)
        if len(self.imagelist) > 0:
            self.image_index = min(current_image_index, len(self.imagelist) - 1)
            self.next_image()

        # Store the deleted image path for undoing later
        self.deleted_image_paths.append((current_image_path, current_image_index))
        
        # Show the next image
        if self.image_index >= len(self.imagelist):
            self.image_index = len(self.imagelist) - 1
        self.next_image()
        self.previous_image()

    def start_recording(self, event):
        if not self.is_recording:
            self.is_recording = True
            channels = 2 
            blocksize = 2048 
            self.recording = sd.rec(int(5 * fs), samplerate=fs, channels=channels, blocksize=blocksize)
            print('Recording...')
        
    def stop_recording(self, event):
        if self.is_recording:
            self.is_recording = False
            filename = "audio.wav"
            sf.write(filename, self.recording, fs)
            print('Recording stopped.')
            self.transcribe_audio(filename)
            
    def transcribe_audio(self,recording):
        print("Transcribing...")
        recording = model.transcribe("audio.wav")
        print("Done.")
        text = recording["text"]
        print(text)
        text = re.sub(r'[^\w\s]', '', text)
        self.clear_entry()
        self.entry.insert(0, text)

    def get_aesthetic_score(self,image):
        aesthetic_model = predict_aesthetic(image)
        return aesthetic_model

'''    def undo_delete(self):
        if len(self.deleted_image_paths) > 0:
            # Get the most recent deleted image path and index
            deleted_image_path, deleted_image_index = self.deleted_image_paths.pop()

            # Move the image file back to the original directory
            image_dir = self.get_dir()
            image_name = os.path.basename(deleted_image_path)
            original_path = os.path.join(image_dir, image_name)
            os.rename(deleted_image_path, original_path)

            # Update the image list and index
            self.image_filenames.insert(deleted_image_index, original_path)
            image = Image.open(original_path).thumbnail((self.MAX_WIDTH, self.MAX_HEIGHT))
            self.imagelist.insert(deleted_image_index, image)
            if self.image_index >= deleted_image_index:
                self.image_index += 1
            self.next_image()
'''
if __name__ == "__main__":
    app = ImageAnnotationProgram()
    app.root.mainloop()