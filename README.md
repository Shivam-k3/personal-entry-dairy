# 📖 Personal Daily Journal with Sentiment Tracker

A beautiful web application that helps you track your daily mood and journal entries with AI-powered sentiment analysis.

## ✨ Features

- **📝 Daily Journal Entries**: Write about your day, thoughts, and feelings
- **🧠 AI Sentiment Analysis**: Automatically analyzes your mood (Positive, Negative, Neutral, Crisis)
- **💡 Personalized Suggestions**: Get helpful suggestions based on your mood
- **📈 Mood Trend Chart**: Visualize your mood over time
- **💾 Persistent Storage**: Your entries are saved locally
- **🎨 Beautiful UI**: Modern, responsive design with Tailwind CSS
- **📱 Mobile Friendly**: Works great on all devices
- **🚨 Crisis Support**: Special detection and resources for serious negative thoughts

## 🚀 Quick Start (Choose One Method)

### Method 1: One-Click Startup (Recommended)

1. **Double-click `start_journal.bat`** in the `journal_app` folder
2. **Or double-click `start_journal.ps1`** (PowerShell version)
3. The app will automatically:
   - Check if Python is installed
   - Install dependencies if needed
   - Download TextBlob data if needed
   - Start the server
4. **Open your browser** and go to `http://localhost:5000`

### Method 2: Desktop Shortcut

1. **Run `create_shortcut.bat`** once to create a desktop shortcut
2. **Double-click "Journal App"** on your desktop anytime
3. The app will start automatically

### Method 3: Manual Setup (Original Method)

1. **Install Python dependencies:**
   ```bash
   cd journal_app
   pip install -r requirements.txt
   ```

2. **Download TextBlob data:**
   ```bash
   python -m textblob.download_corpora
   ```

3. **Start the backend server:**
   ```bash
   python app.py
   ```

4. **Open the app:**
   - Go to `http://localhost:5000` in your browser
   - Or open `index.html` directly

## 📁 Project Structure

```
journal_app/
├── index.html              # Frontend (beautiful UI)
├── app.py                 # Backend (Flask API)
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── start_journal.bat     # Windows batch launcher
├── start_journal.ps1     # PowerShell launcher
├── create_shortcut.bat   # Desktop shortcut creator
└── journal_entries.json  # Your saved entries (created automatically)
```

## 🎯 How to Use

1. **Write an Entry**: Type about your day in the text area
2. **Click "Add Entry"**: Your entry will be analyzed for mood
3. **View Results**: See your mood analysis and personalized suggestion
4. **Track Trends**: Check the mood chart to see patterns over time
5. **Review History**: Browse your previous entries

## 🔧 API Endpoints

If you're running the backend, these endpoints are available:

- `POST /api/journal` - Add a new journal entry
- `GET /api/journal` - Get all entries (or last 7 with `?limit=7`)
- `DELETE /api/journal/<id>` - Delete a specific entry
- `GET /api/stats` - Get journal statistics

## 🎨 Customization

### Adding More Positive/Negative Words

Edit the `analyze_sentiment` function in `app.py` to add more keywords for better sentiment analysis.

### Changing Suggestions

Modify the `get_suggestion` function in `app.py` to customize the suggestions based on mood.

### Styling

The app uses Tailwind CSS. You can modify the classes in `index.html` to change the appearance.

## 🛠️ Troubleshooting

### "Page is black/not loading"
- Make sure you're opening the correct `index.html` file
- Check your internet connection (needed for Tailwind CSS)
- Try a different browser

### Backend errors
- Make sure Python is installed
- Use the `start_journal.bat` file for automatic setup
- Check if the server is running on port 5000

### "Module not found" errors
- Use the `start_journal.bat` file for automatic dependency installation
- Make sure you're in the correct directory

### PowerShell execution policy error
- Right-click `start_journal.ps1` and select "Run with PowerShell"
- Or run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## 📊 Data Storage

- **Frontend only**: Entries are stored in your browser's localStorage
- **With backend**: Entries are saved to `journal_entries.json` file

## 🔒 Privacy

