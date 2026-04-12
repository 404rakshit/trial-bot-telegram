# Frontend Setup - Quick Fix

## ✅ Issue Fixed!

The frontend was trying to call `undefined/api/otp/generate` because the API URL wasn't configured.

**Fixed by creating:** `frontend/.env` with `VITE_API_URL=http://localhost:8000`

---

## 🚀 How to Run Frontend

### Step 1: Install Dependencies (if not done)
```bash
cd frontend
npm install
```

### Step 2: Verify .env File
Check that `frontend/.env` exists and contains:
```
VITE_API_URL=http://localhost:8000
```
✅ Already created for you!

### Step 3: Start Development Server
```bash
npm run dev
```

Expected output:
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
```

### Step 4: Open Browser
Go to: http://localhost:5173

---

## ✅ What Should Work Now

1. **Click "Get Started"** button
2. **Should see:** 6-digit OTP code
3. **No errors** in browser console
4. **API call goes to:** `http://localhost:8000/api/otp/generate` ✅

---

## 🧪 Test It

### Option 1: Use the UI
1. Open http://localhost:5173
2. Click "Get Started"
3. Copy the OTP
4. Go to Telegram
5. Send `/link <otp>` to your bot

### Option 2: Test API Directly
```bash
# Make sure backend is running first!
curl http://localhost:8000/api/otp/generate \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-123"}'
```

---

## 🐛 Troubleshooting

### Still seeing "undefined" in URL?
**Solution:** Restart the frontend dev server
```bash
# Press Ctrl+C in the frontend terminal
# Then restart:
npm run dev
```

### CORS errors?
**Solution:** Make sure backend is running on port 8000
```bash
cd backend
venv\Scripts\activate
python main.py
```

### Connection refused?
**Check:**
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:5173
- ✅ No firewall blocking localhost

---

## 📁 Files Created

```
frontend/
├── .env              ← API URL configuration ✅
└── .env.example      ← Template for reference
```

---

## 🎯 Complete Setup (3 Terminals)

**Terminal 1 - Backend API:**
```bash
cd backend
venv\Scripts\activate
python main.py
```

**Terminal 2 - Telegram Bot:**
```bash
cd backend
venv\Scripts\activate
python bot_polling.py
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser! 🎉

---

## 📝 Environment Variables

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

### Backend (.env)
```env
TELEGRAM_BOT_TOKEN=your_token_here
OPENWEATHER_API_KEY=your_key_here
```

---

**Issue fixed! Restart your frontend dev server if it's already running.** 🚀
