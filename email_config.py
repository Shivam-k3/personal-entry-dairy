# Email Configuration for Personal Daily Journal
# 
# To use email authentication, you need to:
# 1. Update the EMAIL_CONFIG below with your email credentials
# 2. For Gmail, you'll need to create an "App Password" (not your regular password)
# 3. Enable 2-factor authentication on your Gmail account first
# 4. Go to Google Account settings > Security > App passwords
# 5. Generate an app password for "Mail" and use it below

EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',  # For Gmail
    'smtp_port': 587,                 # TLS port for Gmail
    'sender_email': 'dreamerclothing001@gmail.com',      # Developer Gmail address
    'sender_password': 'YOUR_APP_PASSWORD',              # Gmail App Password (not your normal password!)
    'app_name': 'Personal Daily Journal'
}

# Alternative configurations for other email providers:

# For Outlook/Hotmail:
# EMAIL_CONFIG = {
#     'smtp_server': 'smtp-mail.outlook.com',
#     'smtp_port': 587,
#     'sender_email': 'your-email@outlook.com',
#     'sender_password': 'your-password',
#     'app_name': 'Personal Daily Journal'
# }

# For Yahoo:
# EMAIL_CONFIG = {
#     'smtp_server': 'smtp.mail.yahoo.com',
#     'smtp_port': 587,
#     'sender_email': 'your-email@yahoo.com',
#     'sender_password': 'your-app-password',
#     'app_name': 'Personal Daily Journal'
# }

# Instructions for Gmail App Password:
# 1. Go to your Google Account settings: https://myaccount.google.com/
# 2. Click on "Security" in the left sidebar
# 3. Under "Signing in to Google," click on "2-Step Verification"
# 4. At the bottom, click on "App passwords"
# 5. Select "Mail" as the app and "Other" as the device
# 6. Click "Generate"
# 7. Copy the 16-character password and use it in the EMAIL_CONFIG above 