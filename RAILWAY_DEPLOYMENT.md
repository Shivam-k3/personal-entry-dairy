# 🚀 Railway Deployment Guide

Deploy your Personal Daily Journal app to Railway in minutes!

## 🎯 Why Railway?

- ✅ **Free tier available** (no credit card required)
- ✅ **Easy deployment** from GitHub
- ✅ **Automatic HTTPS**
- ✅ **Custom domains**
- ✅ **Great for Python apps**

---

## 📋 Prerequisites

1. **GitHub account** with your journal app repository
2. **Railway account** (free at [railway.app](https://railway.app))

---

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Make sure your repository is on GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Verify these files exist in your repository:**
   - ✅ `app.py` (Flask backend)
   - ✅ `requirements.txt` (Python dependencies)
   - ✅ `Procfile` (tells Railway how to run the app)
   - ✅ `runtime.txt` (Python version)
   - ✅ `index.html` (frontend)

### Step 2: Deploy to Railway

1. **Go to [railway.app](https://railway.app)**
2. **Sign up/Login** with your GitHub account
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your journal app repository**
6. **Click "Deploy Now"**

### Step 3: Configure Your App

1. **Wait for deployment** (usually 2-3 minutes)
2. **Click on your project** in Railway dashboard
3. **Go to "Settings" tab**
4. **Copy your app URL** (something like `https://your-app-name.railway.app`)

### Step 4: Test Your Deployment

1. **Visit your app URL** in browser
2. **Test the journal functionality**
3. **Verify sentiment analysis works**
4. **Check that entries are saved**

---

## 🔧 Troubleshooting

### "Build Failed" Error
- Check that `requirements.txt` exists and is correct
- Verify Python version in `runtime.txt`
- Check Railway logs for specific errors

### "App Not Found" Error
- Make sure `Procfile` exists and contains: `web: python app.py`
- Verify `app.py` has the correct port configuration

### "Module Not Found" Error
- Railway will automatically install dependencies from `requirements.txt`
- Check that all required packages are listed

---

## 🌐 Custom Domain (Optional)

1. **Go to Railway dashboard**
2. **Click "Settings"**
3. **Scroll to "Domains" section**
4. **Add your custom domain**
5. **Update DNS records** as instructed

---

## 📊 Monitoring

Railway provides:
- **Real-time logs**
- **Performance metrics**
- **Error tracking**
- **Automatic restarts**

---

## 💰 Pricing

- **Free tier**: 500 hours/month
- **Pro plan**: $5/month for unlimited usage
- **Team plan**: $20/month for team features

---

## 🔄 Updates

To update your deployed app:
1. **Make changes to your code**
2. **Commit and push to GitHub**
3. **Railway automatically redeploys**

---

## 🎉 Success!

Your journal app is now live on the internet! Share the URL with friends and family.

**Example URL:** `https://your-journal-app.railway.app`

---

## 📞 Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **GitHub Issues**: Create an issue in your repository

---

**Your Personal Daily Journal with AI Sentiment Tracker is now live!** 🎉 