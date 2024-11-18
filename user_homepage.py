import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import time
import threading
import os
from PIL import Image, ImageDraw, ImageTk
import threading
import ZODB
import ZODB.FileStorage
import BTrees
import transaction
import os
import re
import io
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
from library_management import BorrowRecord, ReturnRecord, ReviewRecord, PointDeductionRecord
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import numpy as np
from logout_page import LoginPage
from polymorphism_functions import close_database as cdb, edit_user_information as show_info, show_default_profile_photo as show_default


# Define color scheme
COLORS = {
    'primary': '#339af0',       # Bright sky blue for main actions
    'primary_dark': '#1971c2',  # Rich navy blue for hover effects
    'primary_light': '#a5d8ff', # Soft light blue for highlights
    'secondary': '#f0f4ff',     # Delicate light blue for backgrounds
    'text_primary': '#1b1f23',  # Charcoal for primary text for contrast
    'text_secondary': '#5c6975', # Cool gray for secondary text
    'white': '#ffffff',          # Crisp white for main backgrounds
    'border': '#d0e1ff',         # Light pastel blue for borders
    'hover': '#e9f4ff'  ,
    'select':'#bbcef0'        # Whisper blue for hover states
}

class SearchFilterPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS['primary'], **kwargs)

        # Filter options
        self.genre_var = ctk.StringVar(value="All Genres")
        self.rating_var = ctk.StringVar(value="All Ratings")
        self.availability_var = ctk.StringVar(value="All Books")
        
        # Genre dropdown with "All Genres" as first option
        genre_values = ["All Genres", "Science & Technology", "Humanities", "Social Sciences", 
                       "Business", "Medicine & Health", "Arts", "Math & Statistics", 
                       "Languages & Literature", "Environmental Studies", "Reference"]
        
        genre_dropdown = ctk.CTkOptionMenu(
            self, 
            variable=self.genre_var,
            values=genre_values,
            fg_color=COLORS['white'],
            button_color=COLORS['white'],
            button_hover_color=COLORS['hover'],
            dropdown_fg_color=COLORS['white'],
            dropdown_hover_color=COLORS['hover'],
            dropdown_text_color=COLORS['text_primary'],
            text_color=COLORS['text_primary'],
            width=120,
            height=40
        )
        genre_dropdown.pack(side="left", padx=5)
        
        # Rating dropdown
        rating_dropdown = ctk.CTkOptionMenu(
            self, 
            variable=self.rating_var,
            values=["All Ratings", "5★", "4★+", "3★+"],
            fg_color=COLORS['white'],
            button_color=COLORS['white'],
            button_hover_color=COLORS['hover'],
            dropdown_fg_color=COLORS['white'],
            dropdown_hover_color=COLORS['hover'],
            dropdown_text_color=COLORS['text_primary'],
            text_color=COLORS['text_primary'],
            width=120,
            height=40
        )
        rating_dropdown.pack(side="left", padx=5)
        
        # Availability dropdown
        availability_dropdown = ctk.CTkOptionMenu(
            self, 
            variable=self.availability_var,
            values=["All Books", "Available", "Unavailable"],
            fg_color=COLORS['white'],
            button_color=COLORS['white'],
            button_hover_color=COLORS['hover'],
            dropdown_fg_color=COLORS['white'],
            dropdown_hover_color=COLORS['hover'],
            dropdown_text_color=COLORS['text_primary'],
            text_color=COLORS['text_primary'],
            width=120,
            height=40
        )
        availability_dropdown.pack(side="left", padx=5)

