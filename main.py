import os
import uuid
import tempfile
import subprocess
import seaborn as sns
import cv2 as cv
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import analyze_func as img_func
import dataset_predict as predict
import dataset_analysis


def raise_frame(next_frame):
    next_frame.tkraise()


def on_close():
    root.quit()
    root.destroy()


def select_img():
    # Select image file
    filename = filedialog.askopenfilename(
        title="Select An Image",
        filetypes=(("Image", "*.png"), ("Image", "*.jpg"), ("Image", "*.jpeg"))
    )
    if filename:
        # Read image file
        global img_name
        global original_img
        img_name = os.path.basename(filename)
        img_pil = Image.open(filename)
        img = cv.cvtColor(np.array(img_pil), cv.COLOR_RGB2BGR)
        original_img = img
        if img is not None:
            raise_frame(f_main)
            plot_img_hist(img, f_main_left_top, 7, 3)
            display_image(img, f_main_right_top)
            # Get image parameter values
            WB_red, WB_green, WB_blue = img_func.get_white_balance(img)
            average_brightness = img_func.get_brightness(img)
            contrast = img_func.get_contrast(img)
            average_hue = img_func.get_hue(img)
            average_saturation = img_func.get_saturation(img)
            average_perceived_brightness = img_func.get_perceived_avg_brightness(img)
            average_sharpen = img_func.get_sharpness(img)
            average_highlights = img_func.get_highlights(img)
            average_shadow = img_func.get_shadows(img)
            average_temperature = img_func.get_color_temperature(img)
            average_noisy = img_func.get_noise(img)
            average_exposure = img_func.get_exposure(img)
            # Display image parameter values
            parameters = {
                "Red": WB_red,
                "Green": WB_green,
                "Blue": WB_blue,
                "Contrast": contrast,
                "Brightness": average_brightness,
                "Perceived Brightness": average_perceived_brightness,
                "Hue": average_hue,
                "Saturation": average_saturation,
                "Sharpness": average_sharpen,
                "Highlight": average_highlights,
                "Shadow": average_shadow,
                "Temperature": average_temperature,
                "Noise": average_noisy,
                "Exposure": average_exposure
            }
            display_parameters(f_main_left_bottom, parameters, img)


def display_parameters(frame, parameters, img):
    # Clear previous content
    for widget in frame.winfo_children():
        widget.destroy()

    global img_buffer
    img_buffer = img

    # Create a scrollable canvas
    canvas = ctk.CTkCanvas(frame, highlightthickness=0, bg="white")
    scrollbar = ctk.CTkScrollbar(frame, fg_color="white", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color="white")
    scrollable_frame.bind("<Configure>", lambda e=None: canvas.configure(scrollregion=canvas.bbox("all")))

    # Function to change background color on focus
    def on_focus_in(event):
        event.widget.configure(foreground="black")

    def on_focus_out(event):
        event.widget.configure(foreground="gray")

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the canvas and scrollbar
    canvas.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
    scrollbar.pack(side=ctk.LEFT, fill=ctk.Y)

    # Adding parameters to the scrollable frame
    for i, (param, value) in enumerate(parameters.items()):
        # Parameter's name label
        label = ctk.CTkLabel(scrollable_frame, text=f"{param}", anchor="w", fg_color="white")
        label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

        # Parameter's value textbox
        value_str = f"{value}"
        textbox = ctk.CTkTextbox(scrollable_frame, height=1, width=160, wrap="none", fg_color="#f0f0f0",
                                 text_color="gray")
        textbox.insert("1.0", value_str)
        textbox.grid(row=i, column=1, padx=10, pady=5, sticky="w")

        # Bind focus in and focus out events
        textbox.bind("<FocusIn>", on_focus_in)
        textbox.bind("<FocusOut>", on_focus_out)
        textbox.bind("<FocusOut>",
                     lambda event=None, param1=param, textbox1=textbox: param_updator(param1, textbox1))

    scrollable_frame.update_idletasks()


