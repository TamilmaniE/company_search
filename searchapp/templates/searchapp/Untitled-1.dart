
<style>
    body {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        background-color: #f7f7f7; /* Soft gray background */
    }
    .form-container {
        background-color: #fff;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        max-width: 500px;
        width: 100%;
        border: 1px solid #d92c27; /* Border color */
    }
    h1 {
        font-size: 1.8rem;
        margin-bottom: 20px;
        text-align: center;
        color: #d92c27; /* Heading color */
    }
    .btn-primary {
        width: 100%;
        margin-top: 15px;
        background-color: #d92c27; /* Button color */
        border-color: #a31f15; /* Button border color */
    }
    .btn-primary:hover {
        background-color: #a31f15; /* Darker hover effect */
        border-color: #a31f15;
    }
    .form-label {
        color: #d92c27; /* Line color for labels */
    }
</style>


function validateForm() {
    const email = document.getElementById("email").value;
    const phone = document.getElementById("phone").value;

    // Validate email format
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
        alert("Please enter a valid email address.");
        return false;
    }

    // Validate phone or landline number format
    const phonePattern = /^(\d{10}|(\d{3}[- ]?)?\d{7,10})$/;
    if (!phonePattern.test(phone)) {
        alert("Please enter a valid phone or landline number.");
        return false;
    }

    // All validations passed
    return true;
}


function validateEmail(email) {
    let re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function sendOtp() {
    sendEmailOtp();
    sendSMSOtp();
}

function sendSMSOtp(){
    let phone = document.getElementById('phone').value;
    otpTarget = phone;
    otpType = 'phone';

    fetch(`/send-sms-otp/?phone=${phone}`)
        .then(response => response.json())
        .catch(error => alert('Failed to send SMS OTP. Please try again.'));

}
function sendEmailOtp() {
    let email = document.getElementById('email').value;
    otpTarget = email;
    otpType = 'email';

    if (!validateEmail(email)) {
        alert('Invalid email format');
        return;
    }
    
    fetch(`/send-email-otp/?email=${email}`)
        .then(response => response.json())
        .catch(error => alert('Failed to send OTP. Please try again.'));
}