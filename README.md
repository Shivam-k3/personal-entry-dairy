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