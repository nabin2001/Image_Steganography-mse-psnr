import cv2
import numpy as np
from tkinter import Tk, Label, Button, filedialog, font, messagebox, Toplevel, Entry
from PIL import Image, ImageTk

# Global paths
cover_image_path = ""
steganographed_image_path = ""

# Function to select cover image
def select_cover_image():
    global cover_image_path
    cover_image_path = filedialog.askopenfilename()
    cover_image = Image.open(cover_image_path)
    cover_image = cover_image.resize((300, 300), Image.LANCZOS)
    cover_image = ImageTk.PhotoImage(cover_image)
    cover_image_panel.config(image=cover_image)
    cover_image_panel.image = cover_image
    cover_image_name_label.config(text=cover_image_path.split('/')[-1])

# Function to select steganographed image
def select_steganographed_image():
    global steganographed_image_path
    steganographed_image_path = filedialog.askopenfilename()
    steganographed_image = Image.open(steganographed_image_path)
    steganographed_image = steganographed_image.resize((300, 300), Image.LANCZOS)
    steganographed_image = ImageTk.PhotoImage(steganographed_image)
    steganographed_image_panel.config(image=steganographed_image)
    steganographed_image_panel.image = steganographed_image
    steganographed_image_name_label.config(text=steganographed_image_path.split('/')[-1])

# Function to embed text into image
def embed_text():
    if not cover_image_path:
        messagebox.showerror("Error", "Please select a cover image!")
        return

    text = text_entry.get()
    if not text:
        messagebox.showerror("Error", "Please enter the text to embed!")
        return

    cover_image = cv2.imread(cover_image_path)
    binary_text = ''.join(format(ord(char), '08b') for char in text) + '1111111111111110'  # End delimiter

    if len(binary_text) > cover_image.size * 3:
        messagebox.showerror("Error", "Text is too long to be embedded in the selected image.")
        return

    idx = 0
    for i in range(cover_image.shape[0]):
        for j in range(cover_image.shape[1]):
            for k in range(3):
                if idx < len(binary_text):
                    cover_image[i, j, k] = (cover_image[i, j, k] & ~1) | int(binary_text[idx])
                    idx += 1

    save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    cv2.imwrite(save_path, cover_image)
    messagebox.showinfo("Success", "Text embedded and saved successfully!")

# Function to retrieve text from image
def retrieve_text():
    if not steganographed_image_path:
        messagebox.showerror("Error", "Please select a steganographed image!")
        return

    stego_image = cv2.imread(steganographed_image_path)
    binary_text = ""
    for i in range(stego_image.shape[0]):
        for j in range(stego_image.shape[1]):
            for k in range(3):
                binary_text += str(stego_image[i, j, k] & 1)
                if binary_text.endswith('1111111111111110'):
                    binary_text = binary_text[:-16]
                    text = ''.join(chr(int(binary_text[i:i+8], 2)) for i in range(0, len(binary_text), 8))
                    messagebox.showinfo("Retrieved Text", f"Retrieved Text: {text}")
                    return

    messagebox.showerror("Error", "No hidden text found in the image.")

# Function to calculate MSE
def mse(imageA, imageB):
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err

# Function to calculate PSNR
def psnr(mse, max_pixel=255.0):
    if mse == 0:
        return 100
    return 20 * np.log10(max_pixel / np.sqrt(mse))

# Function to calculate and display MSE and PSNR
def calculate_metrics():
    if not cover_image_path or not steganographed_image_path:
        messagebox.showerror("Error", "Please select both cover and steganographed images!")
        return

    original_img = cv2.imread(cover_image_path)
    steganographed_img = cv2.imread(steganographed_image_path)

    mse_value = mse(original_img, steganographed_img)
    psnr_value = psnr(mse_value)

    mse_label.config(text=f"MSE: {mse_value:.5f}")
    psnr_label.config(text=f"PSNR: {psnr_value:.2f} dB")

