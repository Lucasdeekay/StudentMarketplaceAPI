# views.py
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from MyApp.models import Student, Wallet, Product, Transaction
from MyApp.serializers import StudentSerializer, WalletSerializer, ProductSerializer


def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            password = data.get('password')

            if User.objects.filter(**{"email": email}).exists():
                username = User.objects.get(email=email).username
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return JsonResponse({'success': 'Login successful', 'username': user.username}, status=200)
                else:
                    return JsonResponse({'error': 'Invalid credentials'}, status=401)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username').strip()
            first_name = data.get('first_name').strip()
            last_name = data.get('last_name').strip()
            email = data.get('email').strip()
            matric_number = data.get('matric_number').strip()
            phone_number = data.get('phone_number').strip()
            bio = data.get('bio').strip()
            password = data.get('password').strip()
            if User.objects.filter(**{"username": username, "email": email}).exists():
                return JsonResponse({'error': "User already exists"}, status=400)
            else:
                user = User.objects.create_user(username=username, password=password, email=email)
                Student.object.create(user=user, first_name=first_name, last_name=last_name, email=email, matric_number=matric_number, phone_number=phone_number, bio=bio)
                return JsonResponse({'success': "Registration successful"}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def forgot_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email').strip()

            if User.objects.filter(**{"email": email}).exists():
                user = User.objects.get(email=email)
                data = {
                    'user_id': user.id,
                    'success': "Proceed to change password",
                }
                return JsonResponse(data, status=200)
            else:
                data = {
                    'error': "User does not exist",
                }
                # Redirect to dashboard page
                return JsonResponse(data, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def retrieve_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_id = data.get('user_id').strip()
            user = User.objects.get(id=int(user_id))
            password = data.get('password').strip()
            user.set_password(password)
            user.save()
            data = {
                'success': "Password change successful",
            }
            # Redirect to dashboard page
            return JsonResponse(data, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def logout_user(request):
    # logout user
    logout(request)
    # redirect to login page
    return JsonResponse({}, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]  # Only allow authenticated users

    def get(self, request):
        user = request.user  # Access the authenticated user from the request
        student = Student.objects.get(user=user)  # Get the student profile linked to the user
        wallet = Wallet.objects.get(student=student)  # Get the wallet associated with the student
        student_serializer = StudentSerializer(student)
        wallet_serializer = WalletSerializer(wallet)
        return Response({'user': student_serializer.data, 'wallet': wallet_serializer.data})


class StudentProductListAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only allow authenticated users

    def get(self, request):
        user = request.user
        student = Student.objects.get(user=user)
        products = Product.objects.filter(seller=student)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class StudentProductCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only allow authenticated users

    def post(self, request):
        user = request.user
        student = Student.objects.get(user=user)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=student)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentProductDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only allow authenticated users

    def get(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
            user = request.user
            student = Student.objects.get(user=user)
            if product.seller != student:
                return Response({'error': 'You can only view your own products.'}, status=status.HTTP_403_FORBIDDEN)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
            user = request.user
            student = Student.objects.get(user=user)
            if product.seller != student:
                return Response({'error': 'You can only delete your own products.'}, status=status.HTTP_403_FORBIDDEN)
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)


class SearchProductAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Optional, consider permission approach
    filter_backends = [SearchFilter]  # Enable search filter
    search_fields = ['title', 'description']  # Search by title and description

    def get(self, request):
        queryset = Product.objects.all()
        search_term = request.query_params.get('search', None)  # Get search term from query parameter
        if search_term:
            queryset = queryset.filter(title__icontains=search_term) | queryset.filter(description__icontains=search_term)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)


class ProductDetailPurchaseAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only allow authenticated users

    def get(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, product_id):
        user = request.user
        student = Student.objects.get(user=user)
        try:
            product = Product.objects.get(pk=product_id)
            if product.seller == student:
                return Response({'error': 'You cannot purchase your own product.'}, status=status.HTTP_400_BAD_REQUEST)
            quantity = request.data.get('quantity')
            if not quantity or quantity <= 0:
                return Response({'error': 'Invalid purchase quantity.'}, status=status.HTTP_400_BAD_REQUEST)
            if quantity > product.available_quantity:  # Assuming an 'available_quantity' field exists
                return Response({'error': 'Insufficient product quantity available.'}, status=status.HTTP_400_BAD_REQUEST)
            total_amount = quantity * product.price
            if student.wallet.balance < total_amount:
                return Response({'error': 'Insufficient funds in your wallet.'}, status=status.HTTP_400_BAD_REQUEST)
            # Transaction creation and wallet updates
            transaction = Transaction.objects.create(
                buyer=student, seller=product.seller, product=product, quantity=quantity, total_amount=total_amount
            )
            transaction.save()
            product.available_quantity -= quantity  # Update product quantity
            product.save()
            student.wallet.balance -= total_amount  # Deduct amount from buyer's wallet
            student.wallet.save()
            seller = product.seller
            seller.wallet.balance += total_amount  # Add amount to seller's wallet
            seller.wallet.save()
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)


class DepositFundsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        student = Student.objects.get(user=user)
        try:
            amount = float(request.data.get('amount'))
            if amount <= 0:
                return Response({'error': 'Deposit amount must be positive.'}, status=status.HTTP_400_BAD_REQUEST)
            student.wallet.deposit(amount)
            return Response({'message': 'Deposit successful.'}, status=status.HTTP_201_CREATED)
        except ValueError:
            return Response({'error': 'Invalid deposit amount.'}, status=status.HTTP_400_BAD_REQUEST)

class WithdrawFundsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        student = Student.objects.get(user=user)
        try:
            amount = float(request.data.get('amount'))
            if amount <= 0:
                return Response({'error': 'Withdrawal amount must be positive.'}, status=status.HTTP_400_BAD_REQUEST)
            student.wallet.withdraw(amount)
            return Response({'message': 'Withdrawal successful.'}, status=status.HTTP_200_OK)
        except ValueError:
            return Response({'error': 'Invalid withdrawal amount or insufficient funds.'}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password1 = request.data.get('new_password1')
        new_password2 = request.data.get('new_password2')

        if not old_password or not new_password1 or not new_password2:
            return Response({'error': 'All password fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password1 != new_password2:
            return Response({'error': 'New passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password1)
        user.save()
        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)

class EmailSupportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        subject = request.data.get('subject')
        message = request.data.get('message')

        if not subject or not message:
            return Response({'error': 'Subject and message are required.'}, status=status.HTTP_400_BAD_REQUEST)

        email_from = user.email
        recipient_list = ['support@yourapp.com']  # Replace with your support email
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)

        return Response({'message': 'Email sent successfully.'}, status=status.HTTP_200_OK)