Your journal entries are stored locally on your computer. They are not sent to any external servers (unless you're using the backend, which stores them in a local file).

## 🚨 Crisis Support

If the app detects serious negative thoughts, it will:
- Mark the entry as "Crisis"
- Provide immediate crisis resources
- Show emergency contact information

**If you're having thoughts of self-harm:**
- **Call 988** (Suicide & Crisis Lifeline) - Available 24/7
- **Text HOME to 741741** (Crisis Text Line)
- **Call 911** if you're in immediate danger

## 🎉 Enjoy Your Journal!

Start writing and discover patterns in your mood and thoughts. This app is designed to help you reflect, track your emotional well-being, and gain insights into your daily life.

---

**Made with ❤️ for personal growth and self-reflection**

## 🆕 Multi-Device Support

**Problem Solved**: Previously, all devices shared the same journal entries because they all connected to the same server and used the same storage file.

**Solution**: Each device now has its own separate journal storage with automatic device identification.

### How It Works

1. **Automatic Device ID**: When you first visit the app, a unique device ID is generated and stored in your browser's localStorage
2. **Separate Storage**: Each device's entries are stored in separate files (`journal_data/journal_[device_id].json`)
3. **No Cross-Device Sharing**: Entries from one device won't appear on another device
4. **Device Reset**: You can reset your device ID to start fresh (this will create a new separate storage)

### Features

- ✍️ **Daily Journal Entries**: Write about your day, thoughts, and feelings
- 🧠 **Sentiment Analysis**: Automatic mood detection (Positive, Negative, Neutral, Crisis)
- 💡 **Personalized Suggestions**: Get helpful suggestions based on your mood
- 📊 **Mood Tracking**: Visual charts showing your mood trends over time
- 📱 **Multi-Device Support**: Each device has its own private journal
- 🔄 **Device Reset**: Start fresh with a new device ID when needed

### API Endpoints

- `POST /api/journal` - Add a new journal entry
- `GET /api/journal` - Get all entries for your device
- `DELETE /api/journal/<id>` - Delete a specific entry
- `GET /api/stats` - Get mood statistics for your device
- `GET /api/user-info` - Get device information

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open http://localhost:5000 in your browser

### File Structure

```
journal_app/
├── app.py                 # Main Flask application
├── index.html            # Frontend interface
├── journal_data/         # Directory for device-specific journal files
│   ├── journal_[device1].json
│   ├── journal_[device2].json
│   └── ...
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### Technical Details

- **Device Identification**: Uses browser localStorage to maintain device ID across sessions
- **Storage**: Each device gets its own JSON file in the `journal_data/` directory
- **Fallback**: If no device ID is provided, generates one based on IP and user agent
- **Privacy**: No data sharing between devices unless explicitly configured

### Troubleshooting

**Q: I'm still seeing entries from other devices**
A: Make sure you're using the updated version. Clear your browser cache and reload the page.

**Q: I want to share entries between devices**
A: Currently, each device has separate storage. For sharing, you'd need to implement user accounts and cloud storage.

**Q: I lost my entries after clearing browser data**
A: The device ID is stored in localStorage. If you clear browser data, you'll get a new device ID and start fresh. Use the "Reset" button to manually reset your device ID.

## 🔐 Email Authentication System

**Problem Solved**: Users can now register with email verification and reset passwords securely via email.

**Solution**: Complete email authentication system with verification, password reset, and secure token management.

### Email Authentication Features

- ✉️ **Email Verification**: Users must verify their email before logging in
- 🔑 **Password Reset**: Secure password reset via email links
- 🔄 **Resend Verification**: Users can request new verification emails
- ⏰ **Token Expiration**: Security tokens expire automatically (24h for verification, 1h for reset)
- 🛡️ **Secure Tokens**: Cryptographically secure verification tokens

### How Email Authentication Works

1. **Registration**: User registers with username, email, and password
2. **Verification Email**: System sends verification email with secure token
3. **Email Verification**: User clicks link to verify email address
4. **Login Access**: Only verified users can log in to the journal
5. **Password Reset**: Users can request password reset via email
6. **Secure Reset**: Password reset uses time-limited secure tokens

### Setup Email Authentication

1. **Configure Email Settings**:
   ```bash
   # Edit email_config.py with your email credentials
   EMAIL_CONFIG = {
       'smtp_server': 'smtp.gmail.com',
       'smtp_port': 587,
       'sender_email': 'your-email@gmail.com',
       'sender_password': 'your-app-password',
       'app_name': 'Personal Daily Journal'
   }
   ```

2. **For Gmail Users**:
   - Enable 2-factor authentication on your Gmail account
   - Go to Google Account settings > Security > App passwords
   - Generate an app password for "Mail"
   - Use the 16-character app password (not your regular password)

3. **For Other Email Providers**:
   - See `email_config.py` for Outlook and Yahoo configurations
   - Update SMTP settings according to your provider

### Features

- 🔐 **User Authentication**: Register, login, logout, and password management
- ✉️ **Email Verification**: Secure email verification system
- 🔑 **Password Reset**: Forgot password functionality via email
- ✍️ **Daily Journal Entries**: Write about your day, thoughts, and feelings
- 🧠 **Sentiment Analysis**: Automatic mood detection (Positive, Negative, Neutral, Crisis)
- 💡 **Personalized Suggestions**: Get helpful suggestions based on your mood
- 📊 **Mood Tracking**: Visual charts showing your mood trends over time
- 📱 **Cross-Device Access**: Access your journal from any device by logging in
- 🔒 **Secure Storage**: Each user's data is completely separate and secure

### API Endpoints

#### Authentication Endpoints
- `POST /api/auth/register` - Register a new user account (requires email verification)
- `POST /api/auth/login` - Login with existing credentials (requires verified email)
- `POST /api/auth/logout` - Logout current user
- `GET /api/auth/status` - Check authentication status
- `POST /api/auth/change-password` - Change user password (requires authentication)
- `GET /api/auth/verify-email` - Verify email address using token
- `POST /api/auth/forgot-password` - Send password reset email
- `POST /api/auth/reset-password` - Reset password using token
- `POST /api/auth/resend-verification` - Resend email verification

#### Journal Endpoints (Require Authentication)
- `POST /api/journal` - Add a new journal entry
- `GET /api/journal` - Get all entries for the logged-in user
- `DELETE /api/journal/<id>` - Delete a specific entry
- `GET /api/stats` - Get mood statistics for the logged-in user
- `GET /api/user-info` - Get user information and entry summary

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure email settings:
```bash
# Edit email_config.py with your email credentials
# See setup instructions above
```

3. Run the application:
```bash
python app.py
```

4. Open http://localhost:5000 in your browser

### File Structure

```
journal_app/
├── app.py                 # Main Flask application
├── index.html            # Frontend interface with email auth
├── reset-password.html   # Password reset page
├── email_config.py       # Email configuration file
├── journal_data/         # Directory for user-specific journal files
│   ├── journal_user_[username1].json
│   ├── journal_user_[username2].json
│   └── ...
├── users.json            # User accounts and authentication data
├── verification_tokens.json # Email verification and reset tokens
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### Security Features

- **Password Hashing**: Passwords are hashed using SHA-256 with salt
- **Session Security**: Secure session management with random secret keys
- **Input Validation**: Username, email, and password validation
- **CORS Support**: Cross-origin requests with credentials support
- **Authentication Required**: All journal endpoints require user authentication
- **Email Verification**: Users must verify email before accessing journal
- **Secure Tokens**: Time-limited, cryptographically secure verification tokens
- **Token Expiration**: Automatic cleanup of expired tokens

### User Experience

1. **First Visit**: Users see a login/register page
2. **Registration**: New users create accounts with email verification
3. **Email Verification**: Users receive and click verification email
4. **Login**: Verified users can log in to access their journal
5. **Journal Access**: Users can add entries and view their history
6. **Password Reset**: Users can reset passwords via email if forgotten
7. **Cross-Device**: Users can log in from any device to access their journal
8. **Logout**: Users can log out to secure their account

### Technical Details

- **Backend**: Flask with session-based authentication and email integration
- **Frontend**: HTML/CSS/JavaScript with modern UI and form validation
- **Storage**: JSON files for users, journal entries, and verification tokens
- **Security**: Password hashing, session management, input validation, secure tokens
- **Email**: SMTP integration with support for Gmail, Outlook, and Yahoo
- **CORS**: Configured for cross-origin requests with credentials

### Troubleshooting

**Q: Email verification isn't working**
A: Check your email configuration in `email_config.py`. For Gmail, make sure you're using an app password, not your regular password.

**Q: I can't log in after registering**
A: You need to verify your email first. Check your email for the verification link, or use the "Resend verification" option.

**Q: Password reset email not received**
A: Check your spam folder and verify your email configuration. Make sure the email address is correct.

**Q: I forgot my password**
A: Use the "Forgot your password?" link on the login page to receive a reset email.

**Q: Is my data secure?**
A: Yes! Passwords are hashed with salt, sessions are secure, verification tokens are time-limited, and each user's data is completely separate.

**Q: Can I use a different email provider?**
A: Yes! See `email_config.py` for configurations for Gmail, Outlook, and Yahoo. You can adapt it for other providers.

### Future Enhancements

- Email templates customization
- Two-factor authentication (2FA)
- Social login integration
- Journal entry sharing
- Data export/import
- Advanced mood analytics
- Reminder notifications
- Email preferences management 