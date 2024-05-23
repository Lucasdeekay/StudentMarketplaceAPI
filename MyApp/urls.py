from django.urls import path

from MyApp import views
from MyApp.views import StudentProductListAPIView, StudentProductCreateAPIView, StudentProductDeleteAPIView, \
    SearchProductAPIView, ProductDetailPurchaseAPIView, DepositFundsAPIView, WithdrawFundsAPIView, \
    EmailSupportAPIView, CurrentUserView

urlpatterns = [
    path('login', views.login_user),
    path('register', views.register_user),
    path('logout', views.logout_user),
    path('forgot_password', views.forgot_password),
    path('retrieve_password', views.retrieve_password),
    path('dashboard/', CurrentUserView.as_view(), name='current_user'),
    path('products/', StudentProductListAPIView.as_view(), name='student_product_list'),
    path('products/create/', StudentProductCreateAPIView.as_view(), name='student_product_create'),
    path('products/<int:product_id>/delete/', StudentProductDeleteAPIView.as_view(), name='student_product_delete'),
    path('products/search/', SearchProductAPIView.as_view(), name='product_search'),
    path('products/details/purchase', ProductDetailPurchaseAPIView.as_view(), name='product_purchase'),
    path('wallet/deposit/', DepositFundsAPIView.as_view(), name='wallet_deposit'),
    path('wallet/withdraw/', WithdrawFundsAPIView.as_view(), name='wallet_withdraw'),
    path('support/email/', EmailSupportAPIView.as_view(), name='email_support'),
]
