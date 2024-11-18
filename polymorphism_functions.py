import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import time
import threading
import os
from PIL import Image, ImageDraw, ImageTk
from tkinter import messagebox, filedialog
import transaction
import io

Faculties=[
                "Faculty of Engineering",
                "Faculty of Architecture",
                "Faculty of Science",
                "Faculty of Agricultural Technology",
                "Faculty of Information Technology",
                "Faculty of Industrial Education",
                "Faculty of Business Administration",
                "Faculty of Liberal Arts",
                "Faculty of Medicine"]

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



def close_database(self):
        """Safely close database connections"""
        try:
            if hasattr(self, 'connection'):
                self.connection.close()
            if hasattr(self, 'db'):
                self.db.close()
            if hasattr(self, 'storage'):
                self.storage.close()
        except Exception as e:
            print(f"Error closing database: {e}")


def edit_book_information(item, book_id):
    """Show user profile with editing capabilities"""
    try:
        # Get user data from database
        close_database(item)
        item.setup_database()
        
        if hasattr(item.dbroot, 'books') and book_id in item.dbroot.books:
            book = item.dbroot.books[book_id]
            
            profile_window = ctk.CTkToplevel(item)
            profile_window.title("Book Inforamtion")
            profile_window.transient(item)
            profile_window.grab_set()
            
            # Set window properties
            screen_width = profile_window.winfo_screenwidth()
            screen_height = profile_window.winfo_screenheight()
            profile_window.geometry(f"{screen_width}x{screen_height}+0+0")
            profile_window.resizable(False, False)
            profile_window.state('zoomed')
            profile_window.configure(fg_color=COLORS['white'])
            
            # Header frame
            header_frame = ctk.CTkFrame(profile_window, fg_color=COLORS['primary'], height=80)
            header_frame.pack(fill="x")
            header_frame.pack_propagate(False)
            
            ctk.CTkLabel(
                header_frame,
                text="Book Information" ,
                font=("Arial Bold", 24),
                text_color=COLORS['white']
            ).pack(side="left", padx=20, pady=20)
            
            # Save and Back buttons
            buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            buttons_frame.pack(side="right", padx=20, pady=20)
            
            save_button = ctk.CTkButton(
                buttons_frame,
                text="Save Changes",
                fg_color=COLORS['secondary'],
                hover_color=COLORS['hover'],
                text_color=COLORS['text_primary'],
                command=lambda: save_book_changes(item,book_id, book, photo_frame, name_var, author_var,descr_var, copies_var, genre_var)
            )
            save_button.pack(side="right", padx=10)
            
            back_button = ctk.CTkButton(
                buttons_frame,
                text="Back",
                fg_color=COLORS['secondary'],
                hover_color=COLORS['hover'],
                text_color=COLORS['text_primary'],
                command=profile_window.destroy
            )
            back_button.pack(side="right", padx=10)
            
            # Main content
            content_frame = ctk.CTkFrame(profile_window, fg_color=COLORS['white'])
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)
            content_frame.grid_columnconfigure((0, 1), weight=1)
            
            # Left side - Photo and basic info
            left_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['white'])
            left_frame.grid(row=0, column=0, sticky="nsew", padx=10)
            
            # Photo frame
            photo_frame = ctk.CTkFrame(
                left_frame,
                width=300,
                height=400,
                fg_color=COLORS['secondary']
            )
            photo_frame.pack(pady=20)
            photo_frame.pack_propagate(False)

            
            # Load and display user photo
            display_user_photo(item, photo_frame, book)
            
            
            # Upload photo button
            upload_button = ctk.CTkButton(
                left_frame,
                text="Change Photo",
                command=lambda: change_book_photo(book_id, item, book, photo_frame)
            )
            upload_button.pack(pady=10)
            
            # Right side - Editable information
            right_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['white'])
            right_frame.grid(row=0, column=1, sticky="nsew", padx=10)
            
            # User information fields
            info_frame = ctk.CTkFrame(right_frame, fg_color=COLORS['secondary'])
            info_frame.pack(fill="x", pady=10)
            
            # Book ID (non-editable)
            id_frame = create_info_field(info_frame, "Book ID", book.isbn, editable=False)
            id_frame.pack(fill="x", pady=5, padx=10)
            
            # Name (editable)
            name_var = ctk.StringVar(value=book.name)
            name_frame = create_info_field(info_frame, "Book Name", book.name, variable=name_var)
            name_frame.pack(fill="x", pady=5, padx=10)
            
            # Author (editable)
            author_var = ctk.StringVar(value=book.author)
            author_frame = create_info_field(info_frame, "Author", book.author, variable=author_var)
            author_frame.pack(fill="x", pady=5, padx=10)

            # Description (editable)
            descr_var = ctk.StringVar(value=book.description)
            descr_frame = create_info_field(info_frame, "Description", book.description, variable=descr_var)
            descr_frame.pack(fill="x", pady=5, padx=10)

            # Copies (editable)
            copies_var = ctk.StringVar(value=book.available_copies)
            copies_frame = create_info_field(info_frame, "Available Copies", book.available_copies, variable=copies_var)
            copies_frame.pack(fill="x", pady=5, padx=10)
            
            # Genere (editable dropdown)
            genre_var = ctk.StringVar(value=book.genre)
            genere_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            genere_frame.pack(fill="x", pady=5, padx=10)
            
            ctk.CTkLabel(
                genere_frame,
                text="Genere:",
                font=("Arial", 14),
                anchor="w"
            ).pack(side="left", padx=(0, 10))
            
            genere_menu = ctk.CTkOptionMenu(
                genere_frame,
                variable=genre_var,
                values=item.Genres,
                text_color="black",
                fg_color=COLORS['white'],
                button_color=COLORS['primary']
            )
            genere_menu.pack(side="left", fill="x", expand=True)               
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load book details: {e}")
    finally:
        close_database(item)



