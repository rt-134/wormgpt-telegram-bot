# 🚀 رفع البوت - دليل سريع

## الخطوات السريعة (5 دقائق فقط!)

### 1️⃣ رفع على GitHub

```powershell
# في PowerShell
cd "C:\Users\user\Downloads\محاضرات"

# تهيئة Git
git init
git add .
git commit -m "WormGPT Bot - First Deploy"

# إنشاء repo جديد على GitHub ثم:
git remote add origin https://github.com/YOUR_USERNAME/wormgpt-bot.git
git branch -M main
git push -u origin main
```

### 2️⃣ Railway.app (الأسهل)

1. **افتح:** https://railway.app
2. **سجل دخول** بحساب GitHub
3. **اضغط:** "New Project" → "Deploy from GitHub repo"
4. **اختر:** repository "wormgpt-bot"
5. **انتظر** 2-3 دقائق ✅

**البوت يعمل الآن! 🎉**

---

### 3️⃣ Render.com (بديل ممتاز)

1. **افتح:** https://render.com
2. **سجل دخول** بحساب GitHub
3. **اضغط:** "New +" → "Background Worker"
4. **اختر:** repository "wormgpt-bot"
5. **اضبط:**
   - Name: `wormgpt-bot`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python WormGPT.py`
6. **اضغط:** "Create Background Worker"

**البوت يعمل! 🚀**

---

## ⚡ نصيحة مهمة

إذا كان التوكن مكشوف في الكود، استخدم متغيرات البيئة:

**في Railway/Render:**
- اذهب إلى Settings → Variables
- أضف: `BOT_TOKEN` = `8315094065:AAHYjZmj9ndfsOuxAQx9BsL8sNGvaoiIf5o`

**في الكود:**
```python
import os
VIPCODE3 = os.getenv('BOT_TOKEN', '8315094065:AAHYjZmj9ndfsOuxAQx9BsL8sNGvaoiIf5o')
```

---

## 📊 مراقبة البوت

- **Logs:** في لوحة التحكم Railway/Render
- **الحالة:** تحقق من `/start` في Telegram
- **الإحصائيات:** استخدم `/admin` في البوت

---

## 🆘 مشاكل شائعة

### البوت لا يرد:
```bash
# تحقق من Logs في السيرفر
# ابحث عن errors
```

### خطأ في requirements:
```bash
# أضف إلى requirements.txt:
certifi>=2023.7.22
```

### البوت يتوقف كل فترة:
- Railway: ترقية للـ Pro (محدود 500 ساعة/شهر)
- Render: مجاني إلى الأبد لكن يحتاج restart يدوي بعد 15 يوم

---

## ✅ تم بنجاح!

الآن بوتك يعمل 24/7 على السيرفر! 🎊

**رابط البوت:** https://t.me/YOUR_BOT_USERNAME
