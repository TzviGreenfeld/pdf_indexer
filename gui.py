import tkinter as tk
from tkinter import filedialog


class FileLoader:
    def __init__(self):
        # Create the main window
        self.window = tk.Tk()
        # self.window.wm_iconbitmap("icons/batman.ico")
        self.window.title("File Loader")
        self.window.geometry("320x240")

        # Set the button size
        self.button_size = {"height":3, "width":10}

        # Initialize the file paths list
        self.file_paths = []

    def load_file(self):
        # Show the "Open" dialog and get the selected file
        file_path = filedialog.askopenfilename()
        # Add the file path to the list
        self.file_paths.append(file_path)
        self.show_files_list()


    def load_files(self):
        # Show the "Open" dialog and get the selected files
        file_paths = filedialog.askopenfilenames()
        # Add the file paths to the list
        self.file_paths.extend(file_paths)
        self.show_files_list()


    def load_directory(self):
        # Show the "Open" dialog and get the selected directory
        directory_path = filedialog.askdirectory()
        self.show_files_list()

    
    def done(self):
        self.window.destroy()

    def create_buttons(self):
        # Create a button to open the "Open" dialog
        button = tk.Button(self.window, text="Load File",
                           command=self.load_file)
        # button size
        button.config(**self.button_size)
        button.pack(side=tk.LEFT)

        button = tk.Button(self.window, text="Load Files",
                           command=self.load_files)
        button.config(**self.button_size)
        button.pack(side=tk.LEFT)

        button = tk.Button(self.window, text="Load Directory",
                           command=self.load_directory)
        # tuple unpacking height, width = self.button_size

        button.config(**self.button_size)
        button.pack(side=tk.LEFT)
    
        button = tk.Button(self.window, text="Done", command=self.done)
        button.config(**self.button_size)
        # button.pack(side=tk.BOTTOM, anchor=tk.SW, fill=tk.X)
        button.pack(fill=tk.X, side=tk.BOTTOM, anchor=tk.SW)
        self.show_files_list()
    
    def show_files_list(self):
        # Create a label to show the selected files
        label = tk.Label(self.window, text="Files list:")
        label.pack()
        for file_path in self.file_paths:
            label = tk.Label(self.window, text=file_path)
            #place it to the right of all other widgets

            label.pack(anchor=tk.W)
        

    def get_file_paths(self):
        return self.file_paths

    def run(self):
        # Run the main loop
        self.window.mainloop()


if __name__ == "__main__":
    fl = FileLoader()
    fl.create_buttons()
    fl.run()
    print(fl.get_file_paths())