def edit_user_information(item, user_id):
    """Show user profile with editing capabilities"""
    try:
        # Get user data from database
        close_database(item)
        item.setup_database()
        
        if hasattr(item.dbroot, 'users') and user_id in item.dbroot.users:
            user = item.dbroot.users[user_id]
            
            profile_window = ctk.CTkToplevel(item)
            profile_window.title("User Inforamtion")

            profile_window.transient(item)
            profile_window.grab_set()
            
            # Set window properties
            screen_width = profile_window.winfo_screenwidth()
            screen_height = profile_window.winfo_screenheight()
            profile_window.geometry(f"{screen_width}x{screen_height}+0+0")
            profile_window.resizable(False, False)
            profile_window.state('zoomed')
            profile_window.configure(fg_color=COLORS['white'])
            
            # Header frame
            header_frame = ctk.CTkFrame(profile_window, fg_color=COLORS['primary'], height=80)
            header_frame.pack(fill="x")
            header_frame.pack_propagate(False)
            
            ctk.CTkLabel(
                header_frame,
                text="User Information" ,
                font=("Arial Bold", 24),
                text_color=COLORS['white']
            ).pack(side="left", padx=20, pady=20)
            
            # Save and Back buttons
            buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            buttons_frame.pack(side="right", padx=20, pady=20)
            
            save_button = ctk.CTkButton(
                buttons_frame,
                text="Save Changes",
                fg_color=COLORS['secondary'],
                hover_color=COLORS['hover'],
                text_color=COLORS['text_primary'],
                command=lambda: save_profile_changes(item,user_id, user, photo_frame, name_var, phone_var, faculty_var)
            )
            save_button.pack(side="right", padx=10)
            
            back_button = ctk.CTkButton(
                buttons_frame,
                text="Back",
                fg_color=COLORS['secondary'],
                hover_color=COLORS['hover'],
                text_color=COLORS['text_primary'],
                command=profile_window.destroy
            )
            back_button.pack(side="right", padx=10)
            
            # Main content
            content_frame = ctk.CTkFrame(profile_window, fg_color=COLORS['white'])
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)
            content_frame.grid_columnconfigure((0, 1), weight=1)
            
            # Left side - Photo and basic info
            left_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['white'])
            left_frame.grid(row=0, column=0, sticky="nsew", padx=10)
            
            # Photo frame
            photo_frame = ctk.CTkFrame(
                left_frame,
                width=300,
                height=400,
                fg_color=COLORS['secondary']
            )
            photo_frame.pack(pady=20)
            photo_frame.pack_propagate(False)

            
            # Load and display user photo
            display_user_photo(item, photo_frame, user)
            
            
            # Upload photo button
            upload_button = ctk.CTkButton(
                left_frame,
                text="Change Photo",
                command=lambda: change_profile_photo(user_id, item, user, photo_frame)
            )
            upload_button.pack(pady=10)
            
            # Right side - Editable information
            right_frame = ctk.CTkFrame(content_frame, fg_color=COLORS['white'])
            right_frame.grid(row=0, column=1, sticky="nsew", padx=10)
            
            # User information fields
            info_frame = ctk.CTkFrame(right_frame, fg_color=COLORS['secondary'])
            info_frame.pack(fill="x", pady=10)
            
            # User ID (non-editable)
            id_frame = create_info_field(info_frame, "User ID", user.user_id, editable=False)
            id_frame.pack(fill="x", pady=5, padx=10)
            
            # Name (editable)
            name_var = ctk.StringVar(value=user.name)
            name_frame = create_info_field(info_frame, "Name", user.name, variable=name_var)
            name_frame.pack(fill="x", pady=5, padx=10)
            
            # Phone (editable)
            phone_var = ctk.StringVar(value=user.ph_number)
            phone_frame = create_info_field(info_frame, "Phone", user.ph_number, variable=phone_var)
            phone_frame.pack(fill="x", pady=5, padx=10)
            
            # Faculty (editable dropdown)
            faculty_var = ctk.StringVar(value=user.faculty)
            faculty_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            faculty_frame.pack(fill="x", pady=5, padx=10)
            
            ctk.CTkLabel(
                faculty_frame,
                text="Faculty:",
                font=("Arial", 14),
                anchor="w"
            ).pack(side="left", padx=(0, 10))
            
            faculty_menu = ctk.CTkOptionMenu(
                faculty_frame,
                variable=faculty_var,
                values=Faculties,
                text_color="black",
                fg_color=COLORS['white'],
                button_color=COLORS['primary']
            )
            faculty_menu.pack(side="left", fill="x", expand=True)               
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load profile: {e}")
    finally:
        close_database(item)

