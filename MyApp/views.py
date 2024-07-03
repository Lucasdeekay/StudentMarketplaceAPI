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

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
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
                    student = Student.objects.get(user=user)
                    student_serializer = StudentSerializer(student)
                    return JsonResponse({'success': 'Login successful', 'student': student_serializer.data}, status=200)
                else:
                    return JsonResponse({'error': 'Invalid credentials'}, status=401)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            first_name = data.get('first_name').strip()
            last_name = data.get('last_name').strip()
            email = data.get('email').strip()
            matric_number = data.get('matric_number').strip()
            phone_number = data.get('phone_number').strip()
            bio = data.get('bio').strip()
            password = data.get('password').strip()
            if User.objects.filter(**{"username": matric_number, "email": email}).exists():
                return JsonResponse({'error': "User already exists"}, status=400)
            else:
                user = User.objects.create_user(username=matric_number, password=password, email=email)
                student = Student.objects.create(user=user, first_name=first_name, last_name=last_name, email=email, matric_no=matric_number, phone_number=phone_number, bio=bio)
                Wallet.objects.create(student=student)
                return JsonResponse({'success': "Registration successful"}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
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

@csrf_exempt
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
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        user = User.objects.get(id=int(user_id))
        student = Student.objects.get(user=user)  # Get the student profile linked to the user
        wallet = Wallet.objects.get(student=student)  # Get the wallet associated with the student
        student_serializer = StudentSerializer(student)
        wallet_serializer = WalletSerializer(wallet)
        return JsonResponse({'student': student_serializer.data, 'wallet': wallet_serializer.data}, status=status.HTTP_200_OK)


class StudentProductListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        user = User.objects.get(id=int(user_id))
        student = Student.objects.get(user=user)
        if Product.objects.filter(seller=student).exists():
            products = Product.objects.filter(seller=student)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)


class StudentProductCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        user_id = data.get('user_id').strip()
        title = data.get('title').strip()
        description = data.get('description').strip()
        price = data.get('price').strip()
        available_quantity = data.get('available_quantity').strip()
        image = data.get('image').strip()

        user = User.objects.get(id=int(user_id))
        student = Student.objects.get(user=user)

        if available_quantity == '0':
            available_quantity = '1000000000'

        if not Product.objects.filter(**{"title": title, "seller": student}).exists():
            Product.objects.create(seller=student, title=title, description=description, price=price, available_quantity=available_quantity, image=image)
            return Response(status=status.HTTP_201_CREATED)
        return Response({'error': 'Product already created by user'}, status=status.HTTP_400_BAD_REQUEST)


class StudentProductDeleteAPIView(APIView):
    def delete(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
            student = product.seller
            product.delete()

            student_serializer = StudentSerializer(student)
            
            return Response({'success': 'Product successfully deleted.', 'student': student_serializer.data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)


class SearchProductAPIView(APIView):
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
    def post(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        user = User.objects.get(id=int(user_id))
        student = Student.objects.get(user=user)
        try:
            product_id = request.data.get('product_id')
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
    def post(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        user = User.objects.get(id=int(user_id))
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
    def post(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        user = User.objects.get(id=int(user_id))
        student = Student.objects.get(user=user)
        try:
            amount = float(request.data.get('amount'))
            if amount <= 0:
                return Response({'error': 'Withdrawal amount must be positive.'}, status=status.HTTP_400_BAD_REQUEST)
            student.wallet.withdraw(amount)
            return Response({'message': 'Withdrawal successful.'}, status=status.HTTP_200_OK)
        except ValueError:
            return Response({'error': 'Invalid withdrawal amount or insufficient funds.'}, status=status.HTTP_400_BAD_REQUEST)


class EmailSupportAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        user = User.objects.get(id=int(user_id))
        student = Student.objects.get(user=user)
        subject = request.data.get('subject')
        message = request.data.get('content')

        if not subject or not message:
            return Response({'error': 'Subject and message are required.'}, status=status.HTTP_400_BAD_REQUEST)

        email_from = 'lucasdeekay98@gmail.com'
        recipient_list = ['lucasdeekay98@gmail.com']
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)

        return Response({'message': 'Email sent successfully.'}, status=status.HTTP_200_OK)