class SearchBar(ctk.CTkFrame):
    def __init__(self, parent, command=None, **kwargs):
        super().__init__(parent, fg_color=COLORS['primary'], **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Search entry
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="Search books...",
            textvariable=self.search_var,
            height=40,  # Increased height
            fg_color=COLORS['white'],
            border_color=COLORS['border'],
            text_color=COLORS['text_primary']
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Search button with icon
        self.search_button = ctk.CTkButton(
            self,
            text="🔍",
            width=40,
            height=40,  # Made square
            fg_color=COLORS['white'],
            hover_color=COLORS['hover'],
            text_color=COLORS['primary'],
            command=command
        )
        self.search_button.grid(row=0, column=1)


class UserHomepage(ctk.CTkFrame):  
    def __init__(self, master, user_id):  # Add master parameter
        super().__init__(master)
        self.master = master  # Store reference to master window
        self.user_id=user_id

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
        
        # Initialize database connection
        self.db_lock = threading.Lock()
        self.setup_database()
       

        # Configure theme
        self._set_theme()
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Initialize sidebar state
        self.sidebar_visible = False
        
        # Load books from database
        self.load_books_from_database()

        # Create sidebar
        self.create_sidebar()

        # Create header frame
        self.header = ctk.CTkFrame(self, fg_color=COLORS['primary'], height=100)
        self.header.grid(row=0, column=1, sticky="ew")
        self.header.grid_columnconfigure(3, weight=1)
        self.header.grid_rowconfigure(0, weight=1)
        self.header.grid_propagate(False)
        self.header.grid(row=0, column=1, sticky="ew", padx=(0, 20))
         # Logo frame (square)
        self.logo_frame = ctk.CTkFrame(
            self.header,
            width=90,  # Logo size
            height=90,  # Logo size
            fg_color="transparent",
            corner_radius=10
        )
        # Center the logo frame vertically and horizontally in its cell
        self.logo_frame.grid(row=0, column=1, padx=20, pady=(5, 5), sticky="nsew")
        self.logo_frame.grid_propagate(False)

        # Create a container frame inside logo_frame for perfect centering
        logo_container = ctk.CTkFrame(
            self.logo_frame,
            fg_color="transparent"
        )
        logo_container.place(relx=0.5, rely=0.5, anchor="center")

        # Load and display logo
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(current_dir, "logos", "kmitlgo.png")
            
            logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(80, 80)  # Logo image size
            )
            logo_label = ctk.CTkLabel(
                logo_container,
                image=logo_image,
                text=""
            )
            logo_label.pack()
        except Exception as e:
            print(f"Error loading logo: {e}")
            ctk.CTkLabel(
                logo_container,
                text="LIBRARY",
                font=("Arial Bold", 28),
                text_color=COLORS['white']
            ).pack()


        # Search filter panel
        self.search_filter = SearchFilterPanel(self.header)
        self.search_filter.grid(row=0, column=2, padx=10, pady=30)

        # Search bar
        self.search_bar = SearchBar(self.header, command=self.search_books)
        self.search_bar.grid(row=0, column=3, sticky="ew", pady=30)

       # Profile button
        self.profile_button = self.create_profile_button()
        self.profile_button.grid(row=0, column=4, padx=(0,20), pady=20)

        # Create main content frame
        self.main_content = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS['white']
        )
        self.main_content.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)

        # All Books Label
        self.all_books_label = ctk.CTkLabel(
            self.main_content,
            text="All Books",
            font=("Arial Bold", 24),
            text_color=COLORS['text_primary']
        )
        self.all_books_label.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Create book grid
        self.create_book_grid()
        
        

    def setup_database(self):
        """Initialize database connection with proper error handling"""
        try:
            storage_path = os.path.join(os.path.dirname(__file__), 'library.fs')
            self.storage = ZODB.FileStorage.FileStorage(storage_path)
            self.db = ZODB.DB(self.storage)
            self.connection = self.db.open()
            self.dbroot = self.connection.root()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
            self.destroy()

    def close_database(self):
        cdb(self)

    def _set_theme(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLORS['white'])

    def create_sidebar(self):
        # Create sidebar frame with reduced width for icons only
        self.sidebar = ctk.CTkFrame(
            self,
            width=60,  # Reduced width to fit icons
            fg_color=COLORS['secondary'],
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsw")
        self.sidebar.grid_propagate(False)
        
        # Add a separator line on the right
        separator = ctk.CTkFrame(
            self.sidebar,
            width=2,                          
            fg_color=COLORS['border'],        
            corner_radius=0                   
        )
        separator.place(relx=1, rely=0, relheight=1, anchor="ne")  
        
        # Menu items with icons only
        menu_items = [
            ("📚", "borrowed", "Borrowed Books"),
            ("📋", "history", "Activity History"),
            ("📊", "statistics", "Book Statistics"),
            ("📧", "contact", "Contact Us"),
            ("↪️", "logout", "Log Out"),
            ("❌", "exit", "Exit")
        ]
        
        for icon, command, tooltip_text in menu_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=icon,
                width=40,  # Fixed width for icons
                height=40,  # Fixed height for icons
                fg_color="transparent",
                text_color=COLORS['text_secondary'],
                hover_color=COLORS['hover'],
                corner_radius=8,
                font=ctk.CTkFont(size=20),
                command=lambda x=command: self.menu_click(x)
            )
            btn.pack(pady=5)
            
            # Create tooltip
            self.create_tooltip(btn, tooltip_text)

    def create_profile_button(self):
        """Create profile button with user's profile photo"""
        try:
            # Get the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            profile_path = None
            points=0
            
            # Try to get user's profile photo from database
            if hasattr(self.dbroot, 'users') and self.user_id in self.dbroot.users:
                user = self.dbroot.users[self.user_id]
                points=user.points
                if hasattr(user, 'image_data') and user.image_data:
                    # Create a circular profile image from user's stored image
                    image = Image.open(io.BytesIO(user.image_data))
                    # Convert to RGBA if not already
                    if image.mode != 'RGBA':
                        image = image.convert('RGBA')
                    
                    # Create circular mask
                    size = min(image.size)
                    mask = Image.new('L', (size, size), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0, size, size), fill=255)
                    
                    # Create new image with transparent background
                    output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                    output.paste(image, (0, 0))
                    output.putalpha(mask)
                    
                    # Create CTkImage object
                    profile_image = ctk.CTkImage(
                        light_image=output,
                        dark_image=output,
                        size=(50, 50)
                    )
                else:
                    # Use default profile image if no user image
                    default_path = os.path.join(current_dir, "logos", "default_user.png")
                    profile_image = self.create_circular_image(default_path)
            else:
                # Use default profile image
                default_path = os.path.join(current_dir, "logos", "default_user.png")
                profile_image = self.create_circular_image(default_path)

            # Create button with image
            return ctk.CTkButton(
                self.header,
                text=f"{points} points",
                image=profile_image,
                width=60,
                height=60,
                corner_radius=30,
                fg_color="transparent",
                hover_color=COLORS['hover'],
                command=self.show_profile
            )

        except Exception as e:
            print(f"Error creating profile button: {e}")
            # Fallback to text button
            return ctk.CTkButton(
                self.header,
                text="👤{points}points",
                width=60,
                height=60,
                corner_radius=30,
                fg_color=COLORS['white'],
                text_color=COLORS['primary'],
                hover_color=COLORS['hover'],
                font=ctk.CTkFont(size=24),
                command=self.show_profile
            )
        
    
    def create_circular_image(self, image_path, size=(50, 50)):
        """Helper function to create circular profile image"""
        try:
            image = Image.open(image_path)
            # Convert to RGBA
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Create square image
            image = image.resize(size)
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            
            # Create output image with transparent background
            output = Image.new('RGBA', size, (0, 0, 0, 0))
            output.paste(image, (0, 0))
            output.putalpha(mask)
            
            return ctk.CTkImage(
                light_image=output,
                dark_image=output,
                size=size
            )
        except Exception as e:
            print(f"Error creating circular image: {e}")
            return None

        
    def create_book_frame(self, parent, book_data, width=250, height=350):
        frame = ctk.CTkFrame(
            parent,
            width=width,
            height=height,
            fg_color=COLORS['secondary'],
            border_color=COLORS['border'],
            border_width=1
        )
        frame.grid_propagate(False)
        
        # Book cover with image handling
        if book_data.get("image_data"):
            try:
                image = Image.open(io.BytesIO(book_data["image_data"]))
                image.thumbnail((width-40, 200))  # Resize image while maintaining aspect ratio
                photo = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=(width-40, 200)
                )
                cover_label = ctk.CTkLabel(
                    frame,
                    text="",
                    image=photo,
                    width=width-40,
                    height=200
                )
                cover_label.image = photo  # Keep a reference to prevent garbage collection
                cover_label.place(relx=0.5, rely=0.3, anchor="center")
            except Exception as e:
                print(f"Error loading book cover: {e}")
                self._create_book_placeholder(frame, width)
        else:
            self._create_book_placeholder(frame, width)
        
        # Book info with larger fonts and spacing
        title_label = ctk.CTkLabel(
            frame,
            text=book_data["title"],
            wraplength=220,
            text_color=COLORS['text_primary'],
            font=("Arial Bold", 16)
        )
        title_label.place(relx=0.5, rely=0.65, anchor="center")
        
        author_label = ctk.CTkLabel(
            frame,
            text=book_data["author"],
            font=("Arial", 14),
            text_color=COLORS['text_secondary']
        )
        author_label.place(relx=0.5, rely=0.8, anchor="center")
        
        rating_label = ctk.CTkLabel(
            frame,
            text=book_data["rating"],
            text_color=COLORS['primary'],
            font=("Arial", 16)
        )
        rating_label.place(relx=0.5, rely=0.9, anchor="center")
        
        # Status indicator
        status_color = COLORS['primary'] if book_data["status"] == "Available" else "gray"
        status_frame = ctk.CTkFrame(
            frame,
            width=15,
            height=15,
            fg_color=status_color,
            corner_radius=7
        )
        status_frame.place(relx=0.9, rely=0.1)
        
        def on_enter(e):
            frame.configure(fg_color=COLORS['select'])
            
        def on_leave(e):
            frame.configure(fg_color=COLORS['secondary'])
            
        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)
        frame.bind("<Button-1>", lambda e: self.show_book_details(book_data))
        
        return frame

    def _create_book_placeholder(self, frame, width):
        """Create placeholder cover when image is not available"""
        try:
            # Get the current directory and construct path to default book image
            current_dir = os.path.dirname(os.path.dirname(__file__))
            default_book_path = os.path.join(current_dir, "logos", "default_book.png")
            
            # Create CTkImage with the default book image
            default_image = ctk.CTkImage(
                light_image=Image.open(default_book_path),
                dark_image=Image.open(default_book_path),
                size=(width-40, 200)  # Keep your original size
            )
            
            # Create and place the image label
            cover_label = ctk.CTkLabel(
                frame,
                text="",
                image=default_image,
                width=width-40,
                height=200
            )
            cover_label.image = default_image  # Keep a reference to prevent garbage collection
            cover_label.place(relx=0.5, rely=0.3, anchor="center")
            
        except Exception as e:
            print(f"Error loading default book cover: {e}")
            # Fallback to the original text-based placeholder if image loading fails
            cover = ctk.CTkFrame(
                frame,
                width=width-40,
                height=200,
                fg_color=self.COLORS['secondary']
            )
            cover.place(relx=0.5, rely=0.3, anchor="center")
            
            placeholder_label = ctk.CTkLabel(
                cover,
                text="No Cover\nAvailable",
                font=("Arial", 14),
                text_color=self.COLORS['text_secondary']
            )
        placeholder_label.place(relx=0.5, rely=0.5, anchor="center")

    

    def create_tooltip(self, widget, text):
        """Create persistent tooltip for sidebar buttons"""
        def enter(e):
            # Get current mouse position
            x, y = e.x_root, e.y_root
            
            # Create tooltip window that stays on top
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x + 20}+{y}")
            tooltip.attributes('-topmost', True)  # Keep tooltip on top
            
            # Create tooltip label with improved visibility
            label = ctk.CTkLabel(
                tooltip,
                text=text,
                fg_color=COLORS['primary_dark'],
                corner_radius=6,
                text_color=COLORS['white'],
                padx=10,
                pady=5
            )
            label.pack()
            
            # Store tooltip reference
            widget.tooltip = tooltip
            
            # Function to keep checking mouse position
            def check_mouse(widget=widget, tooltip=tooltip, original_x=x, original_y=y):
                if not hasattr(widget, 'tooltip'):
                    return
                try:
                    # Update tooltip position if mouse moved
                    curr_x = widget.winfo_pointerx()
                    curr_y = widget.winfo_pointery()
                    if curr_x != original_x or curr_y != original_y:
                        tooltip.wm_geometry(f"+{curr_x + 20}+{curr_y}")
                    tooltip.lift()  # Keep tooltip on top
                    widget.after(50, lambda: check_mouse(widget, tooltip, curr_x, curr_y))
                except tk.TclError:
                    pass
            
            check_mouse()
        
        def leave(e):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

        
    def load_books_from_database(self):
        with self.db_lock:
            try:
                self.books_data = []
                if hasattr(self.dbroot, 'books'):
                    for isbn, book in self.dbroot.books.items():
                        book_data = {
                            "title": book.name,
                            "author": book.author,
                            "genre": book.genre if hasattr(book, 'genre') else "Uncategorized",
                            "status": "Available" if book.available_copies > 0 else "Unavailable",
                            "description": book.description,
                            "isbn": isbn,
                            "total_copies": book.total_copies,
                            "available_copies": book.available_copies,
                            "image_data": book.image_data if hasattr(book, 'image_data') else None,
                            "rating": self._calculate_book_rating(book)
                        }
                        self.books_data.append(book_data)

                    if hasattr(self, 'grid_frame'):
                        self.update_book_displays()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load books: {e}")

    def _calculate_book_rating(self, book):
        if book.total_ratings > 0:
            rating = round(book.sum_ratings / book.total_ratings, 1)
            return f"{'★' * int(rating)}{'☆' * (5 - int(rating))} ({book.total_ratings})"
        else:
            return "No ratings"

    def update_book_grid(self, books_to_display):
        """Updated function to refresh the book grid with given books"""
        try:
            # Clear existing grid frame
            if hasattr(self, 'grid_frame'):
                self.grid_frame.destroy()

            # Create new grid frame
            self.grid_frame = ctk.CTkFrame(self.main_content, fg_color=COLORS['white'])
            self.grid_frame.grid(row=1, column=0, sticky="nsew")
            
            # Update "All Books" label with count
            self.all_books_label.configure(text=f"Books Found: {len(books_to_display)}")
            
            if not books_to_display:
                # Show "No books found" message
                no_books_frame = ctk.CTkFrame(
                    self.grid_frame,
                    fg_color=COLORS['secondary'],
                    corner_radius=10
                )
                no_books_frame.pack(pady=50, padx=20, fill="x")
                
                ctk.CTkLabel(
                    no_books_frame,
                    text="No books found matching your search criteria",
                    font=("Arial", 16),
                    text_color=COLORS['text_secondary'],
                    pady=20
                ).pack()
                
                return

            # Fixed 5 columns
            num_columns = 5
            
            # Create grid of books
            for i, book in enumerate(books_to_display):
                row = i // num_columns
                col = i % num_columns
                book_frame = self.create_book_frame(self.grid_frame, book)
                book_frame.grid(row=row, column=col, padx=15, pady=15)
                
            # Configure grid columns to expand evenly
            for i in range(num_columns):
                self.grid_frame.grid_columnconfigure(i, weight=1)
            
            # Update the display
            self.grid_frame.update()
            self.main_content.update()

        except Exception as e:
            print(f"Error updating book grid: {e}")
            messagebox.showerror("Error", f"Failed to update display: {str(e)}")

    def meets_rating_criteria(self, book, rating_filter):
        """Helper function to check if a book meets the rating criteria"""
        if rating_filter == "All Ratings":
            return True
            
        rating_str = book["rating"]
        if "No ratings" in rating_str:
            return False
            
        try:
            # Extract numeric rating from format "★★★☆☆ (X)"
            stars = rating_str.split()[0]
            rating = stars.count('★')
            
            if rating_filter == "5★":
                return rating == 5
            elif rating_filter == "4★+":
                return rating >= 4
            elif rating_filter == "3★+":
                return rating >= 3
            return True
        except Exception as e:
            print(f"Error processing rating: {e}")
            return False

    def create_book_grid(self):
        """Initial creation of the book grid"""
        self.grid_frame = ctk.CTkFrame(self.main_content, fg_color=COLORS['white'])
        self.grid_frame.grid(row=1, column=0, sticky="nsew")
        
        # Fixed 5 columns
        num_columns = 5
        
        # Create grid of books
        for i, book in enumerate(self.books_data):
            row = i // num_columns
            col = i % num_columns
            book_frame = self.create_book_frame(self.grid_frame, book)
            book_frame.grid(row=row, column=col, padx=15, pady=15)
            
        # Configure grid columns to expand evenly
        for i in range(num_columns):
            self.grid_frame.grid_columnconfigure(i, weight=1)

    def search_books(self, event=None):
        """Updated search function with proper display refresh"""
        try:
            # Get search criteria
            search_term = self.search_bar.search_var.get().lower()
            genre_filter = self.search_filter.genre_var.get()
            rating_filter = self.search_filter.rating_var.get()
            availability_filter = self.search_filter.availability_var.get()

            # Filter books
            filtered_books = []
            for book in self.books_data:
                # Genre filter
                genre_match = (genre_filter == "All Genres" or 
                            book["genre"] == genre_filter)
                
                # Availability filter
                availability_match = (
                    availability_filter == "All Books" or
                    (availability_filter == "Available" and book["status"] == "Available") or
                    (availability_filter == "Unavailable" and book["status"] == "Unavailable")
                )
                
                # Rating filter
                rating_match = self.meets_rating_criteria(book, rating_filter)
                
                # Search term match
                search_match = (
                    search_term == "" or
                    search_term in book["title"].lower() or
                    search_term in book["author"].lower() or
                    search_term in book["genre"].lower() or
                    search_term in str(book["isbn"]).lower()
                )

                if all([genre_match, availability_match, rating_match, search_match]):
                    filtered_books.append(book)

            # Update the display with filtered results
            self.update_book_grid(filtered_books)

        except Exception as e:
            print(f"Search error: {e}")
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def update_book_displays(self):
        """Update book display with error handling"""
        try:
            # Clear existing grid
            for widget in self.grid_frame.winfo_children():
                widget.destroy()
            
            # Recreate book grid
            self.create_book_grid()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update display: {e}")

    def show_profile(self):
        show_info(self, self.user_id)
    

    def update_profile_button_image(self, image_data):
        """Update profile button with new image"""
        try:
            # Create a copy of the image data
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGBA if needed
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Create square image
            size = min(image.size)
            image = image.resize((size, size), Image.Resampling.LANCZOS)
            
            # Create circular mask
            mask = Image.new('L', (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)
            
            # Apply mask
            output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            output.paste(image, (0, 0))
            output.putalpha(mask)
            
            # Resize for button
            output = output.resize((50, 50), Image.Resampling.LANCZOS)
            
            # Create CTkImage
            profile_image = ctk.CTkImage(
                light_image=output,
                dark_image=output,
                size=(50, 50)
            )
            
            # Update button
            if hasattr(self, 'profile_button'):
                self.profile_button.configure(image=profile_image)
                self.profile_button.image = profile_image  # Keep reference
                
        except Exception as e:
            print(f"Error updating profile button image: {e}")
            # Fallback to default if needed
            self.show_default_profile_photo(self.profile_button)

    
    def show_default_profile_photo(self, frame):
        show_default(self, frame)


    

    def show_book_details(self, book_data):
        """Show detailed book information"""
        self.book_details_window = ctk.CTkToplevel(self)
        self.book_details_window.title("Book Details")
        
        # Set window to appear over UserHomepage GUI
        self.book_details_window.transient(self)
        self.book_details_window.grab_set()
        
        # Get screen dimensions and set fixed maximized state
        screen_width = self.book_details_window.winfo_screenwidth()
        screen_height = self.book_details_window.winfo_screenheight()
        self.book_details_window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.book_details_window.resizable(False, False)
        self.book_details_window.state('zoomed')
        self.book_details_window.bind('<Map>', lambda e: self.book_details_window.state('zoomed'))
        
        # Configure window colors
        self.book_details_window.configure(fg_color=COLORS['white'])
        
        # Create header frame
        header_frame = ctk.CTkFrame(self.book_details_window, fg_color=COLORS['primary'], height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text=book_data["title"],
            font=("Arial Bold", 24),
            text_color=COLORS['white']
        ).pack(side="left", padx=20, pady=20)
        
        # Back button
        back_button = ctk.CTkButton(
            header_frame,
            text="Back",
            fg_color=COLORS['secondary'],
            hover_color=COLORS['hover'],
            text_color=COLORS['text_primary'],
            command=self.book_details_window.destroy
        )
        back_button.pack(side="right", padx=20, pady=20)
        
        # Create content frame
        content_frame = ctk.CTkFrame(self.book_details_window, fg_color=COLORS['white'])
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=2)
        content_frame.grid_columnconfigure(2, weight=2)
        content_frame.grid_rowconfigure(0, weight=2)  # Upper section
        content_frame.grid_rowconfigure(1, weight=3)  # Description section
        
        # Book cover
        cover_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['white'])
        cover_frame.grid(row=0, column=0, padx=20, pady=20, sticky="n")  # Changed to sticky="n"
        
        if book_data.get("image_data"):
            try:
                image = Image.open(io.BytesIO(book_data["image_data"]))
                image.thumbnail((300, 400))
                photo = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=(300, 400)
                )
                cover_label = ctk.CTkLabel(
                    cover_frame,
                    text="",
                    image=photo
                )
                cover_label.image = photo
                cover_label.pack(fill="both", expand=True)
            except Exception as e:
                print(f"Error loading book cover: {e}")
        
        # Book details - with fixed height
        details_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['white'], height=400)  # Fixed height
        details_frame.grid(row=0, column=1, padx=20, pady=20, sticky="n")  # Changed to sticky="n"
        details_frame.pack_propagate(False)  # Prevent frame from expanding
        
        def create_info_label(text):
            return ctk.CTkLabel(
                details_frame,
                text=text,
                font=("Arial", 16),  # Reduced font size
                anchor="w",
                fg_color=COLORS['secondary'],
                corner_radius=10,
                padx=10,
                pady=3  # Reduced padding
            )
        
        create_info_label(f"Author: {book_data['author']}").pack(pady=5, anchor="w", fill="x")  # Reduced padding
        create_info_label(f"Genre: {book_data['genre']}").pack(pady=5, anchor="w", fill="x")
        create_info_label(f"ISBN: {book_data['isbn']}").pack(pady=5, anchor="w", fill="x")
        create_info_label(f"Rating: {book_data['rating']}").pack(pady=5, anchor="w", fill="x")
        create_info_label(f"Status: {book_data['status']}").pack(pady=5, anchor="w", fill="x")
        create_info_label(f"Total Copies: {book_data['total_copies']}").pack(pady=5, anchor="w", fill="x")
        create_info_label(f"Available Copies: {book_data['available_copies']}").pack(pady=5, anchor="w", fill="x")
        
        # User ratings horizontal bar graph
        ratings_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['white'], height=400)  # Fixed height
        ratings_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")  # Changed to sticky="n"
        ratings_frame.pack_propagate(False)  # Prevent frame from expanding
        
        ctk.CTkLabel(
            ratings_frame,
            text="User Ratings",
            font=("Arial Bold", 20),
            anchor="w"
        ).pack(pady=10, anchor="w")
        
        # Fetch real ratings data from the database
        ratings = [5, 4, 3, 2, 1]  # Example ratings, replace with actual data
        rating_counts = [0] * 5  # Initialize rating counts
        
        if hasattr(self.dbroot, 'all_records'):
            for record in self.dbroot.all_records.values():
                if isinstance(record, ReviewRecord) and record.isbn == book_data['isbn']:
                    rating = record.rating
                    if 1 <= rating <= 5:
                        rating_counts[5 - rating] += 1  # Increment the count for the corresponding rating
        
        max_count = max(rating_counts) if rating_counts else 0
        
        for i, count in enumerate(rating_counts):
            rating = ratings[i]
            bar_frame = ctk.CTkFrame(ratings_frame, fg_color=COLORS['secondary'], height=20)
            bar_frame.pack(pady=5, fill="x")
            
            # Display rating text
            ctk.CTkLabel(
                bar_frame,
                text=f"{rating} {'★' * rating}",
                font=("Arial", 14),
                text_color=COLORS['text_primary']
            ).pack(side="left", padx=10)
            
            # Display horizontal bar
            bar_width = count / max_count * 200 if max_count > 0 else 0
            bar = ctk.CTkFrame(bar_frame, fg_color=COLORS['primary'], height=20, width=bar_width)
            bar.pack(side="left")
            
            # Display count text
            ctk.CTkLabel(
                bar_frame,
                text=str(count),
                font=("Arial", 14),
                text_color=COLORS['text_primary']
            ).pack(side="left", padx=10)
        
        # Book description
        description_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['white'])
        description_frame.grid(row=1, column=1, columnspan=2, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(
            description_frame,
            text="Description:",
            font=("Arial Bold", 20),
            anchor="w"
        ).pack(pady=10, anchor="w", padx=10)
        
        description_text = ctk.CTkTextbox(
            description_frame,
            fg_color=COLORS["white"],
            height=250,  # Increased height
            font=("Arial", 16),
            wrap="word"
        )
        description_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        description_text.insert("0.0", book_data["description"])
        description_text.configure(state="disabled")
        
        if book_data["available_copies"] > 0 :
            # Borrow button
            borrow_button = ctk.CTkButton(
            content_frame,
            text="Borrow",
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            command=lambda: self.borrow_book(book_data),
            state="normal"   # Add this line
            )
            borrow_button.grid(row=1, column=0, pady=20)
        else:
            # Not available label
            unavailable_label = ctk.CTkLabel(
                content_frame,
                text="Book is not available to borrow.",
                font=("Arial Bold", 16),
                text_color=COLORS['text_primary'],
                fg_color=COLORS['secondary'],
                corner_radius=8,
                padx=20,
                pady=10
            )
            unavailable_label.grid(row=1, column=0, pady=20)


    def logout(self):
        """Return to login page"""
        try:
            self.close_database()
            messagebox.showinfo("Success", "Logout Successful!")
            self.master.destroy()
            next=LoginPage()
            next.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Error returning to login page: {e}")

    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        if self.sidebar_visible:
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid()
        self.sidebar_visible = not self.sidebar_visible

    def menu_click(self, item):
        """Handle menu item clicks for user interface"""
        if item == "borrowed":
            # Show currently borrowed books
            self.show_borrowed_books()
        elif item == "history":
            # Show borrowing history
            self.show_activity_history()
        elif item == "statistics":
            # Show reading statistics
            self.show_book_statistics()
        elif item=="contact":
            self.contact()
        elif item == "logout":
            if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
                self.logout()
        elif item == "exit":
            if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
                self.destroy()
                self.master.destroy()

    def show_activity_history(self):
        """Show user's activity history in a chronological order"""
        history_window = ctk.CTkToplevel(self)
        history_window.title("Activity History")
        history_window.transient(self)
        history_window.grab_set()
        
        # Set window to fullscreen
        screen_width = history_window.winfo_screenwidth()
        screen_height = history_window.winfo_screenheight()
        history_window.geometry(f"{screen_width}x{screen_height}+0+0")
        history_window.resizable(False, False)
        history_window.state('zoomed')
        history_window.configure(fg_color=COLORS['white'])
        
        # Header frame
        header_frame = ctk.CTkFrame(history_window, fg_color=COLORS['primary'], height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="Activity History",
            font=("Arial Bold", 24),
            text_color=COLORS['white']
        ).pack(side="left", padx=20, pady=20)
        
        # Buttons frame on the right
        buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons_frame.pack(side="right", padx=20, pady=20)
        
        # Statistics button
        stats_button = ctk.CTkButton(
            buttons_frame,
            text="📊",
            width=40,
            height=40,
            fg_color=COLORS['secondary'],
            text_color=COLORS['text_primary'],
            hover_color=COLORS['hover'],
            command=lambda: self.show_activity_statistics()
        )
        stats_button.pack(side="right", padx=10)
        
        # Back button
        back_button = ctk.CTkButton(
            buttons_frame,
            text="Back",
            fg_color=COLORS['secondary'],
            hover_color=COLORS['hover'],
            text_color=COLORS['text_primary'],
            command=history_window.destroy
        )
        back_button.pack(side="right", padx=10)
        
        # Main content frame with scrollable
        content_frame = ctk.CTkScrollableFrame(history_window, fg_color=COLORS['white'])
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        try:
            # Get all records for the user
            all_records = []
            
            # Get borrow records
            if hasattr(self.dbroot, 'borrow_records'):
                for record_id, record in self.dbroot.borrow_records.items():
                    if record.user_id == self.user_id:
                        all_records.append(record)
            
            # Get return and review records
            if hasattr(self.dbroot, 'all_records'):
                for record_id, record in self.dbroot.all_records.items():
                    if record.user_id == self.user_id:
                        all_records.append(record)
            
            # Sort records by date
            all_records.sort(key=lambda x: x.date)
            
            # Create a header for the list
            header_label = ctk.CTkLabel(
                content_frame,
                text="Date                                            Activity                                   ",
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
                    fg_color=COLORS['secondary'],
                    corner_radius=10
                )
                record_frame.pack(fill="x", pady=5, padx=10)
                
                # Get book details
                book = self.dbroot.books.get(record.isbn)
                book_title = book.name if book else "Unknown Book"
                
                # Create record content based on type
                if isinstance(record, BorrowRecord):
                    action_text = f"Borrowed '{book_title}'"
                    end_date_text = f" (Due: {record.end_date.strftime('%B %d, %Y')})" if hasattr(record, 'end_date') else ""
                    text_color = COLORS['primary']  # Blue for borrows
                elif isinstance(record, ReturnRecord):
                    action_text = f"Returned '{book_title}'"
                    end_date_text = ""
                    text_color = "green"  # Green for returns
                elif isinstance(record, ReviewRecord):
                    action_text = f"Reviewed '{book_title}' - Rating: {'★' * int(record.rating)}{'☆' * (5 - int(record.rating))}"
                    end_date_text = ""
                    text_color = "orange"  # Orange for reviews
                elif isinstance(record, PointDeductionRecord ):
                    action_text=f"20 points deducted for overdue book."
                    end_date_text=""
                    text_color="red"
                else:
                    continue  # Skip unknown record types
                
                record_content = ctk.CTkLabel(
                    record_frame,
                    text=f"{record.date.strftime('%Y-%m-%d %I:%M %p')}    {action_text}{end_date_text}",
                    font=("Arial", 14),
                    text_color=text_color,
                    anchor="w",
                    padx=15,
                    pady=10
                )
                record_content.pack(fill="x")
                
                # Add hover effect
                def on_enter(e, frame=record_frame):
                    frame.configure(fg_color=COLORS['hover'])
                
                def on_leave(e, frame=record_frame):
                    frame.configure(fg_color=COLORS['secondary'])
                
                record_frame.bind("<Enter>", on_enter)
                record_frame.bind("<Leave>", on_leave)
                
            if not all_records:
                ctk.CTkLabel(
                    content_frame,
                    text="No activity records found",
                    font=("Arial", 14),
                    text_color=COLORS['text_secondary']
                ).pack(pady=20)
                
        except Exception as e:
            print(f"Error displaying activity history: {e}")
            ctk.CTkLabel(
                content_frame,
                text=f"Error loading activity history: {str(e)}",
                text_color="red"
            ).pack(pady=20)

    def show_activity_statistics(self):
        """Show statistics about user's library activities with graph"""
        stats_window = ctk.CTkToplevel(self)
        stats_window.title("Activity Statistics")
        stats_window.grab_set()
        
        # Reduced window size
        width = 700
        height = 600
        x = (stats_window.winfo_screenwidth() - width) // 2
        y = (stats_window.winfo_screenheight() - height) // 2
        stats_window.geometry(f"{width}x{height}+{x}+{y}")
        stats_window.resizable(False, False)  # Prevent resizing
        
        # Add a scrollable main frame
        main_frame = ctk.CTkScrollableFrame(
            stats_window,
            fg_color=COLORS['white'],
            width=width-40,  # Account for padding
            height=height-40
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Simple header without extra close button
        ctk.CTkLabel(
            main_frame,
            text="Activity Statistics",
            font=("Arial Bold", 24),
            text_color=COLORS['primary']
        ).pack(pady=(0, 10))
        
        try:
            # Calculate statistics
            total_borrowed = 0
            total_returned = 0
            total_reviews = 0
            rating_sum = 0
            
            # Prepare data for last 7 days
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
            
            # Initialize data structure for daily counts
            daily_data = {date: {'borrow': 0, 'return': 0, 'review': 0} for date in dates}
            
            # Count borrow records
            if hasattr(self.dbroot, 'borrow_records'):
                for record in self.dbroot.borrow_records.values():
                    if record.user_id == self.user_id:
                        total_borrowed += 1
                        record_date = record.date.replace(hour=0, minute=0, second=0, microsecond=0)
                        if record_date in daily_data:
                            daily_data[record_date]['borrow'] += 1
            
            # Count return and review records
            if hasattr(self.dbroot, 'all_records'):
                for record in self.dbroot.all_records.values():
                    if record.user_id == self.user_id:
                        record_date = record.date.replace(hour=0, minute=0, second=0, microsecond=0)
                        if isinstance(record, ReturnRecord):
                            total_returned += 1
                            if record_date in daily_data:
                                daily_data[record_date]['return'] += 1
                        elif isinstance(record, ReviewRecord):
                            total_reviews += 1
                            rating_sum += record.rating
                            if record_date in daily_data:
                                daily_data[record_date]['review'] += 1
            
            avg_rating = rating_sum / total_reviews if total_reviews > 0 else 0
            
            # Create stats display in a more compact format
            stats_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['secondary'])
            stats_frame.pack(fill="x", pady=10)
            
            stats_data = [
                ("Borrowed Books=", total_borrowed),
                ("Returned Books=", total_returned),
                ("Total Reviews=", total_reviews),
                ("Average Rating=", f"{avg_rating:.1f}/5.0" if total_reviews > 0 else "N/A"),
                ("Currently Borrowed=", total_borrowed - total_returned)
            ]
            
            # Create two columns for stats to save vertical space
            for i in range(0, len(stats_data), 2):
                row_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
                row_frame.pack(fill="x", padx=10, pady=5)
                
                # First stat in row
                stat_frame1 = ctk.CTkFrame(row_frame, fg_color="transparent")
                stat_frame1.pack(side="left", expand=True, fill="x", padx=5)
                
                stat_text = f"{stats_data[i][0]}{stats_data[i][1]}"
                ctk.CTkLabel(
                    stat_frame1,
                    text=stat_text,
                    font=("Arial Bold", 12),
                    anchor="w"
                ).pack(side="left")
                
                # Second stat in row (if exists)
                if i + 1 < len(stats_data):
                    stat_frame2 = ctk.CTkFrame(row_frame, fg_color="transparent")
                    stat_frame2.pack(side="right", expand=True, fill="x", padx=5)
                    
                    stat_text = f"{stats_data[i + 1][0]}{stats_data[i + 1][1]}"
                    ctk.CTkLabel(
                        stat_frame2,
                        text=stat_text,
                        font=("Arial Bold", 12),
                        anchor="w"
                    ).pack(side="left")
            
            # Create matplotlib figure with smaller size
            fig, ax = plt.subplots(figsize=(8, 4))
            
            # Prepare data for plotting
            x = np.arange(len(dates))
            width = 0.25
            
            # Create bars
            borrows = [daily_data[date]['borrow'] for date in dates]
            returns = [daily_data[date]['return'] for date in dates]
            reviews = [daily_data[date]['review'] for date in dates]
            ax.plot(x, borrows, 'o-', label='Borrows', color=COLORS['primary'], linewidth=2, markersize=6)
            ax.plot(x, returns, 's-', label='Returns', color='green', linewidth=2, markersize=6)
            ax.plot(x, reviews, '^-', label='Reviews', color='orange', linewidth=2, markersize=6)
            
            # Add value labels on points
            for i in range(len(dates)):
                if borrows[i] > 0:
                    ax.text(i, borrows[i] + 0.1, str(borrows[i]), ha='center', va='bottom', color=COLORS['primary'])
                if returns[i] > 0:
                    ax.text(i, returns[i] + 0.1, str(returns[i]), ha='center', va='bottom', color='green')
                if reviews[i] > 0:
                    ax.text(i, reviews[i] + 0.1, str(reviews[i]), ha='center', va='bottom', color='orange')
            
            # Customize graph
            ax.set_ylabel('Number of Activities')
            ax.set_title('Activity History - Last 7 Days')
            ax.set_xticks(x)
            ax.set_xticklabels([date.strftime('%m/%d') for date in dates], rotation=45)
            
            # Add grid for better readability
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Move legend to upper left to avoid overlap with lines
            ax.legend(loc='upper left', bbox_to_anchor=(0, 1.15), ncol=3)
            
            # Adjust y-axis to start from 0 and have some padding at top
            ax.set_ylim(bottom=0, top=max(max(borrows), max(returns), max(reviews)) + 1)
            
            # Adjust layout to prevent label cutoff
            plt.tight_layout()
            
            # Create canvas for matplotlib
            canvas = FigureCanvasTkAgg(fig, master=main_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        except Exception as e:
            print(f"Error displaying statistics: {e}")
            ctk.CTkLabel(
                main_frame,
                text=f"Error loading statistics: {str(e)}",
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
    
    def show_book_statistics(self):
        """Show statistics about book borrowing patterns"""
        stats_window = ctk.CTkToplevel(self)
        stats_window.title("Book Statistics")
        stats_window.grab_set()
        
        # Window size
        width = 700
        height = 400  # Reduced height since we removed detailed stats
        x = (stats_window.winfo_screenwidth() - width) // 2
        y = (stats_window.winfo_screenheight() - height) // 2
        stats_window.geometry(f"{width}x{height}+{x}+{y}")
        stats_window.resizable(False, False)
        
        main_frame = ctk.CTkScrollableFrame(
            stats_window,
            fg_color=COLORS['white'],
            width=width-40,
            height=height-40
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        ctk.CTkLabel(
            main_frame,
            text="Most Popular Books",
            font=("Arial Bold", 24),
            text_color=COLORS['primary']
        ).pack(pady=(0, 10))
        
        try:
            # Calculate book borrow frequencies
            book_borrow_counts = {}
            
            if hasattr(self.dbroot, 'borrow_records'):
                for record in self.dbroot.borrow_records.values():
                    book_isbn = record.isbn
                    if book_isbn not in book_borrow_counts:
                        book_borrow_counts[book_isbn] = 0
                    book_borrow_counts[book_isbn] += 1
            
            # Sort books by borrow count and get top 5 (or all if ≤ 5 books)
            sorted_books = sorted(
                book_borrow_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            top_books = sorted_books[:5]
            
            if top_books:
                # Create matplotlib figure
                fig, ax = plt.subplots(figsize=(8, 4))
                
                # Prepare data for plotting
                book_names = []
                borrow_counts = []
                
                for isbn, count in top_books:
                    # Get book name from database
                    if isbn in self.dbroot.books:
                        book = self.dbroot.books[isbn]
                        # Truncate long book names
                        name = book.name if len(book.name) <= 20 else book.name[:17] + "..."
                        book_names.append(name)
                        borrow_counts.append(count)
                
                # Create bars
                x = np.arange(len(book_names))
                bars = ax.bar(x, borrow_counts, color=COLORS['primary'])
                
                # Customize graph
                ax.set_ylabel('Number of Times Borrowed')
                ax.set_title('Top 5 Most Borrowed Books')
                ax.set_xticks(x)
                ax.set_xticklabels(book_names, rotation=45, ha='right')
                
                # Add value labels on top of each bar
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom')
                
                # Adjust layout to prevent label cutoff
                plt.tight_layout()
                
                # Create canvas for matplotlib
                canvas = FigureCanvasTkAgg(fig, master=main_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
                
            else:
                ctk.CTkLabel(
                    main_frame,
                    text="No borrowing history available",
                    font=("Arial", 14),
                    text_color=COLORS['text_secondary']
                ).pack(pady=20)
        
        except Exception as e:
            print(f"Error displaying book statistics: {e}")
            ctk.CTkLabel(
                main_frame,
                text=f"Error loading statistics: {str(e)}",
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

    def contact(self):
        """Show contact information in a persistent popup window"""
        # Create contact window as an attribute so it persists
        self.contact_window = ctk.CTkToplevel()
        self.contact_window.title("Contact Information")
        self.contact_window.geometry("400x250")
        self.contact_window.resizable(False, False)
        
        # Make window stay on top and grab focus
        self.contact_window.transient(self)
        self.contact_window.grab_set()
        self.contact_window.focus_force()
        self.contact_window.lift()
        
        if hasattr(self.contact_window, 'attributes'):  # For Windows and Linux
            self.contact_window.attributes('-topmost', True)
        
        # Center the window on screen
        screen_width = self.contact_window.winfo_screenwidth()
        screen_height = self.contact_window.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 250) // 2
        self.contact_window.geometry(f"400x250+{x}+{y}")
        
        # Configure grid
        self.contact_window.grid_rowconfigure(0, weight=1)
        self.contact_window.grid_columnconfigure(0, weight=1)
        
        # Main frame with background color
        main_frame = ctk.CTkFrame(
            self.contact_window,
            fg_color="#f0f4ff",
            corner_radius=0
        )
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Title frame with blue background
        title_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#1e88e5",
            height=60,
            corner_radius=0
        )
        title_frame.pack(fill="x", pady=(0, 20))
        title_frame.pack_propagate(False)
        
        # Title
        ctk.CTkLabel(
            title_frame,
            text="Contact Us",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(pady=15)
        
        # Contact details frame
        contact_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        contact_frame.pack(fill="both", expand=True, padx=20)
        
        # Line contact with copy button
        line_frame = ctk.CTkFrame(contact_frame, fg_color="white")
        line_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            line_frame,
            text="Line ID:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1e88e5"
        ).pack(side="left", padx=10, pady=10)
        
        line_id = "@phoopwintchothar"
        ctk.CTkLabel(
            line_frame,
            text=line_id,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5, pady=10)
        
        copy_line_btn = ctk.CTkButton(
            line_frame,
            text="Copy",
            width=60,
            height=30,
            fg_color="#1e88e5",
            hover_color="#1976d2",
            command=lambda: self.copy_to_clipboard(line_id, "Line ID copied!")
        )
        copy_line_btn.pack(side="right", padx=10, pady=10)
        
        # Email contact with copy button
        email_frame = ctk.CTkFrame(contact_frame, fg_color="white")
        email_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            email_frame,
            text="Email:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1e88e5"
        ).pack(side="left", padx=10, pady=10)
        
        email = "phoopwintchothar1@gmail.com"
        ctk.CTkLabel(
            email_frame,
            text=email,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5, pady=10)
        
        copy_email_btn = ctk.CTkButton(
            email_frame,
            text="Copy",
            width=60,
            height=30,
            fg_color="#1e88e5",
            hover_color="#1976d2",
            command=lambda: self.copy_to_clipboard(email, "Email copied!")
        )
        copy_email_btn.pack(side="right", padx=10, pady=10)
        

    def copy_to_clipboard(self, text, message):
        """Copy text to clipboard and show notification"""
        self.clipboard_clear()
        self.clipboard_append(text)
        
        # Show notification
        notification = ctk.CTkToplevel(self.contact_window)  # Make notification a child of contact window
        notification.attributes('-topmost', True)
        notification.overrideredirect(True)
        
        # Position notification near the cursor
        x = self.contact_window.winfo_pointerx() + 10
        y = self.contact_window.winfo_pointery() + 10
        
        # Ensure notification stays within screen bounds
        screen_width = notification.winfo_screenwidth()
        screen_height = notification.winfo_screenheight()
        
        if x + 200 > screen_width:
            x = screen_width - 210
        if y + 40 > screen_height:
            y = screen_height - 50
            
        notification.geometry(f"200x40+{x}+{y}")
        
        # Notification label
        label = ctk.CTkLabel(
            notification,
            text=message,
            fg_color="#1e88e5",
            text_color="white",
            corner_radius=5
        )
        label.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Auto-close notification after 1.5 seconds
        notification.after(1500, notification.destroy)

    def borrow_book(self, book_data):
        book = self.dbroot.books[book_data['isbn']]
        user = self.dbroot.users[self.user_id] 
        if user.points<=0:
            messagebox.showinfo("Ineligible", f"Due to the late return of books on five occasions, your points are insufficient. Please contact staff to pay the fine and refill your point")
        elif len(user.borrowed_books)>=5:
            messagebox.showinfo("Ineligible", f"You cannot borrow more than 5 books without returning the ones you currently have.")
        elif not book_data['isbn'] in user.borrowed_books:
            # Create grid of borrowed books
            """Show borrow dialog and handle borrow process"""
            dialog = ctk.CTkToplevel(self)
            dialog.title("Borrow Book")
            dialog.grab_set()

            width, height = 500, 300
            x = (dialog.winfo_screenwidth() - width) // 2
            y = (dialog.winfo_screenheight() - height) // 2
            dialog.geometry(f"{width}x{height}+{x}+{y}")
            
            # Main frame
            main_frame = ctk.CTkFrame(dialog, fg_color=COLORS['white'])
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # Header
            header = ctk.CTkFrame(main_frame, fg_color=COLORS['primary'], height=60)
            header.pack(fill="x", pady=(0, 20))
            header.pack_propagate(False)

            ctk.CTkLabel(
                header,
                text=f"Borrow: {book_data['title']}",
                font=("Arial Bold", 18),
                text_color=COLORS['white']
            ).pack(side="left", padx=20, pady=10)

            # Start date display
            start_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['secondary'])
            start_frame.pack(fill="x", pady=10)
            
            start_date = datetime.now()
            start_date_str = start_date.strftime("%B %d, %Y")
            
            ctk.CTkLabel(
                start_frame,
                text="Start Date (Today):",
                font=("Arial Bold", 14)
            ).pack(side="left", padx=20, pady=10)
            
            ctk.CTkLabel(
                start_frame,
                text=start_date_str,
                fg_color=COLORS['white'],
                font=("Arial", 14)
            ).pack(side="left", padx=10, pady=10)

            # End date selection
            end_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['secondary'])
            end_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                end_frame,
                text="Return Date:",
                font=("Arial Bold", 14)
            ).pack(side="left", padx=20, pady=10)

            dates = [(start_date + timedelta(days=i)).strftime("%B %d, %Y") for i in range(1, 31)]
            date_objects = [start_date + timedelta(days=i) for i in range(1, 31)]
            end_date_var = ctk.StringVar(value=dates[0])
            
            end_date_dropdown = ctk.CTkOptionMenu(
                end_frame,
                variable=end_date_var,
                values=dates,
                width=200,
                text_color=COLORS['text_primary'],
                fg_color=COLORS['white'],
                button_color=COLORS['primary']
            )
            end_date_dropdown.pack(side="left", padx=10, pady=10)

            def show_success_message():
                selected_date = end_date_var.get()
                end_date = datetime.strptime(selected_date, "%B %d, %Y")
                
                with self.db_lock:
                    try:
                        
                        
                        if not hasattr(self.dbroot, 'borrow_records'):
                            self.dbroot.borrow_records = BTrees.OOBTree.BTree()
                            self.dbroot.borrow_id_counter = 0
                        
                        borrow_record = BorrowRecord(self.user_id, book_data['isbn'], start_date)
                        borrow_record.end_date = end_date
                        self.dbroot.borrow_id_counter += 1
                        self.dbroot.borrow_records[self.dbroot.borrow_id_counter] = borrow_record
                        
                        book.available_copies -= 1
                        if not hasattr(user, 'borrowed_books'):
                            user.borrowed_books = []

                    
                        user.borrowed_books.append(book_data['isbn'])
                        user.num_borrowed = len(user.borrowed_books)
                        transaction.commit()        
                        dialog.destroy()
                        
                        # Show success dialog
                        success_dialog = ctk.CTkToplevel(self)
                        success_dialog.title("Success")
                        success_dialog.grab_set()
                        
                        width, height = 400, 300
                        x = (success_dialog.winfo_screenwidth() - width) // 2
                        y = (success_dialog.winfo_screenheight() - height) // 2
                        success_dialog.geometry(f"{width}x{height}+{x}+{y}")
                        
                        frame = ctk.CTkFrame(success_dialog, fg_color=COLORS['white'])
                        frame.pack(fill="both", expand=True, padx=20, pady=20)
                        
                        ctk.CTkLabel(
                            frame,
                            text="Book Borrowed Successfully!",
                            font=("Arial Bold", 18),
                            text_color=COLORS['primary']
                        ).pack(pady=10)
                        
                        info_frame = ctk.CTkFrame(frame, fg_color=COLORS['secondary'])
                        info_frame.pack(fill="x", pady=10, padx=10)
                        
                        for text in [
                            f"Book: {book_data['title']}",
                            f"ISBN: {book_data['isbn']}",
                            f"From: {start_date_str}",
                            f"To: {selected_date}"
                        ]:
                            ctk.CTkLabel(
                                info_frame,
                                text=text,
                                font=("Arial", 14)
                            ).pack(pady=5)
                        
                        ctk.CTkButton(
                            frame,
                            text="OK",
                            fg_color=COLORS['primary'],
                            command=lambda: [success_dialog.destroy(),self.book_details_window.destroy(), self.load_books_from_database()]
                        ).pack(pady=10)                 
                    except Exception as e:
                        print(f"Error borrowing book: {e}")
                        transaction.abort()
            # Buttons
            buttons_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['white'])
            buttons_frame.pack(fill="x", pady=10)
            ctk.CTkButton(
                buttons_frame,
                text="Cancel",
                fg_color=COLORS['secondary'],
                text_color=COLORS['text_primary'],
                hover_color=COLORS['border'],
                width=100,
                command=dialog.destroy
            ).pack(side="left", padx=10)
            ctk.CTkButton(
                buttons_frame,
                text="Confirm",
                fg_color=COLORS['primary'],
                width=100,
                command=show_success_message
            ).pack(side="right", padx=10)
        else:
                messagebox.showinfo("Ineligible", f"You can't borrow the same book two times")

    def get_most_recent_borrow_record(self, isbn):
        """Get the most recent unreturned borrow record for a given book and user"""
        most_recent_record = None
        most_recent_date = None
        
        if hasattr(self.dbroot, 'borrow_records'):
            for borrow_record in self.dbroot.borrow_records.values():
                if borrow_record.isbn == isbn and borrow_record.user_id == self.user_id:
                    # Check if this borrow has been returned
                    is_returned = False
                    if hasattr(self.dbroot, 'all_records'):
                        for record in self.dbroot.all_records.values():
                            if (isinstance(record, ReturnRecord) and 
                                record.isbn == isbn and 
                                record.user_id == self.user_id and 
                                record.date > borrow_record.date):
                                is_returned = True
                                break
                    
                    # Only consider unreturned borrows
                    if not is_returned:
                        if most_recent_date is None or borrow_record.date > most_recent_date:
                            most_recent_record = borrow_record
                            most_recent_date = borrow_record.date
        
        return most_recent_record

    def show_borrowed_books(self):
        """Show borrowed books in a clean interface without header/sidebar"""
        self.borrowed_window = ctk.CTkToplevel(self)
        self.borrowed_window.title("Borrowed Books")
        self.borrowed_window.transient(self)
        self.borrowed_window.grab_set()
        
        # Set fullscreen
        screen_width = self.borrowed_window.winfo_screenwidth()
        screen_height = self.borrowed_window.winfo_screenheight()
        self.borrowed_window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.borrowed_window.resizable(False, False)
        self.borrowed_window.state('zoomed')
        self.borrowed_window.configure(fg_color=COLORS['white'])
        
        # Header frame
        header_frame = ctk.CTkFrame(self.borrowed_window, fg_color=COLORS['primary'], height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="My Borrowed Books",
            font=("Arial Bold", 24),
            text_color=COLORS['white']
        ).pack(side="left", padx=20, pady=20)
        
        back_button = ctk.CTkButton(
            header_frame,
            text="Back",
            fg_color=COLORS['secondary'],
            hover_color=COLORS['hover'],
            text_color=COLORS['text_primary'],
            command=self.borrowed_window.destroy
        )
        back_button.pack(side="right", padx=20, pady=20)
        
        # Main content frame with scrollable
        content_frame = ctk.CTkScrollableFrame(self.borrowed_window, fg_color=COLORS['white'])
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        grid_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['white'])
        grid_frame.pack(fill="both", expand=True)
        
        try:
            user = self.dbroot.users[self.user_id]
            borrowed_books = []
            current_date = datetime.now()

            # Get borrowed books details
            if hasattr(user, 'borrowed_books'):
                for isbn in user.borrowed_books:
                    if isbn in self.dbroot.books:
                        book = self.dbroot.books[isbn]
                        # Get most recent unreturned borrow record
                        borrow_record = self.get_most_recent_borrow_record(isbn)
                        
                        # Only if we found an unreturned borrow record
                        if borrow_record and hasattr(borrow_record, 'end_date'):
                            end_date = borrow_record.end_date
                            is_overdue = current_date > end_date
                        else:
                            end_date = None
                            is_overdue = False

                        borrowed_books.append({
                            'isbn': isbn,
                            'title': book.name,
                            'author': book.author,
                            'end_date': end_date,
                            'is_overdue': is_overdue,
                            'image_data': book.image_data if hasattr(book, 'image_data') else None
                        })


            # Create grid of borrowed books
            for i, book in enumerate(borrowed_books):
                row = i // 3
                col = i % 3
                frame_color = '#ffcccc' if book['is_overdue'] else '#ccffcc'
                book_frame = self.create_borrowed_book_frame(grid_frame, book, frame_color)
                book_frame.grid(row=row, column=col, padx=15, pady=15)
                
            # Configure grid columns
            for i in range(3):
                grid_frame.grid_columnconfigure(i, weight=1)
                
        except Exception as e:
            print(f"Error displaying borrowed books: {e}")

    def create_borrowed_book_frame(self, parent, book_data, frame_color):
        """Create frame for borrowed book display"""
        frame = ctk.CTkFrame(
            parent,
            width=250,
            height=350,
            fg_color=frame_color,
            border_color=COLORS['border'],
            border_width=1
        )
        frame.grid_propagate(False)

        if book_data.get('image_data'):
            try:
                image = Image.open(io.BytesIO(book_data['image_data']))
                image.thumbnail((210, 200))
                photo = ctk.CTkImage(light_image=image, dark_image=image, size=(210, 200))
                cover_label = ctk.CTkLabel(frame, text="", image=photo)
                cover_label.image = photo
                cover_label.place(relx=0.5, rely=0.3, anchor="center")
            except Exception as e:
                print(f"Error loading book cover: {e}")
                self._create_book_placeholder(frame, 250)
        else:
            self._create_book_placeholder(frame, 250)

        title_label = ctk.CTkLabel(
            frame,
            text=book_data['title'],
            wraplength=220,
            text_color=COLORS['text_primary'],
            font=("Arial Bold", 16)
        )
        title_label.place(relx=0.5, rely=0.65, anchor="center")

        author_label = ctk.CTkLabel(
            frame,
            text=book_data['author'],
            text_color=COLORS['text_secondary']
        )
        author_label.place(relx=0.5, rely=0.75, anchor="center")

        status_text = "OVERDUE" if book_data['is_overdue'] else book_data['end_date'].strftime("%B %d, %Y")
        status_label = ctk.CTkLabel(
            frame,
            text=f"Return by: {status_text}",
            text_color='red' if book_data['is_overdue'] else COLORS['text_primary']
        )
        status_label.place(relx=0.5, rely=0.85, anchor="center")

        def show_return_dialog():
            dialog = ctk.CTkToplevel()
            dialog.title("Book Details")
            dialog.geometry("400x300")
            dialog.grab_set()

            content = ctk.CTkFrame(dialog, fg_color=COLORS['white'])
            content.pack(fill="both", expand=True, padx=20, pady=20)

            ctk.CTkLabel(
                content, 
                text="Book Details",
                font=("Arial Bold", 18)
            ).pack(pady=10)

            details_frame = ctk.CTkFrame(content, fg_color=COLORS['secondary'])
            details_frame.pack(fill="x", pady=10)

            for label, value in [
                ("ISBN:", book_data['isbn']),
                ("Title:", book_data['title']),
                ("Due Date:", book_data['end_date'].strftime("%B %d, %Y"))
            ]:
                ctk.CTkLabel(
                    details_frame,
                    text=f"{label} {value}",
                    font=("Arial", 14),
                    anchor="w"
                ).pack(padx=20, pady=5)

            ctk.CTkButton(
                content,
                text="Return Book",
                command=lambda: self.handle_return(book_data['isbn'], dialog),
                fg_color=COLORS['primary']
            ).pack(pady=20)

        frame.bind("<Button-1>", lambda e: show_return_dialog())
        return frame

    def handle_return(self, isbn, dialog):
        """Process book return with confirmation and rating"""
        # Create confirmation dialog
        confirm_dialog = ctk.CTkToplevel(dialog)
        confirm_dialog.title("Confirm Return")
        confirm_dialog.grab_set()
        
        # Center the dialog
        width, height = 400, 200
        x = (confirm_dialog.winfo_screenwidth() - width) // 2
        y = (confirm_dialog.winfo_screenheight() - height) // 2
        confirm_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        frame = ctk.CTkFrame(confirm_dialog, fg_color=COLORS['white'])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text="Confirm Book Return",
            font=("Arial Bold", 18),
            text_color=COLORS['text_primary']
        ).pack(pady=10)
        
        ctk.CTkLabel(
            frame,
            text="Are you sure you want to return this book?",
            font=("Arial", 14),
            text_color=COLORS['text_secondary']
        ).pack(pady=10)
        
        button_frame = ctk.CTkFrame(frame, fg_color=COLORS['white'])
        button_frame.pack(fill="x", pady=20)
        
        def show_rating_dialog():
            confirm_dialog.destroy()
            dialog.destroy()
            
            rating_dialog = ctk.CTkToplevel(self)
            rating_dialog.title("Rate Book")
            rating_dialog.grab_set()
            
            width, height = 500, 400
            x = (rating_dialog.winfo_screenwidth() - width) // 2
            y = (rating_dialog.winfo_screenheight() - height) // 2
            rating_dialog.geometry(f"{width}x{height}+{x}+{y}")
            
            frame = ctk.CTkFrame(rating_dialog, fg_color=COLORS['white'])
            frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                frame,
                text="Book Successfully Returned!",
                font=("Arial Bold", 24),
                text_color=COLORS['primary']
            ).pack(pady=10)
            
            ctk.CTkLabel(
                frame,
                text="Please rate your reading experience:",
                font=("Arial", 16),
                text_color=COLORS['text_primary']
            ).pack(pady=20)
            
            # Rating stars frame
            stars_frame = ctk.CTkFrame(frame, fg_color=COLORS['white'])
            stars_frame.pack(pady=20)
            
            selected_rating = ctk.IntVar(value=5)
            star_buttons = []
            
            def update_stars(rating):
                selected_rating.set(rating)
                for i, btn in enumerate(star_buttons):
                    btn.configure(text="★" if i < rating else "☆")
                    btn.configure(text_color=COLORS['primary'] if i < rating else COLORS['text_secondary'])
            
            for i in range(5):
                star_btn = ctk.CTkButton(
                    stars_frame,
                    text="★",
                    width=50,
                    height=50,
                    fg_color="transparent",
                    text_color=COLORS['primary'],
                    hover_color=COLORS['secondary'],
                    font=("Arial", 24),
                    command=lambda x=i+1: update_stars(x)
                )
                star_btn.pack(side="left", padx=5)
                star_buttons.append(star_btn)
            
            def process_return(with_rating=True):
                try:
                    with self.db_lock:
                        book = self.dbroot.books[isbn]
                        user = self.dbroot.users[self.user_id]
                        
                        # Get most recent unreturned borrow record
                        borrow_record = self.get_most_recent_borrow_record(isbn)
                        current_date = datetime.now()
                        is_overdue = False
                        
                        if borrow_record and hasattr(borrow_record, 'end_date'):
                            is_overdue = current_date > borrow_record.end_date
                        
                        # Process the return
                        if isbn in user.borrowed_books:
                            book.available_copies += 1
                            user.borrowed_books.remove(isbn)
                            user.num_borrowed = len(user.borrowed_books)
                            
                            # Create return record
                            return_record = ReturnRecord(self.user_id, isbn, datetime.now())
                            if not hasattr(self.dbroot, 'all_records'):
                                self.dbroot.all_records = BTrees.OOBTree.BTree()
                                self.dbroot.record_id_counter = 0
                            self.dbroot.record_id_counter += 1
                            self.dbroot.all_records[self.dbroot.record_id_counter] = return_record

                            # Handle overdue deduction only if current borrow is overdue
                            if is_overdue:
                                if not hasattr(self.dbroot, 'points_records'):
                                    self.dbroot.points_records = BTrees.OOBTree.BTree()
                                    self.dbroot.points_id_counter = 0
                                                                
                                user.points -= 20
                                # Update button
                                if hasattr(self, 'profile_button'):
                                    self.profile_button.configure(text=f"{user.points} points")
                                    self.profile_button.text = f'{user.points}points'
                                point_reduced_record = PointDeductionRecord(self.user_id, isbn, datetime.now())
                                self.dbroot.points_id_counter += 1
                                self.dbroot.points_records[self.dbroot.points_id_counter] = point_reduced_record
                                self.dbroot.record_id_counter += 1
                                self.dbroot.all_records[self.dbroot.record_id_counter] = point_reduced_record

                            
                            # Add rating and review record only if not skipped
                            if with_rating:
                                rating = selected_rating.get()
                                book.total_ratings += 1
                                book.sum_ratings += rating
                                
                                review_record = ReviewRecord(self.user_id, isbn, datetime.now(), rating)
                                self.dbroot.record_id_counter += 1
                                self.dbroot.all_records[self.dbroot.record_id_counter] = review_record
                            
                            transaction.commit()
                            
                            # Show success message
                            success_dialog = ctk.CTkToplevel(rating_dialog)
                            success_dialog.title("Success")
                            success_dialog.grab_set()
                            
                            success_width, success_height = 300, 150
                            success_x = (success_dialog.winfo_screenwidth() - success_width) // 2
                            success_y = (success_dialog.winfo_screenheight() - success_height) // 2
                            success_dialog.geometry(f"{success_width}x{success_height}+{success_x}+{success_y}")
                            
                            success_frame = ctk.CTkFrame(success_dialog, fg_color=COLORS['white'])
                            success_frame.pack(fill="both", expand=True, padx=20, pady=20)
                            
                            
                            ctk.CTkLabel(
                                success_frame,
                                text="Book returned successfully!",
                                font=("Arial Bold", 16),
                                text_color=COLORS['primary']
                            ).pack(pady=20)
                            
                            ctk.CTkButton(
                                success_frame,
                                text="OK",
                                command=lambda: [success_dialog.destroy(), rating_dialog.destroy(),self.borrowed_window.destroy(),self.show_borrowed_books(), self.load_books_from_database()],
                                fg_color=COLORS['primary'],
                                hover_color=COLORS['primary_dark']
                            ).pack()
                            
                except Exception as e:
                    print(f"Error processing return and rating: {e}")
                    messagebox.showerror("Error", f"Failed to process return: {str(e)}")
                    transaction.abort()
                    rating_dialog.destroy()
            
            submit_button = ctk.CTkButton(
                frame,
                text="Submit Rating",
                font=("Arial", 14),
                fg_color=COLORS['primary'],
                hover_color=COLORS['primary_dark'],
                command=lambda: process_return(with_rating=True),
                width=200
            )
            submit_button.pack(pady=20)
            
            # Skip rating option
            skip_button = ctk.CTkButton(
                frame,
                text="Skip Rating",
                font=("Arial", 14),
                fg_color=COLORS['secondary'],
                text_color=COLORS['text_primary'],
                hover_color=COLORS['hover'],
                command=lambda: process_return(with_rating=False),
                width=200
            )
            skip_button.pack(pady=10)
        
        # Confirmation dialog buttons
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color=COLORS['secondary'],
            text_color=COLORS['text_primary'],
            hover_color=COLORS['hover'],
            command=confirm_dialog.destroy,
            width=100
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Confirm",
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            command=show_rating_dialog,
            width=100
        ).pack(side="right", padx=10)

    
    def on_closing(self):
        """Handle window closing with proper cleanup"""
        try:
            self.close_database()
            self.quit()
        except Exception as e:
            print(f"Error during cleanup: {e}")
            self.quit()