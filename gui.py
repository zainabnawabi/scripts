import tkinter as tk

# 1. Initialize the main window
root = tk.Tk()
root.title("Simple Tkinter GUI")
root.geometry("400x200")  # Width x Height in pixels

# 2. Define an action for the button click
def on_button_click():
    # Retrieve text from the input field
    user_input = entry.get()
    # Update the greeting label with the user's text
    result_label.config(text=f"Hello, {user_input}!")

# 3. Create and place a text label
label = tk.Label(root, text="Enter your name:", font=("Arial", 12))
label.pack(pady=10)  # pady adds vertical spacing

# 4. Create and place an interactive input field
entry = tk.Entry(root, font=("Arial", 12))
entry.pack(pady=5)

# 5. Create and place a clickable button
button = tk.Button(root, text="Greet Me", command=on_button_click, font=("Arial", 10))
button.pack(pady=10)

# 6. Create a placeholder label to display the output
result_label = tk.Label(root, text="", font=("Arial", 12, "bold"), fg="blue")
result_label.pack(pady=10)

# 7. Start the main event loop to keep the window open
root.mainloop()