def create_info_field( parent, label, value, variable=None, editable=True):
    """Create an information field for the profile"""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    
    # Create label
    ctk.CTkLabel(
        frame,
        text=f"{label}:",
        font=("Arial", 14),
        anchor="w"
    ).pack(side="left", padx=(0, 10))
    
    # Handle editable fields
    if editable and variable:
        # Initialize entry with the variable
        entry = ctk.CTkEntry(
            frame,
            textvariable=variable,
            fg_color=COLORS['white'],
            border_color=COLORS['border']
        )
        # Set initial value if not already set
        if not variable.get():
            variable.set(value)
        entry.pack(side="left", fill="x", expand=True)
        
        # Bind focus events to handle input validation
        def on_focus_out(event):
            current_value = variable.get()
            if not current_value or not current_value.strip():
                variable.set(value)  # Reset to original value if empty
                
        entry.bind('<FocusOut>', on_focus_out)
        
    else:
        # Non-editable label
        ctk.CTkLabel(
            frame,
            text=str(value),
            font=("Arial", 14),
            anchor="w",
            fg_color=COLORS['white'],
            corner_radius=6,
            padx=10
        ).pack(side="left", fill="x", expand=True)
    
    return frame
    
def change_profile_photo(user_id, item, user, photo_frame):
        """Handle profile photo change with proper error handling and database updates"""
        try:
            # Reopen database connection to ensure fresh state
            close_database(item)
            item.setup_database()
            
            # Get fresh user object
            if not hasattr(item.dbroot, 'users') or user_id not in item.dbroot.users:
                raise ValueError("User not found in database")
            
            user = item.dbroot.users[user_id]
            
            filename = filedialog.askopenfilename(
                title="Select Profile Photo",
                filetypes=(
                    ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                    ("All files", "*.*")
                )
            )
            
            if filename:
                # Read and process the image
                with open(filename, 'rb') as f:
                    image_data = f.read()
                    
                # Validate image data
                try:
                    # Test if image can be opened
                    test_image = Image.open(io.BytesIO(image_data))
                    test_image.verify()  # Verify image integrity
                    
                    # If verification passes, reopen image for processing
                    image = Image.open(io.BytesIO(image_data))
                    
                    # Convert to RGB if necessary
                    if image.mode not in ('RGB', 'RGBA'):
                        image = image.convert('RGB')
                    
                    # Resize image if too large
                    max_size = (800, 800)
                    image.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Save processed image to bytes
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    processed_image_data = img_byte_arr.getvalue()
                    
                    # Update user object with new image data
                    user.image_data = processed_image_data
                    
                    # Commit transaction
                    transaction.commit()
                    
                    # Update display
                    display_user_photo(item, photo_frame, user)
                    item.update_profile_button_image(processed_image_data)
                    
                    messagebox.showinfo("Success", "Profile photo updated successfully!")
                    
                except Exception as img_error:
                    raise ValueError(f"Invalid image file: {str(img_error)}")
                    
        except Exception as e:
            print(f"Error changing profile photo: {e}")
            messagebox.showerror("Error", f"Failed to update profile photo: {str(e)}")
            transaction.abort()
       


