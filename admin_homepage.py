import customtkinter as ctk
import time
from PIL import Image
import sys
import os
import threading
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
import ZODB
import ZODB.FileStorage
import BTrees
import transaction
from  library_management import ReturnRecord,BorrowRecord, Book, User
from common_functions import edit_user_information as edit_user, edit_book_information as edit_book
from datetime import datetime
import matplotlib.pyplot as plt
from math import pi
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class AdminHomepage(ctk.CTkFrame):  
    def __init__(self, master):  # Add master parameter
        super().__init__(master)
        self.master = master  # Store reference to master window
        
        # Initialize database connection
        self.db_lock = threading.Lock()
        self.setup_database()

        self.Genres = [
            "Science & Technology",
            "Humanities",
            "Social Sciences",
            "Business",
            "Medicine & Health",
            "Arts",
            "Math & Statistics",
            "Languages & Literature",
            "Environmental Studies",
            "Reference"
        ]

        self.Faculties=[
                "Faculty of Engineering",
                "Faculty of Architecture",
                "Faculty of Science",
                "Faculty of Agricultural Technology",
                "Faculty of Information Technology",
                "Faculty of Industrial Education",
                "Faculty of Business Administration",
                "Faculty of Liberal Arts",
                "Faculty of Medicine"]
        self.COLORS = {
            'primary': '#339af0',
            'primary_dark': '#1971c2',
            'primary_light': '#a5d8ff',
            'secondary': '#f0f4ff',
            'text_primary': '#1b1f23',
            'text_secondary': '#5c6975',
            'white': '#ffffff',
            'border': '#d0e1ff',
            'hover': '#e9f4ff',
            'input_bg': '#d0e1ff',
            'input_border': '#5c6975'
        }

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.load_logo()
        self.setup_ui()
    
    


    def setup_database(self):
        """Initialize database connection with proper error handling"""
        try:
            self.storage = ZODB.FileStorage.FileStorage('library.fs')
            self.db = ZODB.DB(self.storage)
            self.connection = self.db.open()
            self.dbroot = self.connection.root()
            
            # Initialize BTrees if they don't exist
            if not hasattr(self.dbroot, 'books'):
                self.dbroot.books = BTrees.OOBTree.BTree()
            if not hasattr(self.dbroot, 'users'):
                self.dbroot.users = BTrees.OOBTree.BTree()
            transaction.commit()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
            self.destroy()
            sys.exit(1)

    def close_database(self):
        """Safely close database connections"""
        try:
            if hasattr(self, 'connection') and self.connection is not None:
                self.connection.close()
                self.connection = None
            if hasattr(self, 'db') and self.db is not None:
                self.db.close()
                self.db = None
            if hasattr(self, 'storage') and self.storage is not None:
                self.storage.close()
                self.storage = None
        except Exception as e:
            print(f"Error closing database: {e}")

    def load_logo(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(current_dir, "logos", "kmitlgo.png")
            
            self.logo = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(80, 80)
            )
        except:
            print("Logo file not found")
            self.logo = None

    def setup_ui(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=self.COLORS['secondary'], width=60)
        self.sidebar.pack(side="left", fill="y", padx=2, pady=2)
        self.sidebar.pack_propagate(False)
        
        self.main_content = ctk.CTkFrame(self, fg_color=self.COLORS['primary_dark'])
        self.main_content.pack(side="right", fill="both", expand=True, padx=2, pady=2)
        
        self.create_sidebar()
        self.create_header()
        self.create_stats_widgets()
        self.create_parallel_lists()

    def create_sidebar(self):
        # Add a separator line on the right
        separator = ctk.CTkFrame(
            self.sidebar,
            width=2,                          
            fg_color=self.COLORS['border'],        
            corner_radius=0                   
        )
        separator.place(relx=1, rely=0, relheight=1, anchor="ne")  
        
        # Menu items with icons only
        menu_items = [        
            ("📋", "history", "Borrow & Return Records"),
            ("👥", "user_statistics", "User Statistics"),
            ("📊", "book_statistics", "Book Statistics"),
            (" ↪️", "logout", "Log Out"),
            ("❌", "exit", "Exit")
        ]
        
        padding_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=20)
        padding_frame.pack(pady=(20, 0))
        
        for icon, command, tooltip_text in menu_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=icon,
                width=40,  # Fixed width for square buttons
                height=40,  # Fixed height for square buttons
                fg_color="transparent",
                hover_color=self.COLORS['hover'],
                corner_radius=8,
                font=ctk.CTkFont(size=20),
                text_color=self.COLORS['text_secondary'],
                command=lambda x=command: self.menu_click(x)
            )
            btn.pack(pady=5)
            
            # Create tooltip
            self.create_tooltip(btn, tooltip_text)

    def create_tooltip(self, widget, text):
        """Create tooltip for sidebar buttons"""
        def enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 20}+{event.y_root}")
            
            label = ctk.CTkLabel(
                tooltip,
                text=text,
                fg_color=self.COLORS['primary_dark'],
                corner_radius=6,
                text_color=self.COLORS['white'],
                padx=10,
                pady=5
            )
            label.pack()
            
            widget.tooltip = tooltip
            
        def leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def create_header(self):
        header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        # Logo in header
        if self.logo:
            logo_label = ctk.CTkLabel(header, image=self.logo, text="")
            logo_label.pack(side="left", padx=(0, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            header,
            text="KMITL Library Management System",
            font=("Arial Bold", 24)
        )
        title_label.pack(side="left")

    def get_borrowed_book_count(self):
        """Get total number of borrowed books across all users"""
        borrowed_count = 0
        if hasattr(self.dbroot, 'users'):
            for user in self.dbroot.users.values():
                borrowed_count += len(user.borrowed_books)
        return borrowed_count

    def get_overdue_book_count(self):
        """Get total number of overdue books for the current user"""
        overdue_count = 0
        current_date = datetime.now()
        if hasattr(self.dbroot, 'users'):
            for user in self.dbroot.users.values():
                user_id=user.user_id
                if hasattr(self.dbroot, 'borrow_records'):
                    for record_id, borrow_record in self.dbroot.borrow_records.items():
                        if borrow_record.user_id == user_id:
                            # Check if the book has been returned
                            is_returned = False
                            if hasattr(self.dbroot, 'all_records'):
                                for return_record in self.dbroot.all_records.values():
                                    if isinstance(return_record, ReturnRecord) and \
                                    return_record.isbn == borrow_record.isbn and \
                                    return_record.user_id == borrow_record.user_id and \
                                    return_record.date > borrow_record.date:
                                        is_returned = True
                                        break
                            
                            # If book hasn't been returned and is overdue, increment counter
                            if not is_returned and hasattr(borrow_record, 'end_date') and \
                            borrow_record.end_date < current_date:
                                overdue_count += 1
                        
        return overdue_count
    
    def create_stats_widgets(self):
        stats_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20)

        # Borrowed Books widget
        self.borrowed_frame = ctk.CTkFrame(stats_frame, fg_color=self.COLORS['white'])
        self.borrowed_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        borrowed_count = self.get_borrowed_book_count()
        ctk.CTkLabel(self.borrowed_frame, text=str(borrowed_count), font=("Arial Bold", 28),
                    text_color=self.COLORS['primary']).pack(pady=10)
        ctk.CTkLabel(self.borrowed_frame, text="Borrowed Books",
                    text_color=self.COLORS['text_secondary']).pack()

        # Overdue Books widget
        self.overdue_frame = ctk.CTkFrame(stats_frame, fg_color=self.COLORS['white'])
        self.overdue_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        overdue_count = self.get_overdue_book_count()
        ctk.CTkLabel(self.overdue_frame, text=str(overdue_count), font=("Arial Bold", 28),
                    text_color=self.COLORS['primary']).pack(pady=10)
        ctk.CTkLabel(self.overdue_frame, text="Overdue Books",
                    text_color=self.COLORS['text_secondary']).pack()

    def create_parallel_lists(self):
        lists_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        lists_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Users List (Left)
        self.users_frame = ctk.CTkFrame(lists_container, fg_color=self.COLORS['white'])
        self.users_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.users_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        users_header = ctk.CTkFrame(self.users_frame, fg_color="transparent")
        users_header.pack(fill="x", padx=15, pady=15)
        
        header_container = ctk.CTkFrame(users_header, fg_color="transparent")
        header_container.pack(fill="x")
        
        ctk.CTkLabel(
            header_container,
            text="Users List",
            font=("Arial Bold", 16)
        ).pack(side="left")

        # Add New User button
        add_user_btn = ctk.CTkButton(
            header_container,
            text="Add New User",
            fg_color=self.COLORS['primary'],
            hover_color=self.COLORS['primary_dark'],
            command=self.open_add_user_window
        )
        add_user_btn.pack(side="right", padx=10)

        # Add Refresh button for users
        refresh_users_btn = ctk.CTkButton(
            header_container,
            text="🔄",
            width=40,
            height=40,
            fg_color='transparent',
            text_color="black",
            hover_color=self.COLORS['primary_dark'],
            command=self.refresh_user_list
        )
        refresh_users_btn.pack(side="right", padx=(0, 10))

        # Create initial users table
        self.create_table(
            self.users_frame,
            ["User ID", "User Name", "Borrowed Books", "Faculty", "Action"],
            self.get_user_data(),
            is_user_list=True
        )
        # Books List (Right)
        self.books_frame = ctk.CTkFrame(lists_container, fg_color=self.COLORS['white'])
        self.books_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.books_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        books_header = ctk.CTkFrame(self.books_frame, fg_color="transparent")
        books_header.pack(fill="x", padx=15, pady=15)
        
        header_container = ctk.CTkFrame(books_header, fg_color="transparent")
        header_container.pack(fill="x")
        
        ctk.CTkLabel(
            header_container,
            text="Books List",
            font=("Arial Bold", 16)
        ).pack(side="left")

        # Add New Book button
        add_book_btn = ctk.CTkButton(
            header_container,
            text="Add New Book",
            fg_color=self.COLORS['primary'],
            hover_color=self.COLORS['primary_dark'],
            command=self.open_add_book_window
        )
        add_book_btn.pack(side="right", padx=10)

        # Modified Refresh button without text
        refresh_btn = ctk.CTkButton(
            header_container,
            text="🔄",
            width=40,
            height=40,
            fg_color='transparent',
            text_color="black",
            hover_color=self.COLORS['primary_dark'],
            command=self.refresh_book_list
        )
        refresh_btn.pack(side="right", padx=(0, 10))

        # Create initial books table
        self.create_table(
            self.books_frame,
            ["Book ID", "Title", "Author", "Available", "Action"],
            self.get_book_data(),
            is_user_list=False
        )
    def handle_action_click(self, event, tree, row_id, is_user_list):
        """Handle action column clicks"""
        column = tree.identify_column(event.x)
        item = tree.identify_row(event.y)
        
        if column == f'#{len(tree["columns"])}' and item == row_id:  # Only trigger for action column
            # Get the item values
            item_values = tree.item(row_id)['values']
            
            # Calculate menu position
            x = event.x_root
            y = event.y_root
            
            # Show appropriate menu
            if is_user_list:
                self.show_user_menu(x, y, item_values[0])
            else:
                self.show_book_menu(x, y, item_values[0])

    def create_table(self, parent, columns, data, is_user_list=True):
        frame_width = self.borrowed_frame.winfo_width()-25 #25 for scroll bar
        
        # Create Treeview with fixed height
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=10)
        
        # Style configuration
        style = ttk.Style()
        style.configure("Treeview", 
                    background=self.COLORS['white'],
                    foreground=self.COLORS['text_primary'],
                    rowheight=40,
                    fieldbackground=self.COLORS['white'])
        style.configure("Treeview.Heading", 
                    background=self.COLORS['white'],
                    foreground=self.COLORS['text_secondary'],
                    padding=10)
        
        
        # Set column headings and widths
        for col in columns:
            tree.heading(col, text=col)
            w=frame_width//len(columns)
            if col == "Action" or col=="Borrowed Books" or col=="Available":  # Make action column narrower
                w = w // 2
            tree.column(col, anchor='center' if col == "Action" or col=="Borrowed Books" or col=="Available" else 'w', width=w)
            
        
        
        for row in data:
            values = list(row[:-1])  # Exclude the last item (action column)
            values.append("⚙️")  # Add button-like symbol
            item = tree.insert('', 'end', values=values)
            
           # Bind click event specifically to the action column
            tree.tag_configure(f'action_{item}', foreground=self.COLORS['text_primary'])
            tree.tag_bind(f'action_{item}', '<Button-1>', 
                        lambda e, rid=item: self.handle_action_click(e, tree, rid, is_user_list))
            
            # Apply the tag only to the action column
            tree.set(item, 'Action', "⚙️")
            tree.item(item, tags=(f'action_{item}',))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the tree and scrollbar
        tree.pack(side="left", fill="both", expand=True, pady=(0,15))
        scrollbar.pack(side="right", fill="y", pady=(0,15), padx=(0,15))
        
    
        return tree
    
    def open_add_user_window(self):
        """Create add user window with proper frame configuration"""
        self.add_user_window = ctk.CTkToplevel(self)
        self.add_user_window.title("Add New User")
        
        # Configure window
        self.add_user_window.transient(self)
        self.add_user_window.grab_set()
        screen_width = self.add_user_window.winfo_screenwidth()
        screen_height = self.add_user_window.winfo_screenheight()
        self.add_user_window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.add_user_window.resizable(False, False)
        self.add_user_window.state('zoomed')
        
        # Configure grid
        self.add_user_window.grid_columnconfigure(0, weight=1)
        self.add_user_window.grid_rowconfigure(1, weight=1)
        
        # Header frame
        header_frame = ctk.CTkFrame(self.add_user_window, fg_color=self.COLORS['primary'], height=70)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(2, weight=1)
        header_frame.grid_propagate(False)
        
        # Home button
        home_button = ctk.CTkButton(
            header_frame,
            text=" 🏠 Home",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=self.COLORS['white'],
            hover_color="#2b7fd9",
            width=100,
            height=30,
            command=self.add_user_window.destroy
        )
        home_button.grid(row=0, column=0, padx=(10, 0), pady=10)
        
        # Logo
        logo = self.load_logo_add()
        if logo:
            logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
            logo_label.grid(row=0, column=1, padx=(20, 10), pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="KMITL Library Management System",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.COLORS['white']
        )
        title_label.grid(row=0, column=2, padx=20, pady=10, sticky="w")

        # Main content frame
        main_frame = ctk.CTkFrame(self.add_user_window, fg_color=self.COLORS['secondary'])
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure((0, 1), weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Page title
        page_title = ctk.CTkLabel(
            main_frame,
            text="Add New User",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.COLORS['text_primary']
        )
        page_title.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="n")

        # Left frame - Image upload
        left_frame = ctk.CTkFrame(main_frame, fg_color=self.COLORS['white'])
        left_frame.grid(row=1, column=0, sticky="nsew", padx=10)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)

        # Preview frame
        self.preview_frame = ctk.CTkFrame(
            left_frame, 
            fg_color=self.COLORS['input_bg'],
            height=400,
            width=300,
            border_width=1,
            border_color=self.COLORS['input_border']
        )
        self.preview_frame.grid(row=0, column=0, padx=20, pady=20, sticky="n")
        self.preview_frame.grid_propagate(False)

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="User Photo Preview",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS['text_primary']
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # Upload button
        upload_button = ctk.CTkButton(
            left_frame,
            text="Upload Photo",
            font=ctk.CTkFont(size=14),
            fg_color=self.COLORS['primary'],
            command=self.browse_image,
            width=200
        )
        upload_button.grid(row=1, column=0, pady=10)

        # Right frame - User information
        right_frame = ctk.CTkFrame(main_frame, fg_color=self.COLORS['white'])
        right_frame.grid(row=1, column=1, sticky="nsew", padx=10)
        right_frame.grid_columnconfigure(0, weight=1)

        # User information fields
        self.create_input_field(right_frame, "User ID:", "user_id_var", placeholder="Enter 6-digit user ID")
        self.create_input_field(right_frame, "Full Name:", "name_var", placeholder="Enter full name")
        self.create_input_field(right_frame, "Phone Number:", "ph_number_var", placeholder="Enter phone number")
        self.create_date_field(right_frame, "Birthdate:", "birthdate_var")
        self.create_password_field(right_frame, "Password:", "password_var", placeholder="Enter at least 6 characters")
        self.create_faculty_selector(right_frame)

        # Add User button
        add_button = ctk.CTkButton(
            right_frame,
            text="Add User",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.COLORS['primary'],
            command=self.add_user,
            width=200
        )
        add_button.grid(row=10, column=0, pady=20)


    def create_password_field(self, parent, label, var_name, placeholder=""):
        frame = ctk.CTkFrame(parent, fg_color=self.COLORS['white'])
        frame.grid(sticky="ew", pady=(0, 10), padx=20)
        frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS['text_primary'],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        setattr(self, var_name, ctk.StringVar())
        entry = ctk.CTkEntry(
            frame,
            textvariable=getattr(self, var_name),
            fg_color=self.COLORS['input_bg'],
            border_color=self.COLORS['input_border'],
            border_width=1,
            height=30,
            placeholder_text=placeholder
            #show="●"  # Show dots instead of actual characters
        )
        entry.grid(row=1, column=0, sticky="ew")

    def load_logo_add(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(current_dir, "logos", "kmitlgo.png")
            
            return ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(50, 50)
            )
        except Exception as e:
            print(f"Error loading logo: {e}")
            return None
    
    def browse_image(self):
        """Handle image upload"""
        filename = filedialog.askopenfilename(
            title="Select  Photo",
            filetypes=(
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("All files", "*.*")
            )
        )
        if filename:
            self.image_path = filename
            self.update_image_preview(filename)
        
    def update_image_preview(self, image_path):
        """Update the image preview"""
        try:
            if hasattr(self, 'preview_label'):
                self.preview_label.destroy()
            img = Image.open(image_path)
            display_size = (280, 380)
            img.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            
            label = ctk.CTkLabel(self.preview_frame, image=photo, text="")
            label.image = photo
            label.place(relx=0.5, rely=0.5, anchor="center")
            self.preview_label = label
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.image_path = None

    def create_faculty_selector(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.COLORS['white'])
        frame.grid(sticky="ew", pady=(0, 10), padx=20)
        frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame,
            text="Faculty:",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS['text_primary'],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        self.faculty_var = ctk.StringVar(value="Select Faculty")
        self.faculty_selector = ctk.CTkOptionMenu(
            frame,
            values=self.Faculties,
            variable=self.faculty_var,
            fg_color=self.COLORS['input_bg'],
            button_color=self.COLORS['primary'],
            button_hover_color=self.COLORS['secondary'],
            text_color=self.COLORS['text_primary'],
            dynamic_resizing=False,
            width=200
        )
        self.faculty_selector.grid(row=1, column=0, sticky="ew")

    def create_date_field(self, parent, label, var_name):
        frame = ctk.CTkFrame(parent, fg_color=self.COLORS['white'])
        frame.grid(sticky="ew", pady=(0, 10), padx=20)
        frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS['text_primary'],
            anchor="w"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 2))
        
        # Create variables for day, month, and year
        self.day_var = ctk.StringVar(value="Day")
        self.month_var = ctk.StringVar(value="Month")
        self.year_var = ctk.StringVar(value="Year")
        
        # Create dropdown menus
        days = [str(i).zfill(2) for i in range(1, 32)]
        months = [str(i).zfill(2) for i in range(1, 13)]
        current_year = datetime.now().year
        years = [str(i) for i in range(current_year - 35, current_year + 1)]
        
        day_menu = ctk.CTkOptionMenu(
            frame,
            variable=self.day_var,
            values=days,
            fg_color=self.COLORS['input_bg'],
            text_color=self.COLORS['text_primary'],
            button_color=self.COLORS['primary'],
            width=100
        )
        month_menu = ctk.CTkOptionMenu(
            frame,
            variable=self.month_var,
            values=months,
            fg_color=self.COLORS['input_bg'],
            text_color=self.COLORS['text_primary'],
            button_color=self.COLORS['primary'],
            width=100
        )
        year_menu = ctk.CTkOptionMenu(
            frame,
            variable=self.year_var,
            values=years,
            fg_color=self.COLORS['input_bg'],
            text_color=self.COLORS['text_primary'],
            button_color=self.COLORS['primary'],
            width=100
        )
        
        day_menu.grid(row=1, column=0, padx=5)
        month_menu.grid(row=1, column=1, padx=5)
        year_menu.grid(row=1, column=2, padx=5)

    def validate_ph_number(self, phone):
        # Validate phone number format (adjust pattern as needed)
        pattern = r'^[0-9]{10}$'
        return re.match(pattern, phone) is not None

    def validate_user_id(self, user_id):
        return user_id.isdigit() and len(user_id)>=6
    
    def validate_birthdate(self):
        try:
            day = int(self.day_var.get())
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            datetime(year, month, day)
            return True
        except ValueError:
            return False

    def add_user(self):
        try:
            # Get form data
            user_id = self.user_id_var.get().strip()
            name = self.name_var.get().strip()
            ph_number = self.ph_number_var.get().strip()
            faculty = self.faculty_var.get()
            password = self.password_var.get()
      

            if not self.validate_birthdate():
                messagebox.showerror("Error", "Invalid birthdate!")

                return
            birthdate = f"{self.year_var.get()}-{self.month_var.get()}-{self.day_var.get()}"
            # Validate all fields
            if not all([user_id, name, ph_number, birthdate, faculty, password]):
                messagebox.showerror("Error", "All fields are required!")
                return
                
            if not self.validate_user_id(user_id):
                messagebox.showerror("Error", "User ID must be at least 6 digits")
                return
                
            if not self.validate_ph_number(ph_number):
                messagebox.showerror("Error", "Invalid  Phone Number !")
                return
                
            if faculty == "Select Faculty":
                messagebox.showerror("Error", "Please select a faculty!")
                return
                
        
            if len(password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters!")
                return
            
            # Refresh database connection
            self.close_database()
            self.setup_database()

            # Check if user already exists
            if hasattr(self.dbroot, 'users') and user_id in self.dbroot.users:
                messagebox.showerror("Error", "User ID already exists!")
                return

            # Create new user
            new_user = User(str(user_id), str(name),str(ph_number), str(faculty))
            new_user.birthdate=str(birthdate)
            new_user.set_password(str(password))

            # Add image if available
            if self.image_path:
                with open(self.image_path, 'rb') as f:
                    new_user.image_data = f.read()
            
            # Initialize users BTree if it doesn't exist
            if not hasattr(self.dbroot, 'users'):
                self.dbroot.users = BTrees.OOBTree.BTree()
                
            self.dbroot.users[user_id] = new_user
            transaction.commit()
            
            messagebox.showinfo("Success", "User added successfully!")
            self.user_clear_fields()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add user: {e}")
            transaction.abort()
        finally:
                self.close_database()

    def user_clear_fields(self):
        self.user_id_var.set("")
        self.name_var.set("")
        self.ph_number_var.set("")
        self.faculty_selector.set("Select Faculty")
        self.password_var.set("")
        self.day_var.set("Day")
        self.month_var.set("Month")
        self.year_var.set("Year")
        self.image_path = None
        # Clear image preview
        if hasattr(self, 'preview_label'):
            self.preview_label.destroy()
            
        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Profile Cover Preview",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS['text_primary']
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")
       

        def __del__(self):
            if hasattr(self, 'connection'):
                self.connection.close()
            if hasattr(self, 'db'):
                self.db.close()
            if hasattr(self, 'storage'):
                self.storage.close()

    def open_add_book_window(self):
        """Create add book window with proper frame configuration"""
        self.add_book_window = ctk.CTkToplevel(self)
        self.add_book_window.title("Add New Book")
        
        # Configure window
        self.add_book_window.transient(self)
        self.add_book_window.grab_set()
        screen_width = self.add_book_window.winfo_screenwidth()
        screen_height = self.add_book_window.winfo_screenheight()
        self.add_book_window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.add_book_window.resizable(False, False)
        self.add_book_window.state('zoomed')
        
        # Configure grid
        self.add_book_window.grid_columnconfigure(0, weight=1)
        self.add_book_window.grid_rowconfigure(1, weight=1)
        
        # Header frame
        header_frame = ctk.CTkFrame(self.add_book_window, fg_color=self.COLORS['primary'], height=70)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(2, weight=1)
        header_frame.grid_propagate(False)
        
        # Home button
        home_button = ctk.CTkButton(
            header_frame,
            text=" 🏠 Back",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=self.COLORS['white'],
            hover_color="#2b7fd9",
            width=100,
            height=30,
            command=self.add_book_window.destroy
        )
        home_button.grid(row=0, column=0, padx=(10, 0), pady=10)
        
        # Logo
        logo = self.load_logo_add()
        if logo:
            logo_label = ctk.CTkLabel(header_frame, image=logo, text="")
            logo_label.grid(row=0, column=1, padx=(20, 10), pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="KMITL Library Management System",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.COLORS['white']
        )
        title_label.grid(row=0, column=2, padx=20, pady=10, sticky="w")

        # Main content frame
        main_frame = ctk.CTkFrame(self.add_book_window, fg_color=self.COLORS['secondary'])
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure((0, 1), weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Page title
        page_title = ctk.CTkLabel(
            main_frame,
            text="Add New Book",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.COLORS['text_primary']
        )
        page_title.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="n")

        # Left frame - Image upload
        left_frame = ctk.CTkFrame(main_frame, fg_color=self.COLORS['white'])
        left_frame.grid(row=1, column=0, sticky="nsew", padx=10)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)

        # Preview frame
        self.preview_frame = ctk.CTkFrame(
            left_frame, 
            fg_color=self.COLORS['input_bg'],
            height=400,
            width=300,
            border_width=1,
            border_color=self.COLORS['input_border']
        )
        self.preview_frame.grid(row=0, column=0, padx=20, pady=20, sticky="n")
        self.preview_frame.grid_propagate(False)

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Book Cover Preview",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS['text_primary']
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # Upload button
        upload_button = ctk.CTkButton(
            left_frame,
            text="Upload Cover Image",
            font=ctk.CTkFont(size=14),
            fg_color=self.COLORS['primary'],
            command=self.browse_image,
            width=200
        )
        upload_button.grid(row=1, column=0, pady=10)

        # Right frame - Book information
        right_frame = ctk.CTkFrame(main_frame, fg_color=self.COLORS['white'])
        right_frame.grid(row=1, column=1, sticky="nsew", padx=10)
        right_frame.grid_columnconfigure(0, weight=1)

        # Book information fields
        self.create_input_field(right_frame, "ISBN:", "isbn_var")
        self.create_input_field(right_frame, "Book Name:", "name_var")
        self.create_input_field(right_frame, "Author:", "author_var")
        self.create_genre_selector(right_frame)
        self.create_input_field(right_frame, "Description:", "description_var", is_text=True)
        self.create_input_field(right_frame, "Number of Copies:", "copies_var")

        # Add Book button
        add_button = ctk.CTkButton(
            right_frame,
            text="Add Book",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.COLORS['primary'],
            command=self.add_book,
            width=200
        )
        add_button.grid(row=10, column=0, pady=20)

        
    def create_genre_selector(self, parent):
        """Create a dropdown for genre selection using customtkinter"""
        frame = ctk.CTkFrame(parent, fg_color=self.COLORS['white'])
        frame.grid(sticky="ew", pady=(0, 10), padx=20)
        frame.grid_columnconfigure(0, weight=1)
        
        # Label
        ctk.CTkLabel(
            frame,
            text="Genre:",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS['text_primary'],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        # Create the combobox using CTkOptionMenu
        self.genre_var = ctk.StringVar(value="Select Genre")
        self.genre_selector = ctk.CTkOptionMenu(
            frame,
            values=self.Genres,
            variable=self.genre_var,
            fg_color=self.COLORS['input_bg'],
            button_color=self.COLORS['primary'],
            button_hover_color=self.COLORS['secondary'],
            text_color=self.COLORS['text_primary'],
            dynamic_resizing=False,
            width=200
        )
        self.genre_selector.grid(row=1, column=0, sticky="ew")


    def create_input_field(self, parent, label, var_name, is_text=False, placeholder=""):
        frame = ctk.CTkFrame(parent, fg_color=self.COLORS['white'])
        frame.grid(sticky="ew", pady=(0, 10), padx=20)
        frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS['text_primary'],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        if is_text:
            text_area = ctk.CTkTextbox(
                frame,
                height=60,
                fg_color=self.COLORS['input_bg'],
                border_color=self.COLORS['input_border'],
                border_width=1
            )
            text_area.grid(row=1, column=0, sticky="ew")
            setattr(self, var_name, text_area)
        else:
            setattr(self, var_name, ctk.StringVar())
            entry = ctk.CTkEntry(
                frame,
                textvariable=getattr(self, var_name),
                fg_color=self.COLORS['input_bg'],
                border_color=self.COLORS['input_border'],
                border_width=1,
                height=30,
                placeholder_text=placeholder
            )
            entry.grid(row=1, column=0, sticky="ew")


    def add_book(self):
        """Updated add_book method to work with CTkOptionMenu"""
        with self.db_lock:
            try:
                # Get form data including genre
                isbn = self.isbn_var.get().strip()
                name = self.name_var.get().strip()
                author = self.author_var.get().strip()
                genre = self.genre_var.get()
                description = self.description_var.get("1.0", "end-1c").strip()
                
                try:
                    if int(self.copies_var.get().strip())<=0:
                        raise ValueError
                    copies =  int(self.copies_var.get().strip())
                except ValueError:
                    messagebox.showerror("Error", "Number of copies must be a valid number!")
                    return

                # Validate all fields including genre
                if not all([isbn, name, author, description, copies]):
                    messagebox.showerror("Error", "All fields are required!")
                    return
                    
                if genre == "Select Genre":
                    messagebox.showerror("Error", "Please select a genre!")
                    return

                # Refresh database connection
                self.close_database()
                self.setup_database()

                # Check for existing book
                if hasattr(self.dbroot, 'books') and isbn in self.dbroot.books:
                    response = messagebox.askyesno(
                        "Book Exists",
                        f"This ISBN already exists. Would you like to add {copies} copy/copies to the existing book?"
                    )
                    if response:
                        existing_book = self.dbroot.books[isbn]
                        existing_book.total_copies += copies
                        existing_book.available_copies += copies
                        transaction.commit()
                        messagebox.showinfo("Success", f"Added {copies} copy/copies to existing book.")
                    return

                # Create new book with genre
                book = Book(isbn, name, author, description, copies)
                book.genre = genre  # Add genre to book object
                
                if self.image_path:
                    if not book.set_image(self.image_path):
                        messagebox.showwarning(
                            "Warning", 
                            "Failed to process image, book will be saved without cover."
                        )
                
                if not hasattr(self.dbroot, 'books'):
                    self.dbroot.books = BTrees.OOBTree.BTree()
                    
                self.dbroot.books[isbn] = book
                transaction.commit()
                
                messagebox.showinfo("Success", "Book added successfully!")
                self.book_clear_fields()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add book: {e}")
                transaction.abort()
            finally:
                self.close_database()


    def book_clear_fields(self):
        self.isbn_var.set("")
        self.name_var.set("")
        self.author_var.set("")
        self.genre_selector.set("Select Genre")  # Updated to use set() method
        self.description_var.delete("1.0", "end")
        self.copies_var.set("")
        self.image_path = None
        if hasattr(self, 'preview_label'):
            self.preview_label.destroy()
        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Book Cover Preview",
            font=ctk.CTkFont(size=14),
            text_color=self.COLORS['text_primary']
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        def __del__(self):
            if hasattr(self, 'connection'):
                self.connection.close()
            if hasattr(self, 'db'):
                self.db.close()
            if hasattr(self, 'storage'):
                self.storage.close()

    
    def refresh_book_list(self):
        try:
            """Refresh the book list"""
            for widget in self.books_frame.winfo_children():
                if isinstance(widget, (ttk.Treeview, ttk.Scrollbar)) :
                    widget.destroy()

            self.create_table(
                    self.books_frame,
                    ["Book ID", "Title", "Author", "Available", "Action"],
                    self.get_book_data(),
                    is_user_list=False
                )
           
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh book list : {e}")

   
    def refresh_user_list(self):
        try:
            """Refresh the user list"""
            for widget in self.users_frame.winfo_children():
                if isinstance(widget, (ttk.Treeview, ttk.Scrollbar)):
                    widget.destroy()

            self.create_table(
                    self.users_frame,
                    ["User ID", "User Name", "Borrowed Books", "Faculty", "Action"],
                    self.get_user_data(),
                    is_user_list=True
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh user list : {e}")

    
    def show_user_menu(self, x, y, user_id):
        """Updated user menu with safe action handling"""
        menu = tk.Menu(master=self, tearoff=0)
        menu.configure(bg=self.COLORS['white'], fg=self.COLORS['text_primary'])
        
        menu.add_command(
            label="Edit User Information", 
            command=lambda: self.perform_user_action('edit', user_id)
        )
        menu.add_command(
            label="Reset Points", 
            command=lambda: self.perform_user_action('reset_points', user_id)
        )
        menu.add_command(
            label="Reset Password", 
            command=lambda: self.perform_user_action('reset', user_id)
        )
        menu.add_separator()
        menu.add_command(
            label="Delete User", 
            command=lambda: self.perform_user_action('delete', user_id),
            foreground='red'
        )
        
        menu.post(x, y)

  
    def show_book_menu(self, x, y, book_id):
        """Fixed book menu method with proper parent reference"""
        menu = tk.Menu(master=self, tearoff=0)  # Explicitly set master to self
        menu.configure(bg=self.COLORS['white'], fg=self.COLORS['text_primary'])
        
        menu.add_command(
            label="Edit Book Information", 
            command=lambda: self.edit_book_info(book_id)
        )
        menu.add_separator()
        menu.add_command(
            label="Delete Book", 
            command=lambda: self.delete_book(book_id),
            foreground='red'
        )
        
        menu.post(x, y)  # Use passed coordinates

    def perform_book_action(self, action_type, book_id):
        """Safe wrapper for book actions"""
        actions = {
            'edit': self.edit_book,
            'delete': self.delete_book
        }
        try:
            if action_type in actions:
                actions[action_type](book_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to {action_type} book: {e}")

    def perform_user_action(self, action_type, user_id):
        """Safe wrapper for user actions"""
        actions = {
            'edit': self.edit_user_info,
            'reset_points': self.reset_user_points,
            'reset': self.reset_password,
            'delete': self.delete_user

        }
        try:
            if action_type in actions:
                actions[action_type](user_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to {action_type} user: {e}")

    def get_user_data(self):
        """Fetch user data from database"""
        user_list = []
        with self.db_lock:
            try:
                self.close_database()
                self.setup_database()
                
                if hasattr(self.dbroot, 'users'):
                    for user_id, user in self.dbroot.users.items():
                        user_data = (
                            user_id,
                            user.name,
                            str(len(user.borrowed_books)),
                            user.faculty,
                            ""
                        )
                        user_list.append(user_data)
                    return user_list
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch book data : {e}")
                return []
            finally:
                self.close_database()

    
    def get_book_data(self):
        """Fetch book data with proper locking and connection handling"""
        book_list = []
        with self.db_lock:
            try:
                self.close_database()
                self.setup_database()
                if hasattr(self.dbroot, 'books'):
                    for isbn, book in self.dbroot.books.items():
                        book_data = (
                            isbn,
                            book.name,
                            book.author,
                            str(book.available_copies),
                            ""
                        )
                        book_list.append(book_data)
                    return book_list
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch book data : {e}")
                return []
            finally:
                self.close_database()

    def edit_user_info(self, user_id):
        edit_user(self, str(user_id))

    def edit_book_info(self, book_id):
        edit_book(self, str(book_id))

    def update_profile_button_image(self, processed_image_data):
        pass
        
    def reset_password(self, user_id):
        """Reset user password with proper type handling"""
        try:
            # Ensure user_id is treated as string for dictionary lookup
            user_id = str(user_id)
            
            confirm = messagebox.askyesno(
                "Reset Password", 
                f"Are you sure you want to reset password for user ID {user_id}?"
            )
            
            if confirm:
                with self.db_lock:
                    try:
                        self.close_database()
                        self.setup_database()
                        
                        if hasattr(self.dbroot, 'users') and user_id in self.dbroot.users:
                            user = self.dbroot.users[user_id]
                            default_password = "111111"  
                            user.set_password(default_password)
                            transaction.commit()
                            messagebox.showinfo(
                                "Success", 
                                f"Password has been reset for user {user_id}\nNew password: {default_password}"
                            )
                        else:
                            messagebox.showerror("Error", "User not found!")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to reset password: {e}")
                        transaction.abort()
                    finally:
                        self.close_database()
        except Exception as e:
            messagebox.showerror("Error", f"Error processing user ID: {e}")

    def reset_user_points(self, user_id):
        user_id = str(user_id)
        confirm = messagebox.askyesno(
            "Reset Points", 
            f"Are you sure you want to reset points for user ID {user_id}?"
        )
        if confirm:
            with self.db_lock:
                try:
                    self.close_database()
                    self.setup_database()
                    
                    if hasattr(self.dbroot, 'users') and user_id in self.dbroot.users:
                        user = self.dbroot.users[user_id]
                        user.points = 100
                        transaction.commit()
                        messagebox.showinfo(
                            "Success", 
                            f"Points have been reset for user {user_id}"
                        )

                    else:
                        messagebox.showerror("Error", "User not found!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to reset points: {e}")
                    transaction.abort()
                finally:
                    self.close_database()

    def delete_user(self, user_id):
        """Delete user with improved database handling and refresh mechanism"""
        user_id = str(user_id)
        confirm = messagebox.askyesno(
            "Delete User", 
            f"Are you sure you want to delete user {user_id}?\nThis action cannot be undone."
        )
        if confirm:
            with self.db_lock:
                try:
                    self.close_database()
                    self.setup_database()
                    
                    if hasattr(self.dbroot, 'users') and user_id in self.dbroot.users:
                        del self.dbroot.users[user_id]
                        transaction.commit()
                        messagebox.showinfo("Success", f"User {user_id} has been deleted")
                        # Schedule refresh after a small delay
                        self.master.after(200, self.refresh_user_list)
                    else:
                        messagebox.showerror("Error", "User not found!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete user: {e}")
                    transaction.abort()
                finally:
                    self.close_database()


    def delete_book(self, book_id):
        """Delete book with improved database handling and refresh mechanism"""
        book_id = str(book_id)
        confirm = messagebox.askyesno(
            "Delete Book", 
            f"Are you sure you want to delete book {book_id}?\nThis action cannot be undone."
        )
        if confirm:
            with self.db_lock:
                try:
                    self.close_database()
                    self.setup_database()
                    
                    if hasattr(self.dbroot, 'books') and book_id in self.dbroot.books:
                        del self.dbroot.books[book_id]
                        transaction.commit()
                        messagebox.showinfo("Success", f"Book {book_id} has been deleted")
                        # Schedule refresh after a small delay
                        self.master.after(200, self.refresh_book_list)
                    else:
                        messagebox.showerror("Error", "Book not found!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete book: {e}")
                    transaction.abort()
                finally:
                    self.close_database()

    def menu_click(self, action):
        """Handle menu item clicks"""
        if action == "user_statistics":
            self.show_user_statistics()
        elif action == "history":
            self.show_borrow_return_records()
        elif action == "book_statistics":
            self.show_book_statistics()
        elif action == "logout":
            if messagebox.askyesno("Logout", "Are you sure you want to logout?"):      
                self.logout()

        elif action == "exit":
            if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
                self.destroy()
                self.master.destroy()


    def get_user_data_by_department(self):
        user_data_by_dept = {}
        with self.db_lock:
            try:
                self.close_database()
                self.setup_database()
                
                if hasattr(self.dbroot, 'users'):
                    for user_id, user in self.dbroot.users.items():
                        dept = user.faculty
                        if dept not in user_data_by_dept:
                            user_data_by_dept[dept] = 0
                        user_data_by_dept[dept] += 1
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch user data: {e}")
            finally:
                self.close_database()
        return user_data_by_dept
    
    def show_user_statistics(self):
        stats_window = ctk.CTkToplevel(self)
        stats_window.title("User Statistics")
        stats_window.grab_set()
        
        # Window size
        width = 700
        height = 600
        x = (stats_window.winfo_screenwidth() - width) // 2
        y = (stats_window.winfo_screenheight() - height) // 2
        stats_window.geometry(f"{width}x{height}+{x}+{y}")
        stats_window.resizable(False, False)
        
        main_frame = ctk.CTkScrollableFrame(
            stats_window,
            fg_color=self.COLORS['white'],
            width=width-40,
            height=height-40
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        ctk.CTkLabel(
            main_frame,
            text="User Statistics by Department",
            font=("Arial Bold", 24),
            text_color=self.COLORS['primary']
        ).pack(pady=(0, 10))
        
        try:
            # Get user data by department
            user_data_by_dept = self.get_user_data_by_department()
            
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(8, 4))
            
            # Prepare data for plotting
            labels = list(user_data_by_dept.keys())
            values = list(user_data_by_dept.values())
            
            # Create pie chart
            ax.pie(values, labels=labels, autopct='%1.1f%%')
            ax.axis('equal')
            ax.set_title('')
            
            # Create canvas for matplotlib
            canvas = FigureCanvasTkAgg(fig, master=main_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            print(f"Error displaying user statistics: {e}")
            ctk.CTkLabel(
                main_frame,
                text=f"Error loading user statistics: {str(e)}",
                text_color="red"
            ).pack(pady=20)
        
        # Ensure proper cleanup
        def on_closing():
            try:
                plt.close('all')
                stats_window.destroy()
            except:
                pass
                
        stats_window.protocol("WM_DELETE_WINDOW", on_closing)

    def show_borrow_return_records(self):
        records_window = ctk.CTkToplevel(self)
        records_window.title("Borrow & Return Records")
        records_window.transient(self)
        records_window.grab_set()

        # Set window to fullscreen
        screen_width = records_window.winfo_screenwidth()
        screen_height = records_window.winfo_screenheight()
        records_window.geometry(f"{screen_width}x{screen_height}+0+0")
        records_window.resizable(False, False)
        records_window.state('zoomed')
        records_window.configure(fg_color=self.COLORS['white'])

        # Header frame
        header_frame = ctk.CTkFrame(records_window, fg_color=self.COLORS['primary'], height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        ctk.CTkLabel(
            header_frame,
            text="Borrow & Return Record",
            font=("Arial Bold", 24),
            text_color=self.COLORS['white']
        ).pack(side="left", padx=20, pady=20)

        # Back button
        back_button = ctk.CTkButton(
            header_frame,
            text="Home",
            fg_color=self.COLORS['secondary'],
            hover_color=self.COLORS['hover'],
            text_color=self.COLORS['text_primary'],
            command=records_window.destroy
        )
        back_button.pack(side="right", padx=20, pady=20)

        # Main content frame with scrollable
        content_frame = ctk.CTkScrollableFrame(records_window, fg_color=self.COLORS['white'])
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        try:
            # Open database connection
            self.setup_database()

            # Get all records for all users
            all_records = []

            # Get borrow records
            if hasattr(self.dbroot, 'borrow_records'):
                for record_id, record in self.dbroot.borrow_records.items():
                    all_records.append(record)

            # Get return records
            if hasattr(self.dbroot, 'all_records'):
                for record_id, record in self.dbroot.all_records.items():
                    if isinstance(record, ReturnRecord):
                        all_records.append(record)

            # Sort records by date
            all_records.sort(key=lambda x: x.date)

            # Create a header for the list
            header_label = ctk.CTkLabel(
                content_frame,
                text="Date                                                                Activity",
                font=("Arial Bold", 14),
                anchor="w",
                padx=15,
                pady=10
            )
            header_label.pack(fill="x", padx=10, pady=(0, 10))

            # Display records
            for record in all_records:
                record_frame = ctk.CTkFrame(
                    content_frame,
                    fg_color=self.COLORS['secondary'],
                    corner_radius=10
                )
                record_frame.pack(fill="x", pady=5, padx=10)

                # Get user and book details
                if isinstance(record, BorrowRecord):
                    user = self.dbroot.users.get(record.user_id)
                    book = self.dbroot.books.get(record.isbn)
                    action_text = f"Borrowed Book ID '{record.isbn}' - '{book.name}'" if book else f"Borrowed Unknown Book ID '{record.isbn}'"
                    end_date_text = f" (Due: {record.end_date.strftime('%B %d, %Y')})" if hasattr(record, 'end_date') else ""
                    text_color = self.COLORS['primary']  # Blue for borrows
                elif isinstance(record, ReturnRecord):
                    user = self.dbroot.users.get(record.user_id)
                    book = self.dbroot.books.get(record.isbn)
                    action_text = f"Returned Book ID '{record.isbn}' - '{book.name}'" if book else f"Returned Unknown Book ID '{record.isbn}'"
                    end_date_text = ""
                    text_color = "green"  # Green for returns
                else:
                    continue  # Skip unknown record types

                record_content = ctk.CTkLabel(
                    record_frame,
                    text=f"{record.date.strftime('%Y-%m-%d %I:%M %p')}    {user.name if user else 'Unknown User'} ({record.user_id})    {action_text}{end_date_text}",
                    font=("Arial", 14),
                    text_color=text_color,
                    anchor="w",
                    padx=15,
                    pady=10
                )
                record_content.pack(fill="x")

                # Add hover effect
                def on_enter(e, frame=record_frame):
                    frame.configure(fg_color=self.COLORS['hover'])

                def on_leave(e, frame=record_frame):
                    frame.configure(fg_color=self.COLORS['secondary'])

                record_frame.bind("<Enter>", on_enter)
                record_frame.bind("<Leave>", on_leave)

            if not all_records:
                ctk.CTkLabel(
                    content_frame,
                    text="No borrow or return records found",
                    font=("Arial", 14),
                    text_color=self.COLORS['text_secondary']
                ).pack(pady=20)

        except Exception as e:
            print(f"Error displaying borrow and return records: {e}")
            ctk.CTkLabel(
                content_frame,
                text=f"Error loading records: {str(e)}",
                text_color="red"
            ).pack(pady=20)
        finally:
            # Close database connection
            self.close_database()

    def show_book_statistics(self):
        stats_window = ctk.CTkToplevel(self)
        stats_window.title("Book Statistics")
        stats_window.grab_set()

        # Window size
        width = 800
        height = 700
        x = (stats_window.winfo_screenwidth() - width) // 2
        y = (stats_window.winfo_screenheight() - height) // 2
        stats_window.geometry(f"{width}x{height}+{x}+{y}")
        stats_window.resizable(False, False)

        main_frame = ctk.CTkScrollableFrame(
            stats_window,
            fg_color=self.COLORS['white'],
            width=width-40,
            height=height-40
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        ctk.CTkLabel(
            main_frame,
            text="Book Statistics - Interactive Bubble Chart",
            font=("Arial Bold", 24),
            text_color=self.COLORS['primary']
        ).pack(pady=(0, 10))

        try:
            self.setup_database()
            
            # Fetch data for all books
            all_book_data = []
            if hasattr(self.dbroot, 'books'):
                for isbn, book in self.dbroot.books.items():
                    borrow_count = 0
                    if hasattr(self.dbroot, 'borrow_records'):
                        for record in self.dbroot.borrow_records.values():
                            if record.isbn == isbn:
                                borrow_count += 1
                    
                    # Calculate average rating
                    rating = 0
                    if hasattr(book, 'total_ratings') and hasattr(book, 'sum_ratings') and book.total_ratings > 0:
                        rating = round(book.sum_ratings / book.total_ratings, 1)
                    
                    all_book_data.append({
                        'name': book.name,
                        'borrows': borrow_count,
                        'rating': rating,
                        'copies': book.total_copies,
                        'genre': book.genre if hasattr(book, 'genre') else 'Unknown'
                    })

            if all_book_data:
                # Create bubble chart
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(111)

                # Create color map for genres
                unique_genres = list(set(book['genre'] for book in all_book_data))
                colors = plt.cm.viridis(np.linspace(0, 1, len(unique_genres)))
                genre_color_map = dict(zip(unique_genres, colors))

                # Plot bubbles
                for book in all_book_data:
                    bubble = ax.scatter(
                        book['borrows'], 
                        book['rating'],
                        s=book['copies'] * 100,  # Scale bubble size based on copies
                        alpha=0.6,
                        c=[genre_color_map[book['genre']]],
                        label=book['genre'] if book['genre'] not in ax.get_legend_handles_labels()[1] else ""
                    )
                    
                    # Add book names as annotations with rating info
                    ax.annotate(
                        f"{book['name']}\n(Rating: {book['rating']})",
                        (book['borrows'], book['rating']),
                        xytext=(5, 5),
                        textcoords='offset points',
                        fontsize=8,
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
                    )

                # Customize the plot
                ax.set_xlabel("Number of Times Borrowed", fontsize=10)
                ax.set_ylabel("Average Rating", fontsize=10)
                ax.set_title("Book Statistics: Borrowed vs Rating\n(Bubble size represents total copies)", fontsize=12)
                ax.grid(True, linestyle='--', alpha=0.7)
                
                # Set y-axis limits to show ratings from 0 to 5
                ax.set_ylim(-0.5, 5.5)
                
                # Add legend for genres
                legend = ax.legend(title="Genres", bbox_to_anchor=(1.15, 1), loc='upper left')
                plt.tight_layout()

                # Add explanation text
                explanation = ctk.CTkLabel(
                    main_frame,
                    text="Chart Explanation:\n"
                        "• X-axis: Number of times the book has been borrowed\n"
                        "• Y-axis: Average rating of the book (0-5)\n"
                        "• Bubble size: Total number of copies available\n"
                        "• Colors: Different genres\n"
                        "• Books with no ratings are shown with rating 0",
                    font=("Arial", 12),
                    text_color=self.COLORS['text_secondary'],
                    justify="left"
                )
                explanation.pack(pady=(0, 10))

                # Create canvas for matplotlib
                canvas = FigureCanvasTkAgg(fig, master=main_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

            else:
                ctk.CTkLabel(
                    main_frame,
                    text="No book data available",
                    font=("Arial", 14),
                    text_color=self.COLORS['text_secondary']
                ).pack(pady=20)

        except Exception as e:
            print(f"Error displaying book statistics: {e}")
            ctk.CTkLabel(
                main_frame,
                text=f"Error loading statistics: {str(e)}",
                text_color="red"
            ).pack(pady=20)
        finally:
            self.close_database()

        # Ensure proper cleanup
        def on_closing():
            try:
                plt.close('all')
                stats_window.destroy()
            except:
                pass

        stats_window.protocol("WM_DELETE_WINDOW", on_closing)
    def logout(self):
        """Return to login page"""
        try:
            self.close_database()
            messagebox.showinfo("Success", "Logout Successful!")
            self.master.destroy()
            from login_page import LoginPage
            next=LoginPage()
            next.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Error returning to login page: {e}")

    def toggle_sidebar(self):
        """Handle sidebar toggle"""
        if hasattr(self, 'sidebar_visible') and self.sidebar_visible:
            self.sidebar.pack_forget()
            self.sidebar_visible = False
        else:
            self.sidebar.pack(side="left", fill="y", padx=2, pady=2)
            self.sidebar_visible = True

    def on_closing(self):
        """Handle window closing with proper cleanup"""
        try:
            self.close_database()
            self.quit()
        except Exception as e:
            print(f"Error during cleanup: {e}")
            self.quit()