def param_updator(param, textbox):
    # Get new parameter value
    try:
        new_val = float(textbox.get("1.0", "end-1c"))
    except ValueError:
        messagebox.showerror("Invalid input", f"Invalid value for {param}: {textbox.get('1.0', 'end-1c')}")
        return
    # Pass it to its corresponding 'modify' function
    global img_buffer
    modified_img = None
    if param == "Red":
        modified_img = img_func.modify_white_balance(img_buffer, new_val, -1, -1)
    elif param == "Green":
        modified_img = img_func.modify_white_balance(img_buffer, -1, new_val, -1)
    elif param == "Blue":
        modified_img = img_func.modify_white_balance(img_buffer, -1, -1, new_val)
    elif param == "Contrast":
        modified_img = img_func.modify_contrast(img_buffer, new_val)
    elif param == "Brightness":
        modified_img = img_func.modify_brightness(img_buffer, new_val)
    elif param == "Perceived Brightness":
        modified_img = img_func.modify_perceived_avg_brightness(img_buffer, new_val)
    elif param == "Hue":
        modified_img = img_func.modify_hue(img_buffer, new_val)
    elif param == "Saturation":
        modified_img = img_func.modify_saturation(img_buffer, new_val)
    elif param == "Sharpness":
        modified_img = img_func.modify_sharpness(img_buffer, new_val)
    elif param == "Highlight":
        modified_img = img_func.modify_highlights(img_buffer, new_val)
    elif param == "Shadow":
        modified_img = img_func.modify_shadows(img_buffer, new_val)
    elif param == "Temperature":
        modified_img = img_func.modify_color_temperature(img_buffer, new_val)
    if param == "Noise":
        modified_img = img_func.modify_noise(img_buffer, new_val)
    elif param == "Exposure":
        modified_img = img_func.modify_exposure(img_buffer, new_val)
    else:
        pass
    # Update img_buffer & Refresh the window
    if modified_img is not None:
        img_buffer = modified_img
        plot_img_hist(img_buffer, f_main_left_top, 7, 3)
        display_image(img_buffer, f_main_right_top)


def display_image(img, frame):
    # Clear previous image
    for widget in frame.winfo_children():
        widget.destroy()

    # Convert the image to RGB format
    img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)

    # Get the height and width of the image
    height, width = img.shape[:2]

    # Calculate the maximum width and height
    if height > width:
        max_width = 380
    else:
        max_width = 500
    img_ratio = width / height
    max_height = int(max_width / img_ratio)

    # Display image in the frame
    img_tk = ctk.CTkImage(img_pil, size=(max_width, max_height))
    label = ctk.CTkLabel(frame, image=img_tk, text="")
    label.image = img_tk
    label.pack(padx=10, pady=10, fill='x')


