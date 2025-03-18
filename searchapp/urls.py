from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    company_search_page, search_company, company_details,register_new_company,
    send_email_otp,send_sms_otp,verify_otp,
    verify_page,login_view, verified_user_page,
      dashboard_view,add_user,add_user_success,
      add_user_credentials,registered_users,
      verification_success,sidebar_view
    
    
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', company_search_page, name='company_search_page'),
    path('search/', search_company, name='search_company'),
    path('company/details/', company_details, name='company_details'),
    path('register/new/', register_new_company, name='register_new_company'),
    path('verify/', verify_page, name='verify_page'),
    path('send-email-otp/', send_email_otp, name='send_email_otp'),
    path('send-sms-otp/', send_sms_otp, name='send_sms_otp'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('eventAdmin/', login_view, name='login'),
    path('verified_users/', verified_user_page, name='verified_users'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('sidebar/', sidebar_view, name = 'sidebar'),
    path('add_user/', add_user, name='add_user'),
    path('add-user-credentials/', add_user_credentials, name='add_user_credentials'),
    path('add-user-success/', add_user_success, name='add_user_success'), 
    path('registered-users/', registered_users, name='registered_users'),
    path('verification-success/',verification_success, name='verification_success'),
]