# Create main window with three buttons
def main_window():
    global root
    root = Tk()
    root.title("Image Steganography")
    root.configure(bg='black')

    header_font = font.Font(family='Helvetica', size=24, weight='bold')
    header = Label(root, text="Image Steganography", font=header_font, bg='black', fg='white')
    header.pack(pady=20)
    
    button_font = font.Font(family='Arial', size=16, weight='bold')
    
    convert_button = Button(root, text="Encode the Image with Text", command=convert_window, font=button_font, bg='darkgrey', fg='black', borderwidth=1, relief='solid', highlightthickness=0)
    convert_button.pack(pady=20)
    
    retrieve_button = Button(root, text="Decode the Hidden Text", command=retrieve_window, font=button_font, bg='darkgrey', fg='black', borderwidth=1, relief='solid', highlightthickness=0)
    retrieve_button.pack(pady=20)
    
    calculate_button = Button(root, text="Calculate Metrics", command=metrics_window, font=button_font, bg='darkgrey', fg='black', borderwidth=1, relief='solid', highlightthickness=0)
    calculate_button.pack(pady=20)
    
    footer_font = font.Font(family='Helvetica', size=12, weight='bold')
    footer = Label(root, text="Designed by Nabin Roy", font=footer_font, bg='black', fg='white')
    footer.pack(side='bottom', pady=20)
    
    root.mainloop()

# Window for converting text to image steganography
def convert_window():
    convert_win = Toplevel(root)
    convert_win.title("Convert Text to Image Steganography")
    convert_win.configure(bg='black')
    
    cover_image_label_font = font.Font(family='Arial', size=14, weight='bold', underline=0)
    cover_image_label = Label(convert_win, text="Cover Image", font=cover_image_label_font, bg='black', fg='limegreen')
    cover_image_label.grid(row=0, column=0, sticky="w", padx=120, pady=10)

    global cover_image_panel
    cover_image_panel = Label(convert_win, bg='black')
    cover_image_panel.grid(row=1, column=0, padx=50, pady=10)

    global cover_image_name_label
    cover_image_name_label = Label(convert_win, text="", font=cover_image_label_font, bg='black', fg='white')
    cover_image_name_label.grid(row=2, column=0, sticky="w", padx=120, pady=10)

    cover_image_button_font = font.Font(family='Arial', size=12, weight='bold')
    cover_image_button = Button(convert_win, text="Select Cover Image", command=select_cover_image, font=cover_image_button_font, bg='darkgrey', fg='black', borderwidth=1, relief='solid', highlightthickness=0)
    cover_image_button.grid(row=3, column=0, padx=10, pady=10)
    
    text_label_font = font.Font(family='Arial', size=14, weight='bold', underline=0)
    text_label = Label(convert_win, text="Text to Embed", font=text_label_font, bg='black', fg='limegreen')
    text_label.grid(row=0, column=1, sticky="w", padx=120, pady=10)

    global text_entry
    text_entry = Entry(convert_win, font=text_label_font, bg='white', fg='black', width=30)
    text_entry.grid(row=1, column=1, padx=50, pady=10)

    embed_button_font = font.Font(family='Helvetica', size=16, weight='bold', slant='italic')
    embed_button = Button(convert_win, text="Embed Text", command=embed_text, font=embed_button_font, bg='darkgrey', fg='black', borderwidth=1, relief='solid', highlightthickness=0)
    embed_button.grid(row=2, column=1, pady=20)

# Window for retrieving text from steganographed image
def retrieve_window():
    retrieve_win = Toplevel(root)
    retrieve_win.title("Retrieve Text from Image")
    retrieve_win.configure(bg='black')

    steganographed_image_label_font = font.Font(family='Arial', size=14, weight='bold', underline=0)
    steganographed_image_label = Label(retrieve_win, text="Steganographed Image", font=steganographed_image_label_font, bg='black', fg='limegreen')
    steganographed_image_label.grid(row=0, column=0, sticky="w", padx=120, pady=10)

    global steganographed_image_panel
    steganographed_image_panel = Label(retrieve_win, bg='black')
    steganographed_image_panel.grid(row=1, column=0, padx=50, pady=10)

    global steganographed_image_name_label
    steganographed_image_name_label = Label(retrieve_win, text="", font=steganographed_image_label_font, bg='black', fg='white')
    steganographed_image_name_label.grid(row=2, column=0, sticky="w", padx=120, pady=10)

    steganographed_image_button_font = font.Font(family='Arial', size=12, weight='bold')
    steganographed_image_button = Button(retrieve_win, text="Select Steganographed Image", command=select_steganographed_image, font=steganographed_image_button_font, bg='darkgrey', fg='black', borderwidth=1, relief='solid', highlightthickness=0)
    steganographed_image_button.grid(row=3, column=0, padx=10, pady=10)

    retrieve_button_font = font.Font(family='Helvetica', size=16, weight='bold', slant='italic')
    retrieve_button = Button(retrieve_win, text="Show Text", command=retrieve_text, font=retrieve_button_font, bg='darkgrey', fg='black', borderwidth=1, relief='solid', highlightthickness=0)
    retrieve_button.grid(row=4, column=0, pady=20)