def change_book_photo(book_id, item, book, photo_frame):
        """Handle profile photo change with proper error handling and database updates"""
        try:
            # Reopen database connection to ensure fresh state
            close_database(item)
            item.setup_database()
            
            # Get fresh user object
            if not hasattr(item.dbroot, 'books') or book_id not in item.dbroot.books:
                raise ValueError("Book not found in database")
            
            book = item.dbroot.books[book_id]
            
            filename = filedialog.askopenfilename(
                title="Select Book Photo",
                filetypes=(
                    ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                    ("All files", "*.*")
                )
            )
            
            if filename:
                # Read and process the image
                with open(filename, 'rb') as f:
                    image_data = f.read()
                    
                # Validate image data
                try:
                    # Test if image can be opened
                    test_image = Image.open(io.BytesIO(image_data))
                    test_image.verify()  # Verify image integrity
                    
                    # If verification passes, reopen image for processing
                    image = Image.open(io.BytesIO(image_data))
                    
                    # Convert to RGB if necessary
                    if image.mode not in ('RGB', 'RGBA'):
                        image = image.convert('RGB')
                    
                    # Resize image if too large
                    max_size = (800, 800)
                    image.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Save processed image to bytes
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    processed_image_data = img_byte_arr.getvalue()
                    
                    # Update user object with new image data
                    book.image_data = processed_image_data
                    
                    # Commit transaction
                    transaction.commit()
                    
                    # Update display
                    display_book_photo(item, photo_frame, book)
                    item.update_profile_button_image(processed_image_data)
                    
                    messagebox.showinfo("Success", "Book photo updated successfully!")
                    
                except Exception as img_error:
                    raise ValueError(f"Invalid image file: {str(img_error)}")
                    
        except Exception as e:
            print(f"Error changing book photo: {e}")
            messagebox.showerror("Error", f"Failed to update book photo: {str(e)}")
            transaction.abort()
        finally:
            close_database(item)