def plot_img_hist(img, frame, width, height):
    # Clear previous plots
    for widget in frame.winfo_children():
        widget.destroy()

    plt.figure(figsize=(width, height))

    # Plot grayscale hist
    plt.hist(img.ravel(), 256, [0, 256])
    # Plot color hist
    color = ('blue', 'green', 'red')
    for i, color in enumerate(color):
        hist = cv.calcHist([img], [i], None, [256], [0, 256])
        plt.plot(hist, color=color)

    plt.xlabel("Bins")
    plt.ylabel("Pixel Number")

    # Hide the top and right spines
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Get the current figure & draw & close
    figure = plt.gcf()
    canvas = FigureCanvasTkAgg(figure, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    plt.close()


def revert_to_original():
    # Revert to original_img
    global original_img
    plot_img_hist(original_img, f_main_left_top, 7, 3)
    display_image(original_img, f_main_right_top)
    # Get image parameter values
    WB_red, WB_green, WB_blue = img_func.get_white_balance(original_img)
    average_brightness = img_func.get_brightness(original_img)
    contrast = img_func.get_contrast(original_img)
    average_hue = img_func.get_hue(original_img)
    average_saturation = img_func.get_saturation(original_img)
    average_perceived_brightness = img_func.get_perceived_avg_brightness(original_img)
    average_sharpen = img_func.get_sharpness(original_img)
    average_highlights = img_func.get_highlights(original_img)
    average_shadow = img_func.get_shadows(original_img)
    average_temperature = img_func.get_color_temperature(original_img)
    average_noisy = img_func.get_noise(original_img)
    average_exposure = img_func.get_exposure(original_img)
    # Display image parameter values
    parameters = {
        "Red": WB_red,
        "Green": WB_green,
        "Blue": WB_blue,
        "Contrast": contrast,
        "Brightness": average_brightness,
        "Perceived Brightness": average_perceived_brightness,
        "Hue": average_hue,
        "Saturation": average_saturation,
        "Sharpness": average_sharpen,
        "Highlight": average_highlights,
        "Shadow": average_shadow,
        "Temperature": average_temperature,
        "Noise": average_noisy,
        "Exposure": average_exposure
    }
    display_parameters(f_main_left_bottom, parameters, original_img)


def auto_optimize():
    # Get current image
    global img_buffer
    # Check filter data availability
    json_dataset_path = ".\\dataset\\" + combobox.get() + "\\" + combobox.get() + "_result.json"
    if not os.path.exists(json_dataset_path):
        tk.messagebox.showinfo("Cannot find dataset",
                               "Cannot find json data file for this dataset. Check & Update Dataset.")
        return
    # Get image parameter values
    WB_red, WB_green, WB_blue = img_func.get_white_balance(img_buffer)
    avg_brightness = img_func.get_brightness(img_buffer)
    contrast = img_func.get_contrast(img_buffer)
    avg_hue = img_func.get_hue(img_buffer)
    avg_saturation = img_func.get_saturation(img_buffer)
    avg_perceived_brightness = img_func.get_perceived_avg_brightness(img_buffer)
    avg_sharpness = img_func.get_sharpness(img_buffer)
    avg_highlights = img_func.get_highlights(img_buffer)
    avg_shadow = img_func.get_shadows(img_buffer)
    avg_temperature = img_func.get_color_temperature(img_buffer)
    avg_noisy = img_func.get_noise(img_buffer)
    avg_exposure = img_func.get_exposure(img_buffer)

    # Pass the parameters & Predict optimal values
    optimal_vals = predict.optimal_val_predict(json_dataset_path, contrast, WB_red, WB_green, WB_blue,
                                               avg_brightness, avg_perceived_brightness, avg_hue,
                                               avg_saturation, avg_sharpness, avg_highlights, avg_shadow,
                                               avg_temperature, avg_noisy, avg_exposure)

    # Ensure optimal_vals contains scalar values
    optimal_vals = {key: val.item() if isinstance(val, pd.Series) else val for key, val in optimal_vals.items()}

    # Modify image with optimal values
    modified_img = img_func.modify_hue(img_buffer, optimal_vals["avg_hue"])
    modified_img = img_func.modify_sharpness(modified_img, optimal_vals["avg_sharpness"])
    modified_img = img_func.modify_color_temperature(modified_img, optimal_vals["avg_temperature"])
    modified_img = img_func.modify_exposure(modified_img, optimal_vals["avg_exposure"])
    modified_img = img_func.modify_white_balance(modified_img, optimal_vals["WB_red"],
                                                 optimal_vals["WB_green"], optimal_vals["WB_blue"])
    modified_img = img_func.modify_contrast(modified_img, optimal_vals["contrast"])
    modified_img = img_func.modify_saturation(modified_img, optimal_vals["avg_saturation"])
    modified_img = img_func.modify_highlights(modified_img, optimal_vals["avg_highlights"])
    modified_img = img_func.modify_noise(modified_img, optimal_vals["avg_noisy"])
    modified_img = img_func.modify_brightness(modified_img, optimal_vals["avg_brightness"])
    modified_img = img_func.modify_shadows(modified_img, optimal_vals["avg_shadow"])
    modified_img = img_func.modify_perceived_avg_brightness(modified_img, optimal_vals["avg_perceived_brightness"])

    # Update Window
    if modified_img is not None:
        img_buffer = modified_img
        plot_img_hist(img_buffer, f_main_left_top, 7, 3)
        display_image(img_buffer, f_main_right_top)
        # Display image parameter values
        parameters = {
            "Red": WB_red,
            "Green": WB_green,
            "Blue": WB_blue,
            "Contrast": contrast,
            "Brightness": avg_brightness,
            "Perceived Brightness": avg_perceived_brightness,
            "Hue": avg_hue,
            "Saturation": avg_saturation,
            "Sharpness": avg_sharpness,
            "Highlight": avg_highlights,
            "Shadow": avg_shadow,
            "Temperature": avg_temperature,
            "Noise": avg_noisy,
            "Exposure": avg_exposure
        }
        display_parameters(f_main_left_bottom, parameters, img_buffer)


def export_img():
    if img_buffer is not None:
        # Create a temporary address & Pass the temporarily stored image file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Encode the original image name using UTF-8
            if all(ord(char) < 128 for char in img_name):
                # If all characters in img_name are ASCII characters
                encoded_img_name = img_name.encode('utf-8')
            else:
                # If img_name contains non-ASCII characters
                name, extension = os.path.splitext(img_name)
                uuid_bytes = str(uuid.uuid4()).encode('utf-8')
                encoded_img_name = uuid_bytes + extension.encode('utf-8')
                encoded_img_name_str = encoded_img_name.decode('utf-8')
            tmp_file_path = os.path.join(temp_dir, encoded_img_name_str)
            cv.imwrite(tmp_file_path, img_buffer)
            # Start Export Window
            try:
                subprocess.run(['python', 'export_func.py', tmp_file_path], capture_output=True, text=True)
            except Exception as e:
                messagebox.showerror("Exception", "Error occurred: " + str(e))


def dataset_select(value):
    # Load the dataset
    json_dataset_path = os.path.join(".\\dataset", value, f"{value}_result.json")
    if not os.path.exists(json_dataset_path):
        tk.messagebox.showinfo("Cannot find dataset",
                               "Cannot find json data file for this dataset. Check & Update Dataset.")
        return
    stats, original_stats = dataset_analysis.dataset_desc(json_dataset_path)

    # Create a combobox to select the parameter
    parameter_label = ctk.CTkLabel(f_dataset, text="Select Parameter:")
    parameter_label.pack(padx=20, pady=10, anchor="w")

    # Clear previous widgets
    for widget in f_dataset.winfo_children():
        if widget != home and widget != update and widget != crawler and widget != combobox_m:
            widget.destroy()

    # Display the box plot of all numeric columns
    plt.figure(figsize=(18, 4))
    plt.xticks(fontsize=8)
    sns.boxplot(data=original_stats, color='blue')
    plt.ylabel('Values')
    plt.grid(True)
    plt.tight_layout()
    boxplot_canvas = FigureCanvasTkAgg(plt.gcf(), master=f_dataset)
    boxplot_canvas.draw()
    boxplot_canvas.get_tk_widget().pack()
    plt.close()

    # Update & Pack parameter_combobox
    global parameter_combobox
    parameter_combobox = ctk.CTkComboBox(f_dataset, values=stats['Parameter'].tolist(),
                                         command=lambda param: display_parameter_stats(param, stats,
                                                                                       parameter_combobox))
    parameter_combobox.pack(padx=20, pady=10, fill="x")

    # Initial display of the first parameter's stats
    if not stats.empty:
        display_parameter_stats(stats['Parameter'].iloc[0], stats, parameter_combobox)


def display_parameter_stats(param, stats, parameter_combobox):
    # Find the row corresponding to the selected parameter
    param_stats = stats[stats['Parameter'] == param]
    if param_stats.empty:
        return

    # Extract the parameter stats
    param_values = param_stats.iloc[0].to_dict()
    for widget in f_dataset.winfo_children():
        if isinstance(widget, (ctk.CTkCanvas, ctk.CTkScrollbar)) and widget != parameter_combobox:
            widget.destroy()

    # Create a canvas and a scrollbar
    canvas = ctk.CTkCanvas(f_dataset, bg="white", highlightthickness=0)
    scrollbar = ctk.CTkScrollbar(f_dataset, fg_color="white", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color="white")
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    # Place the scrollable frame in the canvas
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the canvas and scrollbar
    canvas.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
    scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)

    # Display the stats for the selected parameter inside the scrollable frame
    for key, value in param_values.items():
        if key == 'Parameter':
            continue
        # Parameter name label
        label = ctk.CTkLabel(scrollable_frame, text=f"{key}:", anchor="w", fg_color="white")
        label.pack(padx=20, pady=5, anchor="w")

        # Parameter value textbox
        value_str = f"{value:.4f}" if isinstance(value, (int, float)) else f"{value}"
        textbox = ctk.CTkTextbox(scrollable_frame, height=1, width=160, wrap="none", fg_color="#f0f0f0",
                                 text_color="black")
        textbox.insert("1.0", value_str)
        textbox.pack(padx=20, pady=5, anchor="w")
        textbox.configure(state="disabled")

        # Display the histogram for the parameter
        plt.figure(figsize=(6, 4))
        sns.histplot(data=stats[key].dropna(), kde=True, bins=30, color='blue')
        plt.ylabel('Frequency')
        plt.grid(True)
        plt.tight_layout()
        hist_canvas = FigureCanvasTkAgg(plt.gcf(), master=scrollable_frame)
        hist_canvas.draw()
        hist_canvas.get_tk_widget().pack()
        plt.close()