# Window for calculating metrics
def metrics_window():
    metrics_win = Toplevel(root)
    metrics_win.title("Calculate Metrics")
    metrics_win.configure(bg='black')

    cover_image_label_font = font.Font(family='Arial', size=14, weight='bold', underline=0)
    cover_image_label = Label(metrics_win, text="Original Image", font=cover_image_label_font, bg='black', fg='limegreen')
    cover_image_label.grid(row=0, column=0, sticky="w", padx=120, pady=10)

    global cover_image_panel
    cover_image_panel = Label(metrics_win, bg='black')
    cover_image_panel.grid(row=1, column=0, padx=50, pady=10)

    global cover_image_name_label
    cover_image_name_label = Label(metrics_win, text="", font=cover_image_label_font, bg='black', fg='white')
    cover_image_name_label.grid(row=2, column=0, sticky="w", padx=120, pady=10)

    cover_image_button_font = font.Font(family='Arial', size=12, weight='bold')
    cover_image_button = Button(metrics_win, text="Select Original Image", command=select_cover_image, font=cover_image_button_font, bg='darkgrey', fg='black', borderwidth=1, relief='solid', highlightthickness=0)
    cover_image_button.grid(row=3, column=0, padx=10, pady=10)

    steganographed_image_label_font = font.Font(family='Arial', size=14, weight='bold', underline=0)
    steganographed_image_label = Label(metrics_win, text="Steganographed Image", font=steganographed_image_label_font, bg='black', fg='limegreen')
    steganographed_image_label.grid(row=0, column=1, sticky="w", padx=120, pady=10)

    global steganographed_image_panel
    steganographed_image_panel = Label(metrics_win, bg='black')
    steganographed_image_panel.grid(row=1, column=1, padx=50, pady=10)

    global steganographed_image_name_label
    steganographed_image_name_label = Label(metrics_win, text="", font=steganographed_image_label_font, bg='black', fg='white')
    steganographed_image_name_label.grid(row=2, column=1, sticky="w", padx=120, pady=10)

    steganographed_image_button_font = font.Font(family='Arial', size=12, weight='bold')
    steganographed_image_button = Button(metrics_win, text="Select Steganographed Image", command=select_steganographed_image, font=steganographed_image_button_font, bg='darkgrey', fg='black', borderwidth=1, relief='solid', highlightthickness=0)
    steganographed_image_button.grid(row=3, column=1, padx=10, pady=10)

    calculate_button_font = font.Font(family='Helvetica', size=16, weight='bold', slant='italic')
    calculate_button = Button(metrics_win, text="Calculate Metrics", command=calculate_metrics, font=calculate_button_font, bg='darkgrey', fg='black', borderwidth=1, relief='solid', highlightthickness=0)
    calculate_button.grid(row=4, column=0, columnspan=2, pady=20)

    mse_psnr_label_font = font.Font(family='Times', size=16, weight='normal')
    global mse_label
    mse_label = Label(metrics_win, text="MSE: ", font=mse_psnr_label_font, bg='black', fg='snow')
    mse_label.grid(row=5, column=0, columnspan=2, pady=15)

    global psnr_label
    psnr_label = Label(metrics_win, text="PSNR: ", font=mse_psnr_label_font, bg='black', fg='snow')
    psnr_label.grid(row=6, column=0, columnspan=2, pady=15)

if __name__ == "__main__":
    main_window()
