import json
import os
import pickle
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from functions.process_file import process_file
from helpers.create_folder import create_folder_if_not_exist
from helpers.db import db_connection
from helpers.delete_empty_logs import delete_empty_logs

class ExcelFileProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel File Processor")
        self.selected_files = self.load_selected_files()

        self.selected_file = ''
        self.notebook = ttk.Notebook(self.root)  # Create a notebook widget
        self.notebook.pack(fill='both', expand=True, padx=6, pady=6)

        # Create a dictionary to store database settings
        self.database_settings = {
            "Local": {
                "hostname": "",
                "username": "",
                "password": "",
                "database": "",
                "port": ""
            },
            "Live": {
                "hostname": "",
                "username": "",
                "password": "",
                "database": "",
                "port": ""
            }
        }

        self.center_window(700, 300)

        # delete empty log files
        delete_empty_logs('log_files')

        # create folders if not exist
        create_folder_if_not_exist('sample_files')
        create_folder_if_not_exist('record_files')
        create_folder_if_not_exist('log_files')

        
        # Create tabs
        self.create_file_tab()
        self.create_database_settings_tab()
        self.create_log_tab()
        self.update_listbox()

        self.load_database_settings()  # Load settings when the app starts
        # self.toggle_port_entry(None)  # Call the method to handle the initial state

        self.root.configure(bg='#f0f0f0')  # Set background color

    # Make app window to center screen
    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Load already processed file to check weather file is processed or not
    def load_selected_files(self):
        try:
            with open('record_files/selected_files.pkl', 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return []

    # Save seleted file for record which files already processed
    def save_selected_files(self):
        with open('record_files/selected_files.pkl', 'wb') as f:
            pickle.dump(self.selected_files, f)

    # Create a tab for Excel File Processing
    def create_file_tab(self):
        file_tab = ttk.Frame(self.notebook)
        self.notebook.add(file_tab, text='ExcelFileProcessing')  # Add the new tab to the notebook

        file_frame = tk.Frame(file_tab, bg='#f0f0f0')
        file_frame.pack(padx=20, pady=(20, 0))

        self.file_label = tk.Label(file_frame, text="No file selected", bg='#f0f0f0')
        self.file_label.pack()

        self.listbox = tk.Listbox(file_tab, width=70, bg='#ffffff', selectbackground='#b3d9ff')
        self.listbox.pack(side=tk.RIGHT, padx=20, pady=20)

        scrollbar = tk.Scrollbar(file_tab, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        process_frame = tk.Frame(file_tab, bg='#f0f0f0')
        process_frame.pack(anchor='w', padx=20)  # Align frame to the left

        # Vertically center align the radio buttons within the process_frame
        process_frame.pack_propagate(False)  # Prevent frame from resizing
        process_frame.pack(fill=tk.BOTH, pady=(40, 0))  # Center align vertically

        self.process_choice = tk.StringVar()
        json_radio = tk.Radiobutton(process_frame, text="Generate JSON File", variable=self.process_choice, value="json")
        db_radio = tk.Radiobutton(process_frame, text="Insert into Database", variable=self.process_choice, value="db")
        
        json_radio.grid(row=0, column=0, sticky='w')
        db_radio.grid(row=1, column=0, sticky='w')

        self.process_choice.set("db")  # Default choice

        choose_button = tk.Button(process_frame, text="Choose Excel File", command=self.choose_file, bg='#4caf50', fg='white')
        choose_button.grid(row=2, column=0, pady=10, sticky='w')

        proceed_button = tk.Button(process_frame, text="Proceed", command=self.proceed, bg='#f44336', fg='white')
        proceed_button.grid(row=3, column=0, sticky='w')

        # Bind double-click event on listbox to choose the file
        self.listbox.bind("<Double-1>", self.choose_file_from_listbox)
    
    # Create a tab for viewing log files
    def create_log_tab(self):
        log_tab = ttk.Frame(self.notebook)
        self.notebook.add(log_tab, text='LogViewer')  # Add the new tab to the notebook


        log_text = tk.Text(log_tab, wrap=tk.WORD, width=60, height=10)
        log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        open_log_button = tk.Button(log_tab, text="Open Log File", command=self.open_log_file, bg='#ff9800', fg='white')
        open_log_button.pack(anchor='e')

    # Open and display the log file
    def open_log_file(self):
        file_name = self.selected_file.split('/')[-1]
        # log_file_path = f'log_files/{file_name}_missing.log'  # Replace with the actual log file path
        log_file_path = f'log_files/error_log.log'  # Replace with the actual log file path
        try:
            with open(log_file_path, 'r') as log_file:
                log_content = log_file.read()
                log_tab = self.notebook.tab(2, "text")  # Assuming the log tab is the third tab (0-indexed)
                self.notebook.select(2)  # Switch to the log tab
                log_text_widget = self.notebook.winfo_children()[2].winfo_children()[0]  # Access the Text widget
                log_text_widget.delete(1.0, tk.END)  # Clear existing content in the Text widget
                log_text_widget.insert(tk.END, log_content)  # Insert the log content
        except FileNotFoundError:
            messagebox.showwarning("Log File Not Found", "The log file does not exist.")

    def create_database_settings_tab(self):
        database_tab = ttk.Frame(self.notebook)
        self.notebook.add(database_tab, text='Database Settings')
        self.create_database_settings_ui(database_tab)

    # Inside the create_database_settings_ui method:

    def create_database_settings_ui(self, parent_frame):
        database_frame = tk.Frame(parent_frame, bg='#f0f0f0')
        database_frame.pack(padx=20, pady=(20, 0))

        # Database Hostname Label and Entry
        self.hostname_label = tk.Label(database_frame, text="Database Hostname:", bg='#f0f0f0')
        self.hostname_label.grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.hostname_entry = tk.Entry(database_frame)
        self.hostname_entry.grid(row=0, column=1, padx=(0, 20))

        # Database Username Label and Entry
        self.username_label = tk.Label(database_frame, text="Username:", bg='#f0f0f0')
        self.username_label.grid(row=1, column=0, sticky='w', padx=(0, 10))
        self.username_entry = tk.Entry(database_frame)
        self.username_entry.grid(row=1, column=1, padx=(0, 20))

        # Database Password Label and Entry
        self.password_label = tk.Label(database_frame, text="Password:", bg='#f0f0f0')
        self.password_label.grid(row=2, column=0, sticky='w', padx=(0, 10))
        self.password_entry = tk.Entry(database_frame, show="*")  # Use show="*" to hide the password
        self.password_entry.grid(row=2, column=1, padx=(0, 20))

        # Database Username Label and Entry
        self.database_label = tk.Label(database_frame, text="Database Name:", bg='#f0f0f0')
        self.database_label.grid(row=3, column=0, sticky='w', padx=(0, 10))
        self.database_entry = tk.Entry(database_frame)
        self.database_entry.grid(row=3, column=1, padx=(0, 20))

        # Create a Label for Port
        self.port_label = tk.Label(database_frame, text="Port:", bg='#f0f0f0')
        self.port_label.grid(row=4, column=0, sticky='w', padx=(0, 10))

        # Create an Entry for Port
        self.port_entry = tk.Entry(database_frame)
        self.port_entry.grid(row=4, column=1, padx=(0, 20))
        # self.port_entry.grid_remove()  # Initially hide the port entry field

        # Database Type Label and Combobox (Local/Live)
        self.db_type_label = tk.Label(database_frame, text="Database Type:", bg='#f0f0f0')
        self.db_type_label.grid(row=5, column=0, sticky='w', padx=(0, 10))
        self.db_type_combobox = ttk.Combobox(database_frame, values=("Local", "Live"))
        self.db_type_combobox.grid(row=5, column=1, padx=(0, 20))
        self.db_type_combobox.set("Local")  # Set the default value to "Local"
        self.db_type_combobox.bind("<<ComboboxSelected>>", self.toggle_port_entry)

        # Save Database Settings Button
        save_button = tk.Button(database_frame, text="Save Settings", command=self.save_database_settings, bg='#2196F3', fg='white')
        save_button.grid(row=6, column=0, columnspan=2, pady=20)

        # Save Database Settings Button
        test_button = tk.Button(database_frame, text="Test Connection", command=self.test_database_connection, bg='#2196F3', fg='white')
        test_button.grid(row=7, column=0, columnspan=2, pady=20)

    def test_database_connection(self):
        selected_db_type = self.db_type_combobox.get()
        db_connection( selected_db_type, True)

    # # Add this method to your class
    def toggle_port_entry(self, event):
        self.load_database_settings()
    #     selected_db_type = self.db_type_combobox.get()
    #     if selected_db_type == "Live":
    #         self.port_entry.grid()
    #     else:
    #         self.port_entry.grid_remove()

    def save_database_settings(self):
        selected_db_type = self.db_type_combobox.get()

        # Get values from the database settings widgets
        hostname = self.hostname_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        database = self.database_entry.get()
        port = self.port_entry.get()  # Get the port value

        # Update the database settings dictionary based on the selected database type
        self.database_settings[selected_db_type]["hostname"] = hostname
        self.database_settings[selected_db_type]["username"] = username
        self.database_settings[selected_db_type]["password"] = password
        self.database_settings[selected_db_type]["database"] = database
        self.database_settings[selected_db_type]["port"] = port

        # Save the database settings to a JSON file
        settings_filename = 'record_files/database_settings.json'
        try:
            with open(settings_filename, 'w') as settings_file:
                json.dump(self.database_settings, settings_file, indent=4)
            messagebox.showinfo("Settings Saved", "Database settings have been saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving settings: {str(e)}")


    def load_database_settings(self):
        # Load database settings from the JSON file (if it exists)
        settings_filename = 'record_files/database_settings.json'
        try:
            with open(settings_filename, 'r') as settings_file:
                self.database_settings = json.load(settings_file)
                selected_db_type = self.db_type_combobox.get()
                
                # Set the values in the widgets based on the selected database type
                self.hostname_entry.delete(0, tk.END)
                self.hostname_entry.insert(0, self.database_settings[selected_db_type].get("hostname", ""))
                self.username_entry.delete(0, tk.END)
                self.username_entry.insert(0, self.database_settings[selected_db_type].get("username", ""))
                self.password_entry.delete(0, tk.END)
                self.password_entry.insert(0, self.database_settings[selected_db_type].get("password", ""))
                self.database_entry.delete(0, tk.END)
                self.database_entry.insert(0, self.database_settings[selected_db_type].get("database", ""))
                self.port_entry.delete(0, tk.END)
                self.port_entry.insert(0, self.database_settings[selected_db_type].get("port", ""))
        except FileNotFoundError:
            pass  # Settings file doesn't exist yet, use defaults


    # Update listbox when file is processed to show processed file
    def update_listbox(self):
        self.listbox.delete(0, tk.END)  # Clear the listbox
        for file_path in self.selected_files:
            self.listbox.insert(tk.END, file_path)

    # A method to processed Excel file
    def proceed(self):
        selected_db_type = self.db_type_combobox.get()
        if not self.selected_files:
            messagebox.showinfo("File Not Selected", "Please select a file before proceeding.")
            return
        
        current_selected_file = self.selected_file # self.file_label.cget("text")[len("Selected File:"):]
        if current_selected_file.strip() not in self.selected_files:
            messagebox.showinfo("File Not Recorded", "The current selected file has not been recorded. It will only be processed this time.")
        
        process_type = self.process_choice.get()
        success = process_file(current_selected_file, process_type, selected_db_type)
        if success:
            messagebox.showinfo("Process Complete", "Congratulations! The process has been completed successfully.")
        else:
            messagebox.showerror("Error", "There was an error during the process.")
    
    # Choose an Excel file from you storage
    def choose_file(self):
        file_path = filedialog.askopenfilename(title="Choose an Excel file", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            if file_path in self.selected_files:
                messagebox.showinfo("File Already Selected", "You have already selected this file.")
            else:
                self.selected_file = file_path
                self.selected_files.append(file_path)
                self.save_selected_files()
                self.file_label.config(text="Selected File: " + file_path)
                self.update_listbox()
        else:
            self.file_label.config(text="No file selected")

    # Choose an Excel file from you previous processed files
    def choose_file_from_listbox(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_index = int(selected_index[0])
            selected_file = self.selected_files[selected_index]

            if os.path.exists(selected_file):
                if self.file_processed(selected_file):
                    proceed = messagebox.askyesno("File Processed", "This file has already been processed and stored in the database. Do you want to proceed again?")
                    if proceed:
                        self.process_choice.set("db")  # Reset process choice
                        self.file_label.config(text="Selected File: " + selected_file)
                        self.selected_file = selected_file
                        self.update_listbox()  # Highlight the selected file
                else:
                    self.file_label.config(text="Selected File: " + selected_file)
                    self.selected_file = selected_file
                    self.update_listbox()  # Highlight the selected file
                    self.process_choice.set("db")  # Reset process choice
            else:
                messagebox.showwarning("File Not Found", "The selected file path does not exist.")
                remove_confirm = messagebox.askyesno("File Not Found", f"The selected file '{selected_file.split('/')[-1]}' was not found. Do you want to remove it from the list?")
                if remove_confirm:
                    self.selected_files.pop(selected_index)
                    self.save_selected_files()
                    self.update_listbox()  # Update the listbox after removing the file
        else:
            messagebox.showwarning("No File Selected", "Please select a file from the listbox.")

    # Check files is already processed or not
    def file_processed(self, file_path):
        return file_path in self.selected_files


if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelFileProcessorApp(root)
    root.mainloop()