def dataset_update():
    # Create waiting window
    update.configure(text="Processing", fg_color="red")
    update.update()
    # Start Tasks
    img_func.process_images_in_folders(root_dir)
    global subfolders
    subfolders = [sub_folder for sub_folder in os.listdir(root_dir) if
                  os.path.isdir(os.path.join(root_dir, sub_folder))]
    combobox.configure(values=subfolders)
    combobox_m.configure(values=subfolders)
    combobox.update()
    combobox_m.update()
    dataset_select(combobox_m.get())
    # End Waiting Window
    update.configure(text="Update Dataset", fg_color="#3b8ed0")
    update.update()


if __name__ == "__main__":
    # Main window
    img_buffer = None
    bg_color = "white"
    root = ctk.CTk(bg_color)
    root.title("Image Optimizer")
    root.minsize(800, 500)
    root.iconbitmap('./icon/icon.ico')
    root.protocol("WM_DELETE_WINDOW", on_close)

    # Frames
    f_wizard = ctk.CTkFrame(root, fg_color=bg_color)
    f_main = ctk.CTkFrame(root, fg_color=bg_color)
    f_dataset = ctk.CTkFrame(root, fg_color=bg_color)

    for f in (f_wizard, f_main, f_dataset):
        f.grid(row=0, column=0, sticky="nsew")

    # Configure grid to expand
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Predefined root directory
    root_dir = "./dataset"
    subfolders = [sub_folder for sub_folder in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, sub_folder))]

    # Wizard Interface
    f_wizard_bg_color = "white"

    # Wizard Interface Left
    f_wizard_left = ctk.CTkFrame(f_wizard, fg_color=f_wizard_bg_color)
    f_wizard_left.grid(row=0, column=0, sticky="nsew")
    f_wizard_left.grid_rowconfigure(0, weight=1)
    f_wizard_left.grid_columnconfigure(0, weight=1)

    # Wizard Interface Right
    f_wizard_right = ctk.CTkFrame(f_wizard, fg_color=f_wizard_bg_color)
    f_wizard_right.grid(row=0, column=1, sticky="nsew")
    f_wizard_right.grid_rowconfigure(0, weight=1)
    f_wizard_right.grid_columnconfigure(0, weight=1)

    # Configure grid in f_wizard
    f_wizard.grid_rowconfigure(0, weight=1)
    f_wizard.grid_columnconfigure(0, weight=1)
    f_wizard.grid_columnconfigure(1, weight=1)

    # Load Wizard Interface Icons
    icon_select = ctk.CTkImage(Image.open("./icon/select.png"), size=(100, 100))
    icon_db_man = ctk.CTkImage(Image.open("./icon/edit.png"), size=(100, 100))

    # Buttons with icons and custom styles
    select_img_button = ctk.CTkButton(
        f_wizard_left, text="Select An Image", command=select_img,
        image=icon_select, compound="top", fg_color="transparent", text_color="black", hover_color="lightblue"
    )
    select_img_button.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    db_manage_button = ctk.CTkButton(
        f_wizard_right, text="Dataset Management", command=lambda: raise_frame(f_dataset),
        image=icon_db_man, compound="top", fg_color="transparent", text_color="black", hover_color="lightblue"
    )
    db_manage_button.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    # Main Interface
    f_main_bg_color = "white"

    # Main Interface Left
    f_main_left = ctk.CTkFrame(f_main, fg_color=f_main_bg_color)
    f_main_left.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    f_main_left.grid_rowconfigure(0, weight=1)
    f_main_left.grid_rowconfigure(1, weight=1)  # Button
    f_main_left.grid_columnconfigure(0, weight=1)

    # Main Interface Left Top
    f_main_left_top = ctk.CTkFrame(f_main_left, fg_color=f_main_bg_color)
    f_main_left_top.grid(row=0, column=0, sticky="nsew")
    f_main_left_top.grid_rowconfigure(0, weight=1)
    f_main_left_top.grid_columnconfigure(0, weight=1)

    # Main Interface Left Bottom
    f_main_left_bottom = ctk.CTkFrame(f_main_left, fg_color=f_main_bg_color)
    f_main_left_bottom.grid(row=1, column=0, sticky="nsew")  # Button
    f_main_left_bottom.grid_rowconfigure(0, weight=1)
    f_main_left_bottom.grid_columnconfigure(0, weight=1)

    # Main Interface Right
    f_main_right = ctk.CTkFrame(f_main, fg_color=f_main_bg_color)
    f_main_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    f_main_right.grid_rowconfigure(0, weight=1)
    f_main_right.grid_rowconfigure(1, weight=1)
    f_main_right.grid_columnconfigure(0, weight=1)

    # Main Interface Right Top
    f_main_right_top = ctk.CTkFrame(f_main_right, fg_color=f_main_bg_color)
    f_main_right_top.grid(row=0, column=0, sticky="nsew")
    f_main_right_top.grid_rowconfigure(0, weight=1)
    f_main_right_top.grid_columnconfigure(0, weight=1)

    # Main Interface Right Bottom
    f_main_right_bottom = ctk.CTkFrame(f_main_right, fg_color=f_main_bg_color)
    f_main_right_bottom.grid(row=1, column=0, sticky="nsew")
    f_main_right_bottom.grid_rowconfigure(0, weight=1)
    f_main_right_bottom.grid_columnconfigure(0, weight=1)

    # Combobox to display sub-folder names
    combobox = ctk.CTkComboBox(f_main_right_bottom, values=subfolders)
    combobox.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

    auto_button = ctk.CTkButton(f_main_right_bottom, text="Auto Optimization", command=auto_optimize)
    auto_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

    revert_button = ctk.CTkButton(f_main_right_bottom, text="Revert To Original", command=lambda: revert_to_original())
    revert_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

    export_button = ctk.CTkButton(f_main_right_bottom, text="Export Image", command=export_img)
    export_button.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

    export_button = ctk.CTkButton(f_main_right_bottom, text="Discard", command=lambda: raise_frame(f_wizard))
    export_button.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

    # Configure grid in f_main
    f_main.grid_rowconfigure(0, weight=1)
    f_main.grid_columnconfigure(0, weight=1)
    f_main.grid_columnconfigure(1, weight=1)

    # Database Management Interface
    # Back To Wizard Button
    home = ctk.CTkButton(f_dataset, text="Back To Wizard", command=lambda: raise_frame(f_wizard))
    home.pack(padx=20, pady=5, fill='x')

    # Crawler Button
    crawler = ctk.CTkButton(f_dataset, text="Get More Images from Unsplash",
                            command=lambda: subprocess.run(['python', 'crawler.py']))
    crawler.pack(padx=20, pady=5, fill='x')

    # Dataset Update Button
    update = ctk.CTkButton(f_dataset, text="Update Dataset", command=dataset_update)
    update.pack(padx=20, pady=5, fill='x')

    # Combobox to display sub-folder names
    combobox_m = ctk.CTkComboBox(f_dataset, values=subfolders, command=lambda value: dataset_select(value))
    combobox_m.pack(padx=20, pady=5, fill='x')
    dataset_select(combobox_m.get())

    raise_frame(f_wizard)
    root.mainloop()
