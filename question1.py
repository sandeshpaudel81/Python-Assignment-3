import cv2
import customtkinter
from tkinter import Tk, Label, Button, Scale, filedialog, Frame, HORIZONTAL, Text
from PIL import Image, ImageTk

# GUI-based Image Crop and Resize Editor using OpenCV, Tkinter, and PIL
class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")  # Set window title

        # Application Header
        self.header = Label(root, text="Image Editor", font=("Helvetica", 16, "bold"))
        self.header.pack(pady=10)

        self.application_message_label = Label(root, text="", font=("Helvetica", 12))
        self.application_message_label.pack(pady=2)

        # Main container for original and cropped images
        self.frame = Frame(root)
        self.frame.pack()

        # Label to show the original image with crop overlay
        self.original_label = Label(self.frame)
        self.original_label.grid(row=0, column=0)

        # Label to show the cropped/preview image
        self.preview_frame = Frame(self.frame, width=300, height=300)
        self.preview_frame.grid(row=0, column=1)
        self.preview_frame.pack_propagate(False)  # Prevent frame from shrinking to image

        self.cropped_label = Label(self.preview_frame, bg="gray")
        self.cropped_label.pack(expand=True, fill="both")

        self.button_frame = Frame(root)
        self.button_frame.pack(pady=10)

        # color1='#020f12'
        # color2='#05d7ff'
        # color3='#65e7ff'
        # color4='#000000'

        # Buttons side by side in the button_frame using grid
        self.load_button = Button(
            self.button_frame,
            background='#05d7ff',
            foreground='#000000',
            activebackground='#65e7ff',
            activeforeground='#000000',
            highlightthickness=2,
            highlightbackground='#05d7ff',
            highlightcolor='#ffffff',
            width=13,
            height=1,
            border=0,
            cursor='hand2',
            text="Load Image",
            font=('Arial', 12),
            command=self.load_image
        )
        self.load_button.grid(row=0, column=0, padx=10)

        self.save_button = Button(
            self.button_frame,
            background='#05d7ff',
            foreground='#000000',
            activebackground='#65e7ff',
            activeforeground='#000000',
            highlightthickness=2,
            highlightbackground='#05d7ff',
            highlightcolor='#ffffff',
            width=13,
            height=1,
            border=0,
            cursor='hand2',
            text="Save Image",
            font=('Arial', 12),
            command=self.save_image
        )
        self.save_button.grid(row=0, column=1, padx=10)

        # Slider to resize cropped image by percentage
        self.slider_frame = Frame(root)
        self.slider_frame.pack(pady=5)

        Label(self.slider_frame, text="Slide to Resize Image", font=("Arial", 12)).pack()
        self.resize_slider = customtkinter.CTkSlider(
            self.slider_frame, 
            from_=0, 
            to=200, 
            number_of_steps=20,
            width=300,
            height=20,
            fg_color='gray',
            progress_color='#05d7ff',
            button_color='orange',
            command=self.resize_image
        )
        self.resize_slider.pack()
        self.resize_slider.set(100)  # Default to 100% (no resize)
        self.slider_label = Label(self.slider_frame, text="", font=("Helvetica", 12, 'bold'))
        self.slider_label.pack()

        self.cropped_shape_label = Label(root, text="Cropped Image: x x x", font=("Helvetica", 12))
        self.cropped_shape_label.pack()

        self.resized_shape_label = Label(root, text="Resized Image: x x x", font=("Helvetica", 12))
        self.resized_shape_label.pack()

        # Initialize state variables
        self.image = None  # Full loaded image
        self.imageShape = None
        self.cropped_image = None # Cropped region from full image
          
        self.resized_image = None  # Cropped image after resizing
        
        self.crop_rect = None  # Coordinates of crop rectangle [x1, y1, x2, y2]
        self.drag_mode = None  # Mode used while dragging to resize crop area
        self.drag_start = (0, 0)  # Initial mouse position during dragging
        self.hover_side = None  # Current side hovered for visual feedback

        # Mouse events to support cropping and resizing
        self.original_label.bind("<Motion>", self.on_mouse_move)
        self.original_label.bind("<Button-1>", self.start_resize)
        self.original_label.bind("<B1-Motion>", self.do_resize)
        self.original_label.bind("<ButtonRelease-1>", self.end_resize)

    # Load an image using file dialog and initialize crop area in center
    def load_image(self):
        path = filedialog.askopenfilename()
        if not path:
            return

        self.image = cv2.imread(path)
        h, w = self.image.shape[:2]

        # Set crop area to center 50% of the image
        crop_w, crop_h = w // 2, h // 2
        x1, y1 = (w - crop_w) // 2, (h - crop_h) // 2
        self.crop_rect = [x1, y1, x1 + crop_w, y1 + crop_h]
        self.application_message_label.config(text="")
        self.update_display()

    # Display an image in a given label, resizing it to fit max dimensions
    def display_image(self, image, label, max_size=(500, 500)):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(image_rgb)
        pil_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(pil_img)
        label.configure(image=tk_img)
        label.image = tk_img  # Keep reference to avoid garbage collection

    # Refresh both the crop rectangle and cropped preview
    def update_display(self):
        self.draw_crop_rect()
        self.update_crop_preview()

    # Draw the crop rectangle on the original image for visual feedback
    def draw_crop_rect(self):
        preview = self.image.copy()
        x1, y1, x2, y2 = self.crop_rect
        thick = 10  # Thickness when hovered
        thin = 5    # Normal thickness

        if self.hover_side in ['left', 'right', 'top', 'bottom']:
            color = (0, 255, 0)
            # Draw each edge of the crop box individually
            cv2.line(preview, (x1, y1), (x1, y2), color, thick if self.hover_side == 'left' else thin)
            cv2.line(preview, (x2, y1), (x2, y2), color, thick if self.hover_side == 'right' else thin)
            cv2.line(preview, (x1, y1), (x2, y1), color, thick if self.hover_side == 'top' else thin)
            cv2.line(preview, (x1, y2), (x2, y2), color, thick if self.hover_side == 'bottom' else thin)
        else:
            # Default full rectangle without edge highlight
            cv2.rectangle(preview, (x1, y1), (x2, y2), (0, 255, 0), thin)

        self.display_image(preview, self.original_label)

    # Crop the selected region and show the resized version
    def update_crop_preview(self):
        x1, y1, x2, y2 = self.crop_rect
        self.cropped_image = self.image[y1:y2, x1:x2]
        self.resized_image = self.cropped_image.copy()
        self.display_image(self.resized_image, self.cropped_label, max_size=(300, 300))
        h, w = self.cropped_image.shape[:2]
        self.cropped_shape_label.config(text=f"Cropped Image: {w} × {h}")

    # Convert mouse coordinates on label to image coordinates
    def get_mouse_image_coords(self, event):
        label_w = self.original_label.winfo_width()
        label_h = self.original_label.winfo_height()
        img_h, img_w = self.image.shape[:2]
        scale_x = img_w / label_w
        scale_y = img_h / label_h
        return int(event.x * scale_x), int(event.y * scale_y)

    # Handle cursor hovering over crop rectangle sides
    def on_mouse_move(self, event):
        if self.image is None:
            return
        x, y = self.get_mouse_image_coords(event)
        x1, y1, x2, y2 = self.crop_rect
        margin = 10

        self.hover_side = None
        if abs(x - x1) < margin:
            self.hover_side = 'left'
        elif abs(x - x2) < margin:
            self.hover_side = 'right'
        elif abs(y - y1) < margin:
            self.hover_side = 'top'
        elif abs(y - y2) < margin:
            self.hover_side = 'bottom'
        elif abs(x - x1) < margin and abs(y - y1) < margin:
            self.hover_side = 'topleft'
        elif abs(x - x2) < margin and abs(y - y2) < margin:
            self.hover_side = 'bottomright'

        self.update_display()

    # Start resizing crop area on mouse click
    def start_resize(self, event):
        if self.image is None:
            return
        x, y = self.get_mouse_image_coords(event)
        x1, y1, x2, y2 = self.crop_rect
        margin = 10

        # Determine which side or corner to resize
        if abs(x - x1) < margin:
            self.drag_mode = 'left'
        elif abs(x - x2) < margin:
            self.drag_mode = 'right'
        elif abs(y - y1) < margin:
            self.drag_mode = 'top'
        elif abs(y - y2) < margin:
            self.drag_mode = 'bottom'
        elif abs(x - x1) < margin and abs(y - y1) < margin:
            self.drag_mode = 'topleft'
        elif abs(x - x2) < margin and abs(y - y2) < margin:
            self.drag_mode = 'bottomright'
        else:
            self.drag_mode = None

        self.drag_start = (x, y)

    # Resize crop rectangle dynamically during mouse drag
    def do_resize(self, event):
        if self.image is None or not self.drag_mode:
            return
        x, y = self.get_mouse_image_coords(event)
        dx, dy = x - self.drag_start[0], y - self.drag_start[1]
        x1, y1, x2, y2 = self.crop_rect

        # Adjust crop rectangle sides based on drag direction and mode
        if 'left' in self.drag_mode:
            x1 = max(0, min(x1 + dx, x2 - 10))
        if 'right' in self.drag_mode:
            x2 = min(self.image.shape[1], max(x2 + dx, x1 + 10))
        if 'top' in self.drag_mode:
            y1 = max(0, min(y1 + dy, y2 - 10))
        if 'bottom' in self.drag_mode:
            y2 = min(self.image.shape[0], max(y2 + dy, y1 + 10))

        self.crop_rect = [x1, y1, x2, y2]
        self.drag_start = (x, y)
        self.update_display()

    # End drag operation when mouse is released
    def end_resize(self, event):
        self.drag_mode = None

    # Resize the cropped image using the value from the slider
    def resize_image(self, value):
        if self.cropped_image is None or self.crop_rect is None:
            return
        scale = int(value)
        self.slider_label.configure(text=scale)
        width = int(self.cropped_image.shape[1] * scale / 100)
        height = int(self.cropped_image.shape[0] * scale / 100)
        self.resizedImageShape = str(width) + ' x ' + str(height)
        self.resized_image = cv2.resize(self.cropped_image, (width, height))
        self.display_image(self.resized_image, self.cropped_label)
        self.resized_shape_label.config(text=f"Resized Image: {width} × {height}")

    # Save the resized image using file dialog
    def save_image(self):
        if self.resized_image is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg *.jpeg")])
        if path:
            cv2.imwrite(path, self.resized_image)
            print("Image saved to:", path)
            self.application_message_label.config(text=f"Image saved to: {path}", fg='green')

# Launch the GUI application
if __name__ == "__main__":
    root = Tk()
    root.minsize(width=600, height=450)
    app = ImageEditorApp(root)
    root.mainloop()
