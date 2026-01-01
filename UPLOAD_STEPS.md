# 🚀 خطوات رفع البوت - بدون Git

## ✅ الملفات الجاهزة:
- WormGPT.py
- requirements.txt
- Procfile
- runtime.txt

---

## 🎯 الطريقة الأسهل: Render.com (بدون Git)

### الخطوة 1: إنشاء حساب GitHub
1. اذهب إلى: https://github.com/signup
2. سجل حساب جديد (مجاني)

### الخطوة 2: إنشاء Repository
1. اذهب إلى: https://github.com/new
2. اسم المشروع: `wormgpt-telegram-bot`
3. اختر: **Public**
4. ✅ اضغط **Create repository**

### الخطوة 3: رفع الملفات
1. في صفحة Repository الجديدة
2. اضغط **uploading an existing file**
3. اسحب جميع الملفات التالية:
   - `WormGPT.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
   - `README.md`
4. اكتب رسالة: "Initial commit"
5. اضغط **Commit changes**

### الخطوة 4: رفع على Render
1. اذهب إلى: https://render.com/
2. سجل دخول بحساب GitHub
3. اضغط **New +** → **Background Worker**
4. اختر repository: `wormgpt-telegram-bot`
5. الإعدادات:
   ```
   Name: wormgpt-bot
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python WormGPT.py
   ```
6. اضغط **Create Background Worker**

---

## 🎉 تم! البوت الآن يعمل 24/7

تحقق من logs في Render للتأكد من عمل البوت.

---

## 📱 اختبر البوت
أرسل `/start` في Telegram وستحصل على رد!

---

## ⚙️ التحديثات المستقبلية
1. عدل الملفات على GitHub مباشرة
2. Render سيعيد النشر تلقائياً

---

**🌟 مبروك! البوت الآن online!**
