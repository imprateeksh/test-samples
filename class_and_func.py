# Define a class called 'Person'
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        print(f"Hello, my name is {self.name} and I am {self.age} years old.")

# Define a class called 'Book'
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

    def display_info(self):
        print(f"Title: {self.title}\nAuthor: {self.author}")

# Function outside the classes
def greet():
    print("Welcome to our Python program!")

# Function to create a library of books
def create_library():
    library = []
    book1 = Book("Python Programming", "John Smith")
    book2 = Book("Machine Learning Basics", "Alice Johnson")
    book3 = Book("Data Science for Beginners", "Bob Davis")
    library.extend([book1, book2, book3])
    return library

# Function to display the library of books
def display_library(library):
    for book in library:
        book.display_info()

# Function to introduce people
def introduce_people():
    person1 = Person("Alice", 25)
    person2 = Person("Bob", 30)
    person1.introduce()
    person2.introduce()

# Main function
def main():
    greet()
    library = create_library()
    print("\nLibrary of Books:")
    display_library(library)
    print("\nIntroducing People:")
    introduce_people()

if __name__ == "__main__":
    main()
