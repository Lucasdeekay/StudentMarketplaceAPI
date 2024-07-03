from rest_framework import serializers
from .models import Student, Product, Transaction, Wallet


# Serializer for the Student model
class StudentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)  # Use username instead of user object
    phone_number = serializers.CharField(required=False)  # Allow phone number to be optional
    bio = serializers.CharField(required=False)  # Allow bio to be optional

    class Meta:
        model = Student
        fields = '__all__'


# Serializer for the Product model, including nested category serializer
class ProductSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source='seller.user.username', read_only=True)  # Use seller username

    class Meta:
        model = Product
        fields = '__all__'


# Serializer for the Transaction model
class TransactionSerializer(serializers.ModelSerializer):
    buyer_username = serializers.CharField(source='buyer.user.username', read_only=True)  # Use buyer username
    seller_username = serializers.CharField(source='seller.user.username', read_only=True)  # Use seller username
    product_title = serializers.CharField(source='product.title', read_only=True)  # Use product title

    class Meta:
        model = Transaction
        fields = '__all__'


# Serializer for the Wallet model
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
