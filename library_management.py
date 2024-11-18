import ZODB
import ZODB.FileStorage
import transaction
import BTrees._OOBTree
from persistent import Persistent
from datetime import datetime
import sys
import hashlib
import os
from PIL import Image
import io
from abc import ABC, abstractmethod

class LibraryMembers(Persistent):

    def set_image(self, image_path):
        """Set the book's cover image from a file path."""
        try:
            with Image.open(image_path) as img:
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                max_size = (800, 800)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG', quality=85)
                self.image_data = img_byte_arr.getvalue()
                return True
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return False
        

    def get_image(self):
        """
        Return the image data if it exists.
        """
        if hasattr(self, 'image_data') and self.image_data:
            return self.image_data
        return None

    def has_image(self):
        """
        Check if the member has an image.
        """
        return hasattr(self, 'image_data') and self.image_data is not None

    def save_image(self, output_path):
        """
        Save the member's image to a file.
        """
        if self.has_image():
            try:
                with open(output_path, 'wb') as f:
                    f.write(self.image_data)
                return True
            except Exception as e:
                print(f"Error saving image: {str(e)}")
        return False
    
    

class User(LibraryMembers):
    def __init__(self, user_id, name, ph_number, faculty):
        self.user_id = user_id
        self.name = name
        self.points=100
        self.ph_number = ph_number
        self.birthdate = None
        self.faculty = str(faculty)
        self.borrowed_books = []
        self.num_borrowed = 0
        self.image_data = None
        # Set default image
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "logos", "default_user.png")
        if os.path.exists(logo_path):
            self.set_image(logo_path)
    
    def borrow_book(self, book_isbn, library_system):
        """Borrow a book and record the transaction"""
        if book_isbn not in self.borrowed_books:
            self.borrowed_books.append(book_isbn)
            self.num_borrowed = len(self.borrowed_books)
            # Create borrow record
            record = BorrowRecord(self.user_id, book_isbn, datetime.now())
            library_system.add_record(record)
            self._p_changed = True
            return True
        return False
            
    def return_book(self, book_isbn, library_system):
        """Return a book with optional rating"""
        if book_isbn in self.borrowed_books:
            self.borrowed_books.remove(book_isbn)
            self.num_borrowed = len(self.borrowed_books)
            
            # Get book rating from user
            try:
                rating = input("Rate the book (0-5) or press Enter to skip: ").strip()
                if rating:
                    rating = float(rating)
                    if 0 <= rating <= 5:
                        book = library_system.root.books[book_isbn]
                        book.add_rating(rating)
                        # Create review record
                        review_record = ReviewRecord(self.user_id, book_isbn, datetime.now(), rating)
                        library_system.add_record(review_record)
            except ValueError:
                print("Invalid rating, skipping review.")
            
            # Create return record
            return_record = ReturnRecord(self.user_id, book_isbn, datetime.now())
            library_system.add_record(return_record)
            
            self._p_changed = True
            return True
        return False
    

    def set_password(self, password):
        """Set password with salt and hashing"""
        self.password_salt = os.urandom(32)
        self.password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            self.password_salt,
            100000
        )

    def verify_password(self, password):
        """Verify a password against the hash"""
        if not hasattr(self, 'password_hash') or not hasattr(self, 'password_salt'):
            return False
            
        hash_to_check = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            self.password_salt,
            100000
        )
        return hash_to_check == self.password_hash
    


        
        

class Book(LibraryMembers):
    def __init__(self, isbn, name, author, description, copies):
       
        self.isbn = isbn
        self.name = name
        self.author = author
        self.description = description
        self.total_copies = copies
        self.available_copies = copies
        self.image_data = None
        self.genre = None
        # Initialize review attributes
        self.total_ratings = 0
        self.sum_ratings = 0
        self.average_rating = 0.0
        
        # Set default image
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "logos", "default_book.png")
        if os.path.exists(logo_path):
            self.set_image(logo_path)
            
    def add_rating(self, rating):
        """Add a new rating and update the average"""
        if 0 <= rating <= 5:
            self.total_ratings += 1
            self.sum_ratings += rating
            self.average_rating = round(self.sum_ratings / self.total_ratings, 2)
            self._p_changed = True


class Record(Persistent):
    def __init__(self, user_id, isbn, date, action):
        self.user_id = user_id
        self.isbn = isbn
        self.date = date
        self.action = action
        self.end_date=None

    def print_statement(self):
        return f"{self.user_id} {self.action} Book ID- {self.isbn} on {self.date}"

class BorrowRecord(Record):
    def __init__(self, user_id, isbn, start_date):

        super().__init__(user_id, isbn, start_date, "borrowed")
        self.end_date=None

class ReturnRecord(Record):
    def __init__(self, user_id, isbn, return_date):
        super().__init__(user_id, isbn, return_date, "returned")

class ReviewRecord(Record):
    def __init__(self, user_id, isbn, review_date, rating):
        super().__init__(user_id, isbn, review_date, "reviewed")
        self.rating = rating

 
class PointDeductionRecord(Record):
    def __init__(self, user_id, isbn, deduction_date):
        super().__init__(user_id, isbn, deduction_date, " 10 points deducted for overdue book.")


  

