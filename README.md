# Library Management System
#### A Python-based digital library management system designed to streamline library operations and enhance user experience. This system provides tools for efficient catalog management, user activity tracking, and data-driven decision-making for libraries of any scale.

## Features
### For Students/Faculty:
#### -Browse and search books by title, author, or genre.
#### -View book availability and details.
#### -Borrow up to 5 books simultaneously.
#### -Rate and review books upon return.
#### -Track borrowed books and due dates.
#### -View personal borrowing history.
#### -Earn points for timely returns.

### For Administrators:
#### -Manage book catalog (add, edit, delete books).
#### -Monitor overdue books and user activities.
#### -Generate statistical reports.
#### -Track library inventory.
#### -Manage users and reset points/passwords.


### Security:
#### -Passwoed hashing with salt
#### -Role based access control
#### -Session Management

## Prerequisites
#### -Python 3.10 or above.
#### -Required Python libraries:
##### ~CustomTkinter: For GUI.
##### ~ZODB: For database management.
##### ~Matplotlib: For data visualization.
##### ~Pillow (PIL): For image handling.
#### Install the dependencies using the following command:
##### pip install -r requirements.txt

## Project Setup
#### 1.Clone the repository:
##### git clone https://github.com/PhooPwintChoThar/Library-Management-System
##### cd library-management-system

#### 2.Create a database file for storing user and book information:
##### ~The project uses ZODB for database management.
##### ~A library.fs file will be created in the project directory during the first run.

#### 3.Run the application:
##### python login_page.py

## Application Workflow
### For Users:
#### -Login or register a new account.
#### -Browse or search for books by title, author, or genre.
#### -Borrow books and track their due dates.
#### -Rate and review books after returning them.
### For Administrators:
#### -Login with an admin account.
#### -Manage books and users via a dedicated admin dashboard.
#### -View and generate statistics on books and user activities.

## Screenshots
### Admin Features

#### Login Page
![Screenshot (347)](https://github.com/user-attachments/assets/0997d0a2-fa57-4059-860c-597cf78f2a73)

#### Admin Main Page
![Screenshot (348)](https://github.com/user-attachments/assets/626a4a14-6124-4da0-8266-79f8b6620dcd)

#### Borrow and Return Records
![Screenshot (349)](https://github.com/user-attachments/assets/de42b9c3-7425-4dbe-9594-6d957e5c1578)

#### User Statistics
![Screenshot (350)](https://github.com/user-attachments/assets/40aec260-aa6a-44e7-ab3e-1b8fccc628fc)

#### Book Statistics
![Screenshot (351)](https://github.com/user-attachments/assets/d09561e8-38d6-4d76-a0f1-690ab03eb265)

#### Add New User
![Screenshot (352)](https://github.com/user-attachments/assets/9f338eba-411d-4fef-ab53-4be448f43d8e)

#### Add New Book
![Screenshot (353)](https://github.com/user-attachments/assets/879dc49f-e2e8-4e50-973a-48c019d04e6e)

### User Features

#### User Main Page
![Screenshot (357)](https://github.com/user-attachments/assets/e644fa28-5fd6-4381-967f-000a1f26af25)

#### Borrow Records , Return , Review
![Screenshot (363)](https://github.com/user-attachments/assets/8fae8847-cd27-4e69-9aa7-7ebdaa34daa7)

#### Activity History and Statistics
![Screenshot (365)](https://github.com/user-attachments/assets/6e1749e9-7ff7-4956-b91d-fd32c0210327)
![Screenshot (366)](https://github.com/user-attachments/assets/82c7fe8b-ffcd-4007-8efd-cb469c717639)

#### Popular Book
![Screenshot (367)](https://github.com/user-attachments/assets/f2701b52-ac99-49e7-b81e-7cadace622ff)


#### Book Details and Borrow Book
![Screenshot (368)](https://github.com/user-attachments/assets/ccd54621-365d-4fc4-b226-9a9399e18491)

#### Change Profile
![Screenshot (370)](https://github.com/user-attachments/assets/7c5aff0b-cf3a-48dc-a06a-6c9dc5205612)













