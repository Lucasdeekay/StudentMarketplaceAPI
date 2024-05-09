from django.contrib import admin
from .models import Student, Category, Product, Transaction, Wallet

# Register the Student model in the admin panel
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user','first_name', 'last_name', 'email', 'matric_number', 'phone_number', 'bio']  # Display these fields in the student list

# Register the Category model in the admin panel
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']  # Display the category name

# Register the Product model in the admin panel
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['seller', 'title', 'price', 'category', 'image']  # Display these fields in the product list
    readonly_fields = ['image']  # Make the image field read-only in the admin panel (security measure)

# Register the Transaction model in the admin panel
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'seller', 'product', 'quantity', 'total_amount', 'created_at']  # Display these fields in the transaction list

# Register the Wallet model in the admin panel
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['student', 'balance']  # Display the student and their wallet balance
