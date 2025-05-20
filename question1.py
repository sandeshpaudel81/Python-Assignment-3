import cv2
import numpy as np
from tkinter import Tk, Label, Button, Scale, filedialog, Frame, HORIZONTAL
from PIL import Image, ImageTk


class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Crop Resizer")

        self.frame = Frame(root)
        self.frame.pack()

        self.original_label = Label(self.frame)
        self.original_label.grid(row=0, column=0)

        self.cropped_label = Label(self.frame)
        self.cropped_label.grid(row=0, column=1)

        Button(root, text="Load Image", command=self.load_image).pack()
        Button(root, text="Save Cropped Image", command=self.save_image).pack()

        self.resize_slider = Scale(root, from_=10, to=200, orient=HORIZONTAL,
                                   label="Resize %", command=self.resize_image)
        self.resize_slider.pack()
        self.resize_slider.set(100)

        self.image = None
        self.cropped_image = None
        self.resized_image = None
        self.crop_rect = None  # [x1, y1, x2, y2]
        self.drag_mode = None  # 'left', 'right', 'top', 'bottom', 'topleft', etc.
        self.drag_start = (0, 0)

        self.hover_side = None  # to track hovered side
        self.original_label.bind("<Motion>", self.on_mouse_move)

        self.original_label.bind("<Button-1>", self.start_resize)
        self.original_label.bind("<B1-Motion>", self.do_resize)
        self.original_label.bind("<ButtonRelease-1>", self.end_resize)

    def load_image(self):
        path = filedialog.askopenfilename()
        if not path:
            return

        self.image = cv2.imread(path)
        h, w = self.image.shape[:2]

        # Initialize crop rectangle in center (50% of image)
        crop_w, crop_h = w // 2, h // 2
        x1, y1 = (w - crop_w) // 2, (h - crop_h) // 2
        self.crop_rect = [x1, y1, x1 + crop_w, y1 + crop_h]

        self.update_display()

    def display_image(self, image, label, max_size=(500, 500)):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(image_rgb)
        pil_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(pil_img)
        label.configure(image=tk_img)
        label.image = tk_img

    def update_display(self):
        self.draw_crop_rect()
        self.update_crop_preview()

    def draw_crop_rect(self):
        preview = self.image.copy()
        x1, y1, x2, y2 = self.crop_rect
        thick = 10  # highlight thickness
        thin = 5   # normal thickness

        if self.hover_side in ['left', 'right', 'top', 'bottom']:
            # draw each side separately
            color = (0, 255, 0)

            # Left
            cv2.line(preview, (x1, y1), (x1, y2), color, thick if self.hover_side == 'left' else thin)
            # Right
            cv2.line(preview, (x2, y1), (x2, y2), color, thick if self.hover_side == 'right' else thin)
            # Top
            cv2.line(preview, (x1, y1), (x2, y1), color, thick if self.hover_side == 'top' else thin)
            # Bottom
            cv2.line(preview, (x1, y2), (x2, y2), color, thick if self.hover_side == 'bottom' else thin)
        else:
            # default full rectangle
            cv2.rectangle(preview, (x1, y1), (x2, y2), (0, 255, 0), thin)

        self.display_image(preview, self.original_label)

    def update_crop_preview(self):
        x1, y1, x2, y2 = self.crop_rect
        self.cropped_image = self.image[y1:y2, x1:x2]
        self.resized_image = self.cropped_image.copy()
        self.display_image(self.resized_image, self.cropped_label, max_size=(300, 300))

    def get_mouse_image_coords(self, event):
        label_w = self.original_label.winfo_width()
        label_h = self.original_label.winfo_height()
        img_h, img_w = self.image.shape[:2]
        scale_x = img_w / label_w
        scale_y = img_h / label_h
        return int(event.x * scale_x), int(event.y * scale_y)
    
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

    def start_resize(self, event):
        if self.image is None:
            return
        x, y = self.get_mouse_image_coords(event)
        x1, y1, x2, y2 = self.crop_rect
        margin = 10

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

    def do_resize(self, event):
        if self.image is None or not self.drag_mode:
            return
        x, y = self.get_mouse_image_coords(event)
        dx, dy = x - self.drag_start[0], y - self.drag_start[1]
        x1, y1, x2, y2 = self.crop_rect

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

    def end_resize(self, event):
        self.drag_mode = None

    def resize_image(self, value):
        if self.cropped_image is None or self.crop_rect is None:
            return
        scale = int(value)
        width = int(self.cropped_image.shape[1] * scale / 100)
        height = int(self.cropped_image.shape[0] * scale / 100)
        self.resized_image = cv2.resize(self.cropped_image, (width, height))
        self.display_image(self.resized_image, self.cropped_label)

    def save_image(self):
        if self.resized_image is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg *.jpeg")])
        if path:
            cv2.imwrite(path, self.resized_image)
            print("Image saved to:", path)


if __name__ == "__main__":
    root = Tk()
    app = ImageEditorApp(root)
    root.mainloop()
