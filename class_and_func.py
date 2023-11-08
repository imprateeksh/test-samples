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

# Define a class for Products
class Product:
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

    def display_info(self):
        print(f"Product: {self.name}\nPrice: ${self.price}\nStock: {self.stock} units")

# Define a class for Customers
class Customer:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.cart = []

    def add_to_cart(self, product, quantity=1):
        if product.stock >= quantity:
            self.cart.append((product, quantity))
            product.stock -= quantity
            print(f"{quantity} {product.name}(s) added to your cart.")
        else:
            print(f"Sorry, not enough stock of {product.name} to add to your cart.")

    def view_cart(self):
        if not self.cart:
            print("Your cart is empty.")
        else:
            print("Your Shopping Cart:")
            total_price = 0
            for product, quantity in self.cart:
                print(f"{product.name} x{quantity}: ${product.price * quantity}")
                total_price += product.price * quantity
            print(f"Total: ${total_price}")

# Define a class for Orders
class Order:
    def __init__(self, customer, products):
        self.customer = customer
        self.products = products
        self.total_price = sum(product.price * quantity for product, quantity in products)

    def display_order(self):
        print(f"Order for {self.customer.name}:")
        for product, quantity in self.products:
            print(f"{product.name} x{quantity}: ${product.price * quantity}")
        print(f"Total: ${self.total_price}")

# Define a class for an Online Store
class OnlineStore:
    def __init__(self):
        self.products = [
            Product("Laptop", 800, 10),
            Product("Phone", 400, 20),
            Product("Tablet", 300, 15),
        ]
        self.customers = []

    def add_customer(self, name, email):
        customer = Customer(name, email)
        self.customers.append(customer)
        print(f"Customer {name} added to the store.")

    def find_customer(self, email):
        for customer in self.customers:
            if customer.email == email:
                return customer
        return None

    def process_order(self, customer, product_name, quantity=1):
        product = next((p for p in self.products if p.name == product_name), None)
        if product:
            customer.add_to_cart(product, quantity)
        else:
            print(f"Product {product_name} not found.")

    def display_store_info(self):
        print("Welcome to Our Online Store!")
        print("Available Products:")
        for product in self.products:
            product.display_info()

# Function to simulate an online shopping experience
def shop_online():
    store = OnlineStore()
    store.display_store_info()

    store.add_customer("Alice", "alice@example.com")
    store.add_customer("Bob", "bob@example.com")

    alice = store.find_customer("alice@example.com")
    bob = store.find_customer("bob@example.com")

    store.process_order(alice, "Laptop", 2)
    store.process_order(bob, "Phone")
    store.process_order(bob, "Camera")

    alice.view_cart()
    bob.view_cart()

    order1 = Order(alice, alice.cart)
    order2 = Order(bob, bob.cart)

    order1.display_order()
    order2.display_order()

# if __name__ == "__main__":
#     shop_online()


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