def save_book_changes(item,book_id, book, photo_frame, name_var, author_var,descr_var, copies_var, genre_var):
        """Save profile changes to the database with proper error handling."""
        try:
            # Basic validation
            if book is None:
                raise ValueError("Book object is missing")
                
            # Store values immediately after retrieval
            # This prevents potential issues with StringVar objects being destroyed
            try:
                new_name = name_var.get() if isinstance(name_var, ctk.StringVar) else None
                new_author= author_var.get() if isinstance(author_var, ctk.StringVar) else None
                new_descr= descr_var.get() if isinstance(descr_var, ctk.StringVar) else None
                new_copies= copies_var.get() if isinstance(copies_var, ctk.StringVar) else None
                new_genre = genre_var.get() if isinstance(genre_var, ctk.StringVar) else None
                
                # Debug output
                #print(f"Retrieved values - Name: {new_name}, Phone: {new_phone}, Faculty: {new_faculty}")
                
                # Early validation of retrieved values
                if any(v is None for v in [new_name, new_author, new_descr,new_copies,new_genre ]):
                    raise ValueError("Failed to retrieve one or more form values")
                    
            except Exception as e:
                print(f"Error retrieving values: {e}")
                # Use existing user values as fallback
                new_name = getattr(book, 'name', '')
                new_author = getattr(book, 'author', '')
                new_descr = getattr(book, 'description', '')
                new_copies= getattr(book, 'available_copies', '')
                new_genre = getattr(book, 'genre', '')
                #print(f"Using fallback values - Name: {new_name}, Phone: {new_phone}, Faculty: {new_faculty}")

            # Validate values
            if not new_name or not new_name.strip():
                raise ValueError("Name cannot be empty")
            
            if not new_author or not new_author.strip():
                raise ValueError("Author cannot be empty")
            
            
            if not new_descr or not new_descr.strip():
                raise ValueError("Description cannot be empty")
            
            
            if not new_copies or not new_copies.strip() or int(new_copies.strip())<=0:
                raise ValueError("Available copies is not valid")
            
    
                
            if not hasattr(item, 'Genres'):
                Genres = [
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
                
            if new_genre not in item.Genres:
                raise ValueError(f"Invalid faculty selection: {new_genre}. Must be one of: {', '.join(Genres)}")

            # Store the values directly
            close_database(item)  # Close any existing connection
            item.setup_database() # Reopen the connection
            
            # Ensure we have a valid user object after reconnecting
            if hasattr(item.dbroot, 'books') and book_id in item.dbroot.books:
                book = item.dbroot.books[book_id]
                
                # Update user object
                book.name = new_name
                book.author = new_author
                book.description = new_descr
                book.genre=new_genre
                added_copies=int(new_copies)-int(book.available_copies)
                book.total_copies+=added_copies
                book.available_copies=int(new_copies)

                # Commit changes
                transaction.commit()

                # Update profile photo if available
                if hasattr(book, 'image_data') and book.image_data:
                    item.update_profile_button_image(book.image_data)

                messagebox.showinfo("Success", "Book updated successfully!")
                return True
            else:
                raise ValueError("Book not found in database after reconnection")

        except ValueError as ve:
            print(f"Validation error: {ve}")
            messagebox.showerror("Error", str(ve))
            transaction.abort()
            return False
            
        except Exception as e:
            print(f"Unexpected error: {e}")
            messagebox.showerror("Error", f"Failed to save changes: {e}")
            transaction.abort()
            return False
        finally:
            close_database(item)  # Ensure database connection is closed


def save_profile_changes(item,user_id, user, photo_frame, name_var, phone_var, faculty_var):
        """Save profile changes to the database with proper error handling."""
        try:
            # Basic validation
            if user is None:
                raise ValueError("User object is missing")
                
            # Store values immediately after retrieval
            # This prevents potential issues with StringVar objects being destroyed
            try:
                new_name = name_var.get() if isinstance(name_var, ctk.StringVar) else None
                new_phone = phone_var.get() if isinstance(phone_var, ctk.StringVar) else None
                new_faculty = faculty_var.get() if isinstance(faculty_var, ctk.StringVar) else None
                
                
                # Early validation of retrieved values
                if any(v is None for v in [new_name, new_phone, new_faculty]):
                    raise ValueError("Failed to retrieve one or more form values")
                    
            except Exception as e:
                print(f"Error retrieving values: {e}")
                # Use existing user values as fallback
                new_name = getattr(user, 'name', '')
                new_phone = getattr(user, 'ph_number', '')
                new_faculty = getattr(user, 'faculty', '')
                print(f"Using fallback values - Name: {new_name}, Phone: {new_phone}, Faculty: {new_faculty}")

            # Validate values
            if not new_name or not new_name.strip():
                raise ValueError("Name cannot be empty")
            
            if not new_phone or not new_phone.strip():
                raise ValueError("Phone number cannot be empty")
                
            if not hasattr(item, 'Faculties'):
                Faculties=[
                "Faculty of Engineering",
                "Faculty of Architecture",
                "Faculty of Science",
                "Faculty of Agricultural Technology",
                "Faculty of Information Technology",
                "Faculty of Industrial Education",
                "Faculty of Business Administration",
                "Faculty of Liberal Arts",
                "Faculty of Medicine"]
                
            if new_faculty not in item.Faculties:
                raise ValueError(f"Invalid faculty selection: {new_faculty}. Must be one of: {', '.join(Faculties)}")

            # Store the values directly
            close_database(item)  # Close any existing connection
            item.setup_database() # Reopen the connection
            
            # Ensure we have a valid user object after reconnecting
            if hasattr(item.dbroot, 'users') and user_id in item.dbroot.users:
                user = item.dbroot.users[user_id]
                
                # Update user object
                user.name = new_name
                user.ph_number = new_phone
                user.faculty = new_faculty

                # Commit changes
                transaction.commit()

                # Update profile photo if available
                if hasattr(user, 'image_data') and user.image_data:
                    item.update_profile_button_image(user.image_data)

                messagebox.showinfo("Success", "Profile updated successfully!")
                return True
            else:
                raise ValueError("User not found in database after reconnection")

        except ValueError as ve:
            print(f"Validation error: {ve}")
            messagebox.showerror("Error", str(ve))
            transaction.abort()
            return False
            
        except Exception as e:
            print(f"Unexpected error: {e}")
            messagebox.showerror("Error", f"Failed to save changes: {e}")
            transaction.abort()
            return False




def show_default_profile_photo(item, frame):
        """Show default profile photo"""
        try:
            current_dir = os.path.dirname(os.path.dirname(__file__))
            default_path = os.path.join(current_dir, "logos", "default_user.png")
            
            image = Image.open(default_path)
            image.thumbnail((280, 380))
            photo = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
            label = ctk.CTkLabel(frame, image=photo, text="")
            label.image = photo
            label.pack(expand=True)
        except Exception as e:
            print(f"Error loading default photo: {e}")
            ctk.CTkLabel(
                frame,
                text="No Photo\nAvailable",
                font=("Arial", 14)
            ).pack(expand=True)



def show_default_book_photo(item, frame):
        """Show default profile photo"""
        try:
            current_dir = os.path.dirname(os.path.dirname(__file__))
            default_path = os.path.join(current_dir, "logos", "default_book.png")
            
            image = Image.open(default_path)
            image.thumbnail((280, 380))
            photo = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
            label = ctk.CTkLabel(frame, image=photo, text="")
            label.image = photo
            label.pack(expand=True)
        except Exception as e:
            print(f"Error loading default photo: {e}")
            ctk.CTkLabel(
                frame,
                text="No Photo\nAvailable",
                font=("Arial", 14)
            ).pack(expand=True)


    

def display_user_photo(item, frame, user):
    """Display user photo in frame with error handling"""
    try:
        # Clear existing content
        for widget in frame.winfo_children():
            widget.destroy()
        
        if hasattr(user, 'image_data') and user.image_data:
            # Create a copy of the image data
            image_data = io.BytesIO(user.image_data)
            image = Image.open(image_data)
            
            # Convert if necessary
            if image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGB')
            
            # Resize while maintaining aspect ratio
            display_size = (280, 380)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Create CTkImage
            photo = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=image.size
            )
            
            # Create and pack label
            label = ctk.CTkLabel(frame, image=photo, text="")
            label.image = photo  # Keep reference
            label.pack(expand=True)
        else:
            show_default_profile_photo(item, frame)
            
    except Exception as e:
        print(f"Error displaying user photo: {e}")
        show_default_profile_photo(item, frame)

def display_book_photo(item, frame, book):
    """Display user photo in frame with error handling"""
    try:
        # Clear existing content
        for widget in frame.winfo_children():
            widget.destroy()
        
        if hasattr(book, 'image_data') and book.image_data:
            # Create a copy of the image data
            image_data = io.BytesIO(book.image_data)
            image = Image.open(image_data)
            
            # Convert if necessary
            if image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGB')
            
            # Resize while maintaining aspect ratio
            display_size = (280, 380)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Create CTkImage
            photo = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=image.size
            )
            
            # Create and pack label
            label = ctk.CTkLabel(frame, image=photo, text="")
            label.image = photo  # Keep reference
            label.pack(expand=True)
        else:
            show_default_profile_photo(item, frame)
            
    except Exception as e:
        print(f"Error displaying user photo: {e}")
        show_default_profile_photo(item, frame)
