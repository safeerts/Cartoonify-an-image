import tkinter as tk
from tkinter import filedialog
import cv2
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('image_data.db')
cursor = conn.cursor()

# Create a table to store image data if it doesn't exist already
cursor.execute('''CREATE TABLE IF NOT EXISTS images 
                (id INTEGER PRIMARY KEY, filename TEXT, processed_image_path TEXT, timestamp TIMESTAMP)''')

def cartoonify(image_path):
    # Read the image
    img = cv2.imread(image_path)

    # Convert image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply median blur to smooth the image
    gray = cv2.medianBlur(gray, 7)

    # Detect edges using adaptive thresholding
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

    # Apply bilateral filter to reduce noise while keeping edges sharp
    color = cv2.bilateralFilter(img, 9, 75, 75)

    # Combine the edges with the original color image
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    return cartoon



def create_main_window():
    def upload_image():
        nonlocal example_label, cartoon_label
        file_path = filedialog.askopenfilename()
        if file_path:
            # Cartoonify the image
            cartoon_image = cartoonify(file_path)

            # Resize the uploaded image and cartoonified version to fit within a certain dimension
            uploaded_image = cv2.imread(file_path)
            uploaded_image_resized = resize_image(uploaded_image)
            cartoon_image_resized = resize_image(cartoon_image)

            # Convert the cartoon image to PhotoImage format compatible with Tkinter
            cartoon_image_tk = cv2_to_photoimage(cartoon_image_resized)

            # Display the cartoon image
            cartoon_label.config(image=cartoon_image_tk)
            cartoon_label.image = cartoon_image_tk

            # Convert the uploaded image to PhotoImage format compatible with Tkinter
            uploaded_image_tk = cv2_to_photoimage(uploaded_image_resized)

            # Display the uploaded image
            example_label.config(image=uploaded_image_tk)
            example_label.image = uploaded_image_tk

            # Update text
            example_text.config(text="Here is the result!")

            # Insert image data into the database
            insert_image_data(file_path, "processed_image.jpg")  # Assuming processed image path

    def insert_image_data(filename, processed_image_path):
        cursor.execute('''INSERT INTO images (filename, processed_image_path, timestamp) 
                        VALUES (?, ?, CURRENT_TIMESTAMP)''', (filename, processed_image_path))
        conn.commit()

    def retrieve_image_data():
        cursor.execute('''SELECT * FROM images''')
        return cursor.fetchall()

    main_window = tk.Tk()
    main_window.title("Main Window")

    # Set window background color and border radius
    main_window.configure(bg="#2c3e50")
    main_window.attributes("-alpha", 0.95)
    main_window.attributes("-topmost", True)

    # Load and display example image
    example_image_path = r"C:\Users\safee\Desktop\Projects\Cartoonify-an-image\WhatsApp Image 2024-03-10 at 10.52.19 PM.jpeg"  # Update this with your example image path
    example_image = cv2.imread(example_image_path)
    example_image_resized = resize_image(example_image)
    example_image_tk = cv2_to_photoimage(example_image_resized)
    example_label = tk.Label(main_window, image=example_image_tk, bg="#2c3e50")
    example_label.pack(side="left", padx=10, pady=10)

    # Display cartoonified example image
    cartoon_example_image = cartoonify(example_image_path)
    cartoon_example_image_resized = resize_image(cartoon_example_image)
    cartoon_example_image_tk = cv2_to_photoimage(cartoon_example_image_resized)
    cartoon_label = tk.Label(main_window, image=cartoon_example_image_tk, bg="#2c3e50")
    cartoon_label.pack(side="left", padx=10, pady=10)

    # Add "Here is an example for you" text
    example_text = tk.Label(main_window, text="Here is an example for you!", font=("Arial", 12), bg="#2c3e50", fg="white")
    example_text.pack(pady=10)

    # Create a button to upload an image
    upload_button = tk.Button(main_window, text="Upload Image", command=upload_image, bg="#3498db", fg="white", activebackground="#2980b9", activeforeground="white", relief="flat")
    upload_button.pack(pady=10)

    # Instruction label
    instruction_label = tk.Label(main_window, text="Please upload an image to cartoonify.\nAcceptable formats: JPG, PNG, BMP.\nMaximum size: 5MB", bg="#2c3e50", fg="white")
    instruction_label.pack(pady=10)

    main_window.mainloop()

def resize_image(image):
    # Get the dimensions of the image
    height, width, _ = image.shape

    # Calculate the scaling factor to fit the image within the desired dimensions
    max_width = 400  # Maximum width for the image
    max_height = 300  # Maximum height for the image
    scale = min(max_width / width, max_height / height)

    # Resize the image
    resized_image = cv2.resize(image, (int(width * scale), int(height * scale)))

    return resized_image

def cv2_to_photoimage(cv2_image):
    # Convert the OpenCV image array to RGB format
    cv2_image_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)

    # Convert the RGB image array to a byte array
    height, width, channels = cv2_image_rgb.shape
    image_bytes = cv2_image_rgb.tobytes()

    # Create a Tkinter PhotoImage object from the byte array
    image_tk = tk.PhotoImage(width=width, height=height)

    # For each pixel, set its color in the PhotoImage object
    index = 0
    for y in range(height):
        for x in range(width):
            # Get the RGB values for the current pixel
            r, g, b = image_bytes[index], image_bytes[index + 1], image_bytes[index + 2]
            # Convert RGB values to hexadecimal color
            color = f'#{r:02x}{g:02x}{b:02x}'
            # Set the color of the pixel in the PhotoImage object
            image_tk.put(color, (x, y))
            # Move to the next pixel
            index += 3

    return image_tk

create_main_window()
