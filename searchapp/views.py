from django.shortcuts import render, redirect
from pymongo import MongoClient
from django.http import JsonResponse
import random, time, requests
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from pymongo import MongoClient
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password, make_password
from django.views.decorators.csrf import csrf_exempt
import jwt
from django.core.paginator import Paginator

# MongoDB Connection
#client = MongoClient('mongodb://admin:pepdbinstance@52.66.91.85:27017/')

client = MongoClient('mongodb://localhost:27017/')
db = client['migration']
company_collection = db['company_data']
pep_company_info = db['pep_company_info']
login_credentials_collection = db['login_credentials'] 
registered_usersData = db['company_data']

# Generate JWT Token
def generate_jwt_token(user_data):
    payload = {
        'username': user_data['username'],
        'role': user_data['role'],
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token



# Login View
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if user exists in MongoDB
        user = login_credentials_collection.find_one({"username": username})

        if user and check_password(password, user['password']):  # Verify hashed password
            # Generate JWT token
            token = generate_jwt_token(user)
            response = redirect('dashboard')  # Redirect to the dashboard view
            response.set_cookie("jwt", token, httponly=True)
            return response
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'searchapp/login.html')


# Middleware for Role-Based Access
def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            token = request.COOKIES.get('jwt')
            if not token:
                return HttpResponseForbidden("Unauthorized")

            try:
                decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                role = decoded_token.get('role')
                if role not in allowed_roles:
                    return HttpResponseForbidden("You do not have permission to access this page.")
            except jwt.ExpiredSignatureError:
                return JsonResponse({"message": "Token has expired"}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({"message": "Invalid token"}, status=401)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Dashboard View
def dashboard_view(request):
    token = request.COOKIES.get('jwt')
    if not token:
        return redirect('login')

    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        role = decoded_token.get('role')
    except jwt.InvalidTokenError:
        return redirect('login')

    # Render the dashboard with a sidebar and role-specific links
    context = {
        "role": role,
    }
    return render(request, 'searchapp/dashboard.html', context)

# Registered Users View
# Role-Based Pages

@role_required(['superadmin','admin'])
def registered_users(request):
    try:
        # Fetch all data from the collection
        data = list(registered_usersData.find({}, {"_id": 0}))  # Exclude `_id` field
        
        # Handle missing fields in data
        for item in data:
            item['company_name'] = item.get('company_name')
            item['contact_fname'] = item.get('contact_fname', '')
            item['contact_lname'] = item.get('contact_lname', '')
            item['email'] = item.get('email', 'N/A')
            item['mobile'] = item.get('mobile', 'N/A')
            

        # Implement pagination
        page_number = request.GET.get('page', 1)
        paginator = Paginator(data, 10)  # 10 items per page

        try:
            page_obj = paginator.get_page(page_number)
        except Exception:
            page_obj = paginator.get_page(1)  # Default to page 1 if invalid page number

        # Pass data to the template
        return render(request, 'searchapp/registered_usersData.html', {"page_obj": page_obj})

    except Exception as e:
        messages.error(request, f"Error fetching data: {str(e)}")
        return redirect('dashboard')  # Redirect to dashboard on error


@role_required(['superadmin', 'admin'])
def verified_user_page(request):
    return render(request, 'searchapp/verified_user.html')

@role_required(['superadmin'])
def add_user(request):
    return render(request, 'searchapp/add_user.html')

def sidebar_view(request):
    return render(request, 'searchapp/sidebar.html')

def add_user_credentials(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']

        # Hash the password using Django's make_password function
        hashed_password = make_password(password)

        # MongoDB setup
        client = MongoClient('mongodb://localhost:27017/')
        db = client.migration
        collection = db.login_credentials

        # Insert user data into the collection
        collection.insert_one({
            "username": username,
            "password": hashed_password,
            "role": role
        })

        return redirect('add_user_success')  # Redirect to a success page

    return render(request, 'add_user.html')



def add_user_success(request):
    return render(request, 'searchapp/add_user_success.html')





# Search Company
def search_company(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'error': 'Query is required'}, status=400)

    results = pep_company_info.find({"company_name": {"$regex": query, "$options": "i"}})
    
    response = []
    for result in results:
        city = result.get('city_name', '')
        state = result.get('state_name', '')
        country = result.get('country_name', '')
        
        # Construct location based on available fields
        location_parts = [part for part in [city, state, country] if part]  # Filter out empty parts
        location = ', '.join(location_parts)

        response.append({
            'com_id': result.get('com_id', ''),
            'company_name': result.get('company_name', ''),
            'contact_person_name': result.get('firstname', '') + ' ' + result.get('lastname', ''),
            'email_id': result.get('email', ''),
            'phone_no': result.get('mobile', result.get('phone', '')),
            'location': location,
        })
    
    return JsonResponse(response, safe=False)

# Company Search Page

def company_search_page(request):
    return render(request, 'searchapp/company_search.html')

# Company Details View
def company_details(request):
    company_name = request.GET.get('company_name', '')

    # Fetch the company details
    results = pep_company_info.find_one({"company_name": company_name})

    if results:
        # Construct the location based on available fields
        city = results.get('city_name', '')
        state = results.get('state_name', '')
        country = results.get('country_name', '')

        location_parts = [part for part in [city, state, country] if part]  # Filter out empty parts
        location = ', '.join(location_parts)

        # Render form pre-filled with company data
        response = {
            'company_name': results.get('company_name', ''),
            'contact_fname': results.get('firstname', ''),
            'contact_lname': results.get('lastname', ''),
            'email': results.get('email', ''),
            'mobile': results.get('mobile', ''),
            'com_id': results.get('com_id', ''),
            'location': location,  # Use the constructed location
        }
    else:
        # Redirect to registration form with company_name pre-filled
        response = {'company_name': company_name}

    return render(request, 'searchapp/register_form.html', response)



# Register New Company View
def register_new_company(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        contact_fname = request.POST.get('contact_fname')
        contact_lname = request.POST.get('contact_lname')
        email = request.POST.get('email')
        phone = request.POST.get('mobile')
        com_id = request.POST.get('com_id')
        location = request.POST.get('location')
        

        # Validate required fields
        if not (company_name and contact_fname and email and phone):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Prepare company data
        company_data = {
            'com_id': com_id,
            'company_name': company_name,
            'contact_fname': contact_fname,
            'contact_lname': contact_lname,
            'email': email,
            'mobile': phone,
            'location': location,
            'email_verified': False,  
            'phn_verified': False 
            
        }

        # Check if the company already exists
        existing_company = company_collection.find_one({"company_name": company_name})
        if existing_company:
            # Update existing company record
            company_collection.update_one({"_id": existing_company['_id']}, {"$set": company_data})
        else:
            # Insert new company record
            company_collection.insert_one(company_data)

        # Redirect to a confirmation page
        return redirect(f'/verify/?email={email}&phone={phone}')

    return render(request, 'searchapp/register_form.html')

otp_storage = {}
otp_expiry = {}

# Verification Page

def verify_page(request):
    email = request.GET.get('email')
    phone = request.GET.get('phone')
    return render(request, 'searchapp/verify.html', {'email': email, 'phone': phone})

# Generate and Send Email OTP

def send_email_otp(request):
    email = request.GET.get('email')
    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)

    otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
    otp_storage[email] = otp
    otp_expiry[email] = time.time() + 180  # OTP valid for 180 seconds

    # Query user's name from the database (if available)
    user_details = None
    try:
        user_details = company_collection.find_one({"email": email})  # Replace with your MongoDB collection
    except Exception as e:
        return JsonResponse({'error': 'Error fetching user details'}, status=500)

    contact_fname = user_details.get("contact_fname", "Customer") if user_details else "Customer"

    # HTML Email Content
    subject = "Welcome to Pepagora! Here's Your OTP"
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #d92c27; padding: 20px; border-radius: 8px;">
            <h2 style="text-align: center; color: #d92c27;">Welcome to Pepagora!</h2>
            <p>Dear {contact_fname},</p>
            <p>We’re thrilled to have you on board and can’t wait for you to explore everything we have to offer.</p>
            <p>To get started, please use the following One-Time Password (OTP) to verify your account:</p>
            <div style="text-align: center; margin: 20px 0;">
                <span style="display: inline-block; padding: 10px 20px; font-size: 24px; font-weight: bold; color: #d92c27; border: 2px solid #d92c27; border-radius: 4px;">{otp}</span>
            </div>
            <p>If you didn’t request this OTP, please ignore this email.</p>
            <p>Best Regards,</p>
            <p><strong>The Pepagora Team</strong></p>
            <p style="text-align: center;">
                <a href="https://www.pepagora.com" style="background-color: #d92c27; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 4px; border: 2px solid #a31f15; font-weight: bold;">Visit Our Website</a>
            </p>
        </div>
    </body>
    </html>
    """

    # Send Email
    email_message = EmailMessage(
        subject,
        html_message,
        settings.EMAIL_HOST_USER,
        [email],
    )
    email_message.content_subtype = "html"  # Set content type to HTML
    email_message.send(fail_silently=False)

    return JsonResponse({'message': 'OTP sent to email'})


# Verify OTP

from django.core.mail import send_mail, EmailMessage
from django.http import JsonResponse
from django.conf import settings
import time

def verify_otp(request):
    otp = request.GET.get('otp')
    email = request.GET.get('email')
    phone = request.GET.get('phone')

    if not otp:
        return JsonResponse({'error': 'OTP is required'}, status=400)

    current_time = time.time()

    # Email OTP Verification
    if email in otp_storage and otp_storage[email] == int(otp) and current_time < otp_expiry[email]:
        # Query user's details from the database
        user_details = None
        try:
            user_details = company_collection.find_one({"email": email})
        except Exception as e:
            return JsonResponse({'error': 'Error fetching user details'}, status=500)

        if user_details:
            contact_fname = user_details.get("contact_fname", "Customer")  # Fallback to "Customer" if name is missing
            
            # Update email_verified to True
            company_collection.update_one(
                {"email": email},
                {"$set": {"email_verified": True}}
            )
        else:
            contact_fname = "Customer"

        # Clean up OTP storage and expiry
        del otp_storage[email]
        del otp_expiry[email]

        # Sending personalized HTML welcome email
        subject = 'Email Successfully Verified – Thank You for Registering with Us!'
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #d92c27; padding: 20px; border-radius: 8px;">
                <h2 style="text-align: center; color: #d92c27;">Welcome to Pepagora!</h2>
                <p>Dear {contact_fname},</p>
                <p>Congratulations! Your account has been successfully verified. 🎉</p>
                <p>We’re thrilled to have you on board. Here's what you can expect as part of your journey with us:</p>
                
                <p>If you have any questions or need assistance, don’t hesitate to reach out. We’re just an email away!</p>
                <p>Thanks,</p>
                <p><strong>The Pepagora Team</strong></p>
                <p style="text-align: center;">
                    <a href="https://www.pepagora.com" style="background-color: #d92c27; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 4px; border: 2px solid #a31f15; font-weight: bold;">Visit Our Website</a>
                </p>
            </div>
        </body>
        </html>
        """

        email = EmailMessage(
            subject,
            html_message,
            settings.EMAIL_HOST_USER,
            [email],
        )
        email.content_subtype = "html"  # Set content type to HTML
        email.send(fail_silently=False)

        return JsonResponse({'message': 'Email verified successfully'})

    # Phone OTP Verification
    elif phone in otp_storage and otp_storage[phone] == int(otp) and current_time < otp_expiry[phone]:
        # Update phn_verified to True
        company_collection.update_one(
            {"mobile": phone},
            {"$set": {"phn_verified": True}}
        )

        # Clean up OTP storage and expiry
        del otp_storage[phone]
        del otp_expiry[phone]

        return JsonResponse({'message': 'Phone number verified successfully'})

    else:
        return JsonResponse({'error': 'Invalid or expired OTP'}, status=400)






import http.client
import json
import random
import time
from django.http import JsonResponse

# Storage for OTP and expiry time
otp_storage = {}
otp_expiry = {}

def send_sms_otp(request):
    phone = request.GET.get('phone')
    if not phone:
        return JsonResponse({'error': 'Phone number is required'}, status=400)

    # Generate a random 6-digit OTP
    otp = random.randint(100000, 999999)
    otp_storage[phone] = otp
    otp_expiry[phone] = time.time() + 180  # OTP valid for 180 seconds

    # Prepare the payload
    payload = json.dumps({
        "template_id": "67909774d6fc055e1b0af562",
        "short_url": "1",  # Optional, set as per your requirement
        "recipients": [
            {
                "mobiles": f"91{phone}",
                "var1": f"{otp}"
            }
        ]
    })

    headers = {
        'authkey': "439305Ai4NgdjEJ67909a90P1",
        'accept': "application/json",
        'content-type': "application/json"
    }

    # Send SMS using MSG91 API
    try:
        conn = http.client.HTTPSConnection("control.msg91.com")
        conn.request("POST", "/api/v5/flow", payload, headers)
        res = conn.getresponse()
        data = res.read()

        # Parse the response
        response_data = json.loads(data.decode("utf-8"))
        if res.status == 200 and response_data.get("type") == "success":
            return JsonResponse({'message': 'OTP sent to phone number'})
        else:
            return JsonResponse({'error': 'Failed to send SMS OTP', 'details': response_data}, status=500)

    except Exception as e:
        print(f"Exception while sending SMS: {e}")
        return JsonResponse({'error': 'Failed to send SMS OTP'}, status=500)


def verification_success(request):
    return render(request, 'searchapp/verification_success.html')