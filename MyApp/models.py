from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator

# This model extends the default Django User model to create a Student profile
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)  # OneToOne relation with default Django User model
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    matric_no = models.CharField(max_length=12)
    phone_number = models.CharField(max_length=20, blank=True)  # Optional phone number field
    bio = models.TextField(blank=True)  # Optional bio field

    def __str__(self):
        return self.user.username


# This model represents a product listing within the marketplace
class Product(models.Model):
    seller = models.ForeignKey(Student, on_delete=models.CASCADE)  # Seller linked to Student model
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField()
    available_quantity = models.IntegerField()
    image = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return self.title

# This model tracks transactions occurring within the marketplace
class Transaction(models.Model):
    buyer = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='buyer_transactions')  # Buyer linked to Student model
    seller = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='seller_transactions')  # Seller linked to Student model
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction #{self.id} - {self.product.title} (Buyer: {self.buyer.user.username}, Seller: {self.seller.user.username})"

# This model represents a student's wallet for managing their funds within the marketplace
class Wallet(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)  # OneToOne relation with Student model
    balance = models.FloatField(default=0)

    def __str__(self):
        return f"Wallet for {self.student.user.username} (Balance: ${self.balance})"

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.save()
        else:
            raise ValueError("Deposit amount must be positive.")

    def withdraw(self, amount):
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
            self.save()
        else:
            raise ValueError("Withdrawal amount must be positive and cannot exceed current balance.")

    def make_payment(self, transaction):
        if self.balance >= transaction.total_amount:
            self.balance -= transaction.total_amount
            self.save()
        else:
            raise ValueError("Insufficient funds for transaction.")
