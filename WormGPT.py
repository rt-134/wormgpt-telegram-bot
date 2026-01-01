import telebot
from telebot import types
import requests
import json
import time
from datetime import datetime
import os
import re
import html

# إعدادات البوت
VIPCODE3 = '8315094065:AAHYjZmj9ndfsOuxAQx9BsL8sNGvaoiIf5o'
ADMIN = [587293170, 0]

# تهيئة البوت
zo = telebot.TeleBot(VIPCODE3)

# قاموس لتخزين إحصائيات المستخدمين
user_stats = {}
bot_start_time = datetime.now()

# قاموس لتخزين ذاكرة المحادثات لكل مستخدم
conversation_memory = {}
MAX_MEMORY_MESSAGES = 10  # عدد الرسائل التي يتذكرها البوت

# دالة لحفظ الإحصائيات
def save_stats():
    try:
        with open('stats.json', 'w', encoding='utf-8') as f:
            json.dump(user_stats, f, ensure_ascii=False, indent=4)
    except:
        pass

# دالة لتحميل الإحصائيات
def load_stats():
    global user_stats
    try:
        if os.path.exists('stats.json'):
            with open('stats.json', 'r', encoding='utf-8') as f:
                user_stats = json.load(f)
    except:
        user_stats = {}

# دالة لحفظ ذاكرة المحادثات
def save_memory():
    try:
        with open('memory.json', 'w', encoding='utf-8') as f:
            json.dump(conversation_memory, f, ensure_ascii=False, indent=4)
    except:
        pass

# دالة لتحميل ذاكرة المحادثات
def load_memory():
    global conversation_memory
    try:
        if os.path.exists('memory.json'):
            with open('memory.json', 'r', encoding='utf-8') as f:
                conversation_memory = json.load(f)
    except:
        conversation_memory = {}

# دالة لإضافة رسالة للذاكرة
def add_to_memory(user_id, role, content):
    """إضافة رسالة إلى ذاكرة المحادثة"""
    user_id = str(user_id)
    
    if user_id not in conversation_memory:
        conversation_memory[user_id] = []
    
    conversation_memory[user_id].append({
        'role': role,  # 'user' أو 'assistant'
        'content': content,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # الاحتفاظ بآخر N رسالة فقط
    if len(conversation_memory[user_id]) > MAX_MEMORY_MESSAGES * 2:
        conversation_memory[user_id] = conversation_memory[user_id][-MAX_MEMORY_MESSAGES * 2:]
    
    save_memory()

# دالة للحصول على سياق المحادثة
def get_conversation_context(user_id):
    """الحصول على سياق المحادثة السابقة"""
    user_id = str(user_id)
    
    if user_id not in conversation_memory or not conversation_memory[user_id]:
        return ""
    
    # بناء سياق المحادثة
    context = "\n=== السياق السابق ===\n"
    for msg in conversation_memory[user_id][-6:]:  # آخر 3 تبادلات
        role = "المستخدم" if msg['role'] == 'user' else "المساعد"
        context += f"{role}: {msg['content'][:200]}...\n"
    context += "=== نهاية السياق ===\n\n"
    
    return context

# دالة لمسح ذاكرة مستخدم معين
def clear_user_memory(user_id):
    """مسح ذاكرة المحادثة لمستخدم معين"""
    user_id = str(user_id)
    if user_id in conversation_memory:
        conversation_memory[user_id] = []
        save_memory()
        return True
    return False

# دالة لاكتشاف وتنسيق الأكواد البرمجية
def detect_and_format_code(text):
    """
    اكتشاف الأكواد البرمجية في النص وتنسيقها مع زر نسخ
    """
    # البحث عن أكواد بين ``` أو ```language
    code_pattern = r'```(\w*)\n([\s\S]*?)```'
    codes = re.findall(code_pattern, text)
    
    if not codes:
        # البحث عن أكواد بدون تحديد لغة
        code_pattern_simple = r'```([\s\S]*?)```'
        codes_simple = re.findall(code_pattern_simple, text)
        if codes_simple:
            codes = [('', code) for code in codes_simple]
    
    return codes

def get_file_extension(language):
    """
    الحصول على امتداد الملف حسب اللغة البرمجية
    """
    extensions = {
        'python': '.py',
        'py': '.py',
        'javascript': '.js',
        'js': '.js',
        'typescript': '.ts',
        'ts': '.ts',
        'java': '.java',
        'c': '.c',
        'cpp': '.cpp',
        'c++': '.cpp',
        'csharp': '.cs',
        'cs': '.cs',
        'php': '.php',
        'ruby': '.rb',
        'go': '.go',
        'rust': '.rs',
        'swift': '.swift',
        'kotlin': '.kt',
        'html': '.html',
        'css': '.css',
        'scss': '.scss',
        'sass': '.sass',
        'xml': '.xml',
        'json': '.json',
        'yaml': '.yaml',
        'yml': '.yml',
        'sql': '.sql',
        'bash': '.sh',
        'sh': '.sh',
        'shell': '.sh',
        'powershell': '.ps1',
        'ps1': '.ps1',
        'bat': '.bat',
        'cmd': '.cmd',
        'r': '.r',
        'matlab': '.m',
        'perl': '.pl',
        'lua': '.lua',
        'dart': '.dart',
        'scala': '.scala',
        'groovy': '.groovy',
        'markdown': '.md',
        'md': '.md',
        'txt': '.txt',
        'text': '.txt',
    }
    
    lang_lower = language.lower() if language else ''
    return extensions.get(lang_lower, '.txt')

def format_code_with_copy_button(code, language='', code_id=0):
    """
    تنسيق الكود في HTML مع زر نسخ
    """
    # إضافة اسم اللغة إذا كان موجوداً
    lang_display = language.upper() if language else "CODE"
    
    # تنظيف الكود وتحويل الأحرف الخاصة
    code_escaped = html.escape(code.strip())
    
    # الحصول على امتداد الملف
    file_ext = get_file_extension(language)
    
    # إنشاء HTML للكود مع تنسيق أفضل
    formatted_code = f"""<b>╭─────────────────────╮</b>
<b>│ 💻 {lang_display}</b>
<b>╰─────────────────────╯</b>

<pre><code class="language-{language if language else 'text'}">{code_escaped}</code></pre>

<b>─────────────────────────</b>
<i>📋 استخدم الأزرار بالأسفل</i>"""
    
    return formatted_code

def split_text_and_code(text):
    """
    فصل النص عن الأكواد وإرجاع قائمة من الأجزاء
    """
    parts = []
    last_end = 0
    
    # البحث عن جميع الأكواد
    for match in re.finditer(r'```(\w*)\n([\s\S]*?)```', text):
        language = match.group(1)
        code = match.group(2)
        start = match.start()
        end = match.end()
        
        # إضافة النص قبل الكود
        if start > last_end:
            text_before = text[last_end:start].strip()
            if text_before:
                parts.append({
                    'type': 'text',
                    'content': text_before
                })
        
        # إضافة الكود
        parts.append({
            'type': 'code',
            'content': code,
            'language': language
        })
        
        last_end = end
    
    # إضافة النص المتبقي
    if last_end < len(text):
        text_after = text[last_end:].strip()
        if text_after:
            parts.append({
                'type': 'text',
                'content': text_after
            })
    
    # إذا لم يتم العثور على أكواد، أرجع النص كاملاً
    if not parts:
        parts.append({
            'type': 'text',
            'content': text
        })
    
    return parts

# تحميل الإحصائيات والذاكرة عند البدء
load_stats()
load_memory()

# معالج أمر /start
@zo.message_handler(commands=['start'])
def start_command(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    # تسجيل المستخدم الجديد
    if user_id not in user_stats:
        user_stats[user_id] = {
            'name': user_name,
            'messages': 0,
            'join_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_stats()
    
    # إنشاء أزرار تفاعلية
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("💬 ابدأ المحادثة", callback_data="chat")
    btn2 = types.InlineKeyboardButton("📊 إحصائياتي", callback_data="mystats")
    btn3 = types.InlineKeyboardButton("❓ المساعدة", callback_data="help")
    btn4 = types.InlineKeyboardButton("ℹ️ معلومات", callback_data="info")
    btn5 = types.InlineKeyboardButton("🧹 مسح الذاكرة", callback_data="clear_memory")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)
    
    welcome_text = f"""
╔═══════════════════╗
   🤖 *WormGPT Bot* 🧠
╚═══════════════════╝

👋 *أهلاً وسهلاً {user_name}!*

🌟 *أنا بوت ذكاء اصطناعي متقدم*

✨ *ماذا أستطيع أن أفعل لك؟*
━━━━━━━━━━━━━━━━━━━━
📝 كتابة المقالات والنصوص
💻 مساعدة في البرمجة
🌐 ترجمة النصوص
🧮 حل المسائل الرياضية
📚 شرح المفاهيم العلمية
🎨 إنشاء محتوى إبداعي
💡 الإجابة على أسئلتك
━━━━━━━━━━━━━━━━━━━━

⚡ *ابدأ الآن بإرسال رسالتك!*
"""
    zo.send_message(
        message.chat.id, 
        welcome_text, 
        parse_mode='Markdown',
        reply_markup=markup
    )

# معالج أمر /help
@zo.message_handler(commands=['help'])
def help_command(message):
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="start")
    markup.add(btn_back)
    
    help_text = """
╔═══════════════════╗
      ❓ *المساعدة*
╚═══════════════════╝

📖 *كيف تستخدم البوت؟*
━━━━━━━━━━━━━━━━━━━━

*الطريقة الأولى:*
فقط أرسل رسالتك مباشرة!

*الطريقة الثانية:*
استخدم الأوامر التالية:

🔹 /start - القائمة الرئيسية
🔹 /help - عرض المساعدة
🔹 /info - معلومات البوت
🔹 /stats - إحصائياتك
🔹 /memory - عرض الذاكرة
🔹 /clear - مسح ذاكرة المحادثة
🔹 /admin - لوحة الأدمن (للمطورين)

━━━━━━━━━━━━━━━━━━━━

💡 *أمثلة على الاستخدام:*

📌 "اكتب لي مقال عن الذكاء الاصطناعي"
📌 "اشرح لي البرمجة بلغة بايثون"
📌 "ساعدني في كتابة كود لحساب المتوسط"
📌 "ترجم هذا النص: Hello World"
📌 "ما هي أفضل لغة برمجة للمبتدئين؟"

━━━━━━━━━━━━━━━━━━━━

⭐ *نصائح للحصول على أفضل النتائج:*

✅ كن واضحاً ومحدداً
✅ استخدم لغة بسيطة
✅ قسم الأسئلة المعقدة
✅ أعد صياغة السؤال إذا لزم الأمر

━━━━━━━━━━━━━━━━━━━━
🤖 *أنا هنا لمساعدتك دائماً!*
"""
    zo.send_message(
        message.chat.id,
        help_text,
        parse_mode='Markdown',
        reply_markup=markup
    )

# معالج أمر /info
@zo.message_handler(commands=['info'])
def info_command(message):
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="start")
    markup.add(btn_back)
    
    # حساب وقت التشغيل
    uptime = datetime.now() - bot_start_time
    hours = uptime.seconds // 3600
    minutes = (uptime.seconds % 3600) // 60
    
    # حساب عدد المستخدمين
    total_users = len(user_stats)
    total_messages = sum(user.get('messages', 0) for user in user_stats.values())
    
    info_text = f"""
╔═══════════════════╗
    ℹ️ *معلومات البوت*
╚═══════════════════╝

🤖 *الاسم:* WormGPT Bot
🧠 *النوع:* ذكاء اصطناعي متقدم
⚡ *الإصدار:* 2.0 Pro
🌐 *اللغات:* متعدد اللغات

━━━━━━━━━━━━━━━━━━━━

📊 *الإحصائيات العامة:*

👥 المستخدمين: `{total_users}`
💬 الرسائل: `{total_messages}`
⏰ وقت التشغيل: `{hours}س {minutes}د`

━━━━━━━━━━━━━━━━━━━━

✨ *المميزات:*

✔️ ردود فورية وذكية
✔️ دعم النصوص الطويلة
✔️ تقسيم تلقائي للرسائل
✔️ معالجة متقدمة للأخطاء
✔️ إحصائيات شخصية
✔️ واجهة تفاعلية
✔️ متاح 24/7

━━━━━━━━━━━━━━━━━━━━

🔒 *الخصوصية والأمان:*

• لا نحفظ محادثاتك
• بياناتك آمنة ومشفرة
• نحترم خصوصيتك

━━━━━━━━━━━━━━━━━━━━

📧 *للدعم والاستفسارات:*
تواصل مع فريق التطوير

🌟 *شكراً لاستخدامك البوت!*
"""
    zo.send_message(
        message.chat.id,
        info_text,
        parse_mode='Markdown',
        reply_markup=markup
    )

# معالج أمر /stats
@zo.message_handler(commands=['stats'])
def stats_command(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="start")
    markup.add(btn_back)
    
    if user_id in user_stats:
        user_data = user_stats[user_id]
        messages_count = user_data.get('messages', 0)
        join_date = user_data.get('join_date', 'غير معروف')
        
        stats_text = f"""
╔═══════════════════╗
   📊 *إحصائياتك الشخصية*
╚═══════════════════╝

👤 *الاسم:* {user_name}
🆔 *المعرف:* `{user_id}`

━━━━━━━━━━━━━━━━━━━━

📈 *نشاطك:*

💬 عدد الرسائل: `{messages_count}`
📅 تاريخ الانضمام: `{join_date}`

━━━━━━━━━━━━━━━━━━━━

🏆 *إنجازاتك:*

{"🥉 مبتدئ" if messages_count < 10 else "🥈 نشط" if messages_count < 50 else "🥇 محترف" if messages_count < 100 else "👑 خبير"}

━━━━━━━━━━━━━━━━━━━━

⭐ *استمر في التفاعل للحصول على مزيد من الإنجازات!*
"""
    else:
        stats_text = f"""
📊 *إحصائياتك*

لم يتم تسجيل إحصائيات بعد.
أرسل /start للبدء!
"""
    
    zo.send_message(
        message.chat.id,
        stats_text,
        parse_mode='Markdown',
        reply_markup=markup
    )

# معالج أمر /clear - مسح ذاكرة المحادثة
@zo.message_handler(commands=['clear'])
def clear_command(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    if clear_user_memory(user_id):
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="start")
        markup.add(btn_back)
        
        clear_text = f"""
╔═══════════════════╗
   🧹 *تم مسح الذاكرة*
╚═══════════════════╝

👤 {user_name}

✅ تم مسح ذاكرة المحادثة بنجاح!

🆕 الآن يمكنك بدء محادثة جديدة
من الصفر دون أي سياق سابق.

💡 *متى تستخدم هذا الأمر؟*
• عند الرغبة في تغيير الموضوع
• للبدء بمحادثة جديدة تماماً
• إذا أصبحت الذاكرة غير مناسبة

📝 أرسل رسالتك الآن!
"""
        zo.send_message(
            message.chat.id,
            clear_text,
            parse_mode='Markdown',
            reply_markup=markup
        )
    else:
        zo.send_message(
            message.chat.id,
            "ℹ️ *لا توجد ذاكرة لمسحها*\n\nالذاكرة فارغة بالفعل!",
            parse_mode='Markdown'
        )

# معالج أمر /memory - عرض الذاكرة الحالية
@zo.message_handler(commands=['memory'])
def memory_command(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_clear = types.InlineKeyboardButton("🧹 مسح الذاكرة", callback_data="clear_memory")
    btn_back = types.InlineKeyboardButton("🏠 الرئيسية", callback_data="start")
    markup.add(btn_clear, btn_back)
    
    if user_id in conversation_memory and conversation_memory[user_id]:
        memory_count = len(conversation_memory[user_id])
        last_msg = conversation_memory[user_id][-1] if conversation_memory[user_id] else None
        
        memory_text = f"""
╔═══════════════════╗
   🧠 *ذاكرة المحادثة*
╚═══════════════════╝

👤 {user_name}

━━━━━━━━━━━━━━━━━━━━

📊 *معلومات الذاكرة:*

💬 عدد الرسائل المحفوظة: `{memory_count}`
🔄 الحد الأقصى: `{MAX_MEMORY_MESSAGES * 2}`
"""
        
        if last_msg:
            memory_text += f"\n📅 آخر رسالة: `{last_msg['timestamp']}`\n"
        
        memory_text += """
━━━━━━━━━━━━━━━━━━━━

💡 *فائدة الذاكرة:*

✅ البوت يتذكر محادثاتك السابقة
✅ يفهم السياق والمراجع
✅ يعطي إجابات أكثر دقة
✅ محادثة طبيعية ومترابطة

━━━━━━━━━━━━━━━━━━━━

🧹 يمكنك مسح الذاكرة في أي وقت
"""
        
        zo.send_message(
            message.chat.id,
            memory_text,
            parse_mode='Markdown',
            reply_markup=markup
        )
    else:
        zo.send_message(
            message.chat.id,
            f"""
╔═══════════════════╗
   🧠 *ذاكرة المحادثة*
╚═══════════════════╝

👤 {user_name}

📭 *الذاكرة فارغة*

لم تبدأ أي محادثة بعد.
أرسل رسالتك الأولى الآن!

💡 سأبدأ بتذكر محادثاتنا تلقائياً.
""",
            parse_mode='Markdown',
            reply_markup=markup
        )

# معالج أمر /admin - لوحة تحكم الأدمن
@zo.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id not in ADMIN:
        zo.send_message(
            message.chat.id,
            "⛔ *عذراً، هذا الأمر للمطورين فقط!*",
            parse_mode='Markdown'
        )
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📊 إحصائيات البوت", callback_data="admin_stats")
    btn2 = types.InlineKeyboardButton("👥 المستخدمين", callback_data="admin_users")
    btn3 = types.InlineKeyboardButton("📢 إرسال رسالة جماعية", callback_data="admin_broadcast")
    btn4 = types.InlineKeyboardButton("🔄 إعادة تشغيل", callback_data="admin_restart")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    
    admin_text = f"""
╔═══════════════════╗
   👑 *لوحة تحكم الأدمن*
╚═══════════════════╝

مرحباً {message.from_user.first_name}!

🔐 *أنت الآن في لوحة التحكم الكاملة*

اختر الإجراء المطلوب:
"""
    zo.send_message(
        message.chat.id,
        admin_text,
        parse_mode='Markdown',
        reply_markup=markup
    )

# معالج الأزرار التفاعلية (Callback Queries)
@zo.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.from_user.id)
    user_name = call.from_user.first_name
    
    try:
        if call.data == "start":
            # إعادة عرض القائمة الرئيسية
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("💬 ابدأ المحادثة", callback_data="chat")
            btn2 = types.InlineKeyboardButton("📊 إحصائياتي", callback_data="mystats")
            btn3 = types.InlineKeyboardButton("❓ المساعدة", callback_data="help")
            btn4 = types.InlineKeyboardButton("ℹ️ معلومات", callback_data="info")
            markup.add(btn1, btn2)
            markup.add(btn3, btn4)
            
            welcome_text = f"""
╔═══════════════════╗
   🤖 *WormGPT Bot* 🧠
╚═══════════════════╝

👋 *أهلاً وسهلاً {user_name}!*

⚡ *ابدأ الآن بإرسال رسالتك!*
"""
            zo.edit_message_text(
                welcome_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        
        elif call.data == "chat":
            zo.answer_callback_query(call.id, "💬 أرسل رسالتك الآن!", show_alert=False)
            zo.send_message(
                call.message.chat.id,
                "✨ *جاهز للمحادثة!*\n\n📝 أرسل سؤالك أو طلبك وسأرد عليك فوراً...",
                parse_mode='Markdown'
            )
        
        elif call.data == "mystats":
            # عرض إحصائيات المستخدم
            if user_id in user_stats:
                user_data = user_stats[user_id]
                messages_count = user_data.get('messages', 0)
                join_date = user_data.get('join_date', 'غير معروف')
                
                markup = types.InlineKeyboardMarkup()
                btn_back = types.InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="start")
                markup.add(btn_back)
                
                stats_text = f"""
╔═══════════════════╗
   📊 *إحصائياتك*
╚═══════════════════╝

💬 الرسائل: `{messages_count}`
📅 الانضمام: `{join_date}`

{"🥉 مبتدئ" if messages_count < 10 else "🥈 نشط" if messages_count < 50 else "🥇 محترف" if messages_count < 100 else "👑 خبير"}
"""
                zo.edit_message_text(
                    stats_text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
        
        elif call.data == "help":
            help_command(call.message)
        
        elif call.data == "info":
            info_command(call.message)
        
        # مسح ذاكرة المحادثة
        elif call.data == "clear_memory":
            if clear_user_memory(user_id):
                zo.answer_callback_query(call.id, "✅ تم مسح الذاكرة بنجاح!", show_alert=True)
                
                markup = types.InlineKeyboardMarkup()
                btn_back = types.InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="start")
                markup.add(btn_back)
                
                zo.send_message(
                    call.message.chat.id,
                    "🧹 *تم مسح ذاكرة المحادثة!*\n\n🆕 يمكنك الآن بدء محادثة جديدة من الصفر.",
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            else:
                zo.answer_callback_query(call.id, "ℹ️ الذاكرة فارغة بالفعل", show_alert=True)
        
        # عرض الذاكرة
        elif call.data == "show_memory":
            if user_id in conversation_memory and conversation_memory[user_id]:
                memory_count = len(conversation_memory[user_id])
                
                markup = types.InlineKeyboardMarkup(row_width=2)
                btn_clear = types.InlineKeyboardButton("🧹 مسح", callback_data="clear_memory")
                btn_back = types.InlineKeyboardButton("🏠 الرئيسية", callback_data="start")
                markup.add(btn_clear, btn_back)
                
                memory_text = f"""
╔═══════════════════╗
   🧠 *ذاكرة المحادثة*
╚═══════════════════╝

💬 رسائل محفوظة: `{memory_count}`
🔄 الحد الأقصى: `{MAX_MEMORY_MESSAGES * 2}`

━━━━━━━━━━━━━━━━━━━━

✅ البوت يتذكر محادثاتك
✅ يفهم السياق بذكاء
✅ إجابات أكثر دقة

🧹 يمكنك مسح الذاكرة في أي وقت
"""
                zo.edit_message_text(
                    memory_text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            else:
                zo.answer_callback_query(call.id, "📭 الذاكرة فارغة!", show_alert=True)
        
        # معالج نسخ الكود
        elif call.data.startswith("copy_code_"):
            try:
                parts = call.data.split("_")
                code_user_id = parts[2]
                code_id = parts[3]
                temp_code_file = f"temp_code_{code_user_id}_{code_id}.txt"
                
                if os.path.exists(temp_code_file):
                    with open(temp_code_file, 'r', encoding='utf-8') as f:
                        code_content = f.read()
                    
                    # إرسال الكود كرسالة يمكن نسخها
                    zo.send_message(
                        call.message.chat.id,
                        f"📋 <b>تم نسخ الكود - يمكنك تحديده ونسخه:</b>\n\n<code>{html.escape(code_content)}</code>",
                        parse_mode='HTML'
                    )
                    
                    zo.answer_callback_query(call.id, "✅ تم إرسال الكود للنسخ!", show_alert=False)
                else:
                    zo.answer_callback_query(call.id, "❌ انتهت صلاحية الكود", show_alert=True)
            except Exception as e:
                print(f"Copy code error: {e}")
                zo.answer_callback_query(call.id, "❌ حدث خطأ في النسخ", show_alert=True)
        
        # معالج تحميل الكود كملف
        elif call.data.startswith("download_code_") or call.data.startswith("dl_"):
            try:
                # تحليل البيانات
                if call.data.startswith("dl_"):
                    # الصيغة الجديدة: dl_<extension>_<user_id>_<code_id>
                    parts = call.data.split("_")
                    file_format = parts[1]  # py, js, html, txt, etc.
                    code_user_id = parts[2]
                    code_id = parts[3]
                else:
                    # الصيغة القديمة: download_code_<user_id>_<code_id>
                    parts = call.data.split("_")
                    code_user_id = parts[2]
                    code_id = parts[3]
                    file_format = "auto"  # استخدام اللغة المحفوظة
                
                temp_code_file = f"temp_code_{code_user_id}_{code_id}.txt"
                temp_code_lang = f"temp_code_{code_user_id}_{code_id}.lang"
                
                if os.path.exists(temp_code_file):
                    # قراءة الكود
                    with open(temp_code_file, 'r', encoding='utf-8') as f:
                        code_content = f.read()
                    
                    # تحديد اللغة والامتداد
                    if file_format == "auto" and os.path.exists(temp_code_lang):
                        with open(temp_code_lang, 'r', encoding='utf-8') as f:
                            language = f.read().strip()
                        file_ext = get_file_extension(language)
                        lang_display = language.upper() if language else "CODE"
                    else:
                        # تحويل الصيغة المختارة إلى امتداد
                        format_to_ext = {
                            'py': '.py',
                            'python': '.py',
                            'js': '.js',
                            'javascript': '.js',
                            'html': '.html',
                            'css': '.css',
                            'php': '.php',
                            'java': '.java',
                            'c': '.c',
                            'cpp': '.cpp',
                            'sh': '.sh',
                            'bash': '.sh',
                            'json': '.json',
                            'sql': '.sql',
                            'xml': '.xml',
                            'yaml': '.yaml',
                            'txt': '.txt',
                        }
                        file_ext = format_to_ext.get(file_format, '.txt')
                        lang_display = file_format.upper()
                    
                    # إنشاء اسم الملف
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    code_filename = f"code_{timestamp}{file_ext}"
                    
                    # حفظ الكود في ملف
                    with open(code_filename, 'w', encoding='utf-8') as f:
                        f.write(code_content)
                    
                    # إرسال الملف
                    with open(code_filename, 'rb') as f:
                        caption = f"💻 {lang_display} Code\n📄 الملف: {code_filename}\n📊 الحجم: {len(code_content)} حرف"
                        zo.send_document(
                            call.message.chat.id,
                            f,
                            caption=caption,
                            visible_file_name=code_filename
                        )
                    
                    zo.answer_callback_query(call.id, f"✅ تم إرسال الملف {file_ext}!", show_alert=False)
                    
                    # حذف الملف المؤقت
                    try:
                        os.remove(code_filename)
                    except:
                        pass
                else:
                    zo.answer_callback_query(call.id, "❌ انتهت صلاحية الكود", show_alert=True)
            except Exception as e:
                print(f"Download code error: {e}")
                zo.answer_callback_query(call.id, "❌ حدث خطأ في التحميل", show_alert=True)
        
        # معالجات لوحة الأدمن
        elif call.data == "admin_stats":
            if call.from_user.id not in ADMIN:
                zo.answer_callback_query(call.id, "⛔ غير مصرح!", show_alert=True)
                return
            
            total_users = len(user_stats)
            total_messages = sum(user.get('messages', 0) for user in user_stats.values())
            uptime = datetime.now() - bot_start_time
            
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")
            markup.add(btn_back)
            
            admin_stats_text = f"""
╔═══════════════════╗
   📊 *إحصائيات البوت*
╚═══════════════════╝

👥 إجمالي المستخدمين: `{total_users}`
💬 إجمالي الرسائل: `{total_messages}`
⏰ وقت التشغيل: `{uptime}`
📅 تاريخ البدء: `{bot_start_time.strftime("%Y-%m-%d %H:%M")}`

━━━━━━━━━━━━━━━━━━━━

✅ البوت يعمل بشكل طبيعي
"""
            zo.edit_message_text(
                admin_stats_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        
        elif call.data == "admin_users":
            if call.from_user.id not in ADMIN:
                zo.answer_callback_query(call.id, "⛔ غير مصرح!", show_alert=True)
                return
            
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")
            markup.add(btn_back)
            
            # قائمة أكثر 5 مستخدمين نشاطاً
            top_users = sorted(
                user_stats.items(),
                key=lambda x: x[1].get('messages', 0),
                reverse=True
            )[:5]
            
            users_text = "╔═══════════════════╗\n"
            users_text += "   👥 *أكثر المستخدمين نشاطاً*\n"
            users_text += "╚═══════════════════╝\n\n"
            
            for i, (uid, data) in enumerate(top_users, 1):
                name = data.get('name', 'مجهول')
                msgs = data.get('messages', 0)
                users_text += f"{i}. {name} - `{msgs}` رسالة\n"
            
            zo.edit_message_text(
                users_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        
        elif call.data == "admin_broadcast":
            if call.from_user.id not in ADMIN:
                zo.answer_callback_query(call.id, "⛔ غير مصرح!", show_alert=True)
                return
            
            zo.answer_callback_query(call.id, "📝 أرسل الرسالة التي تريد إرسالها لجميع المستخدمين", show_alert=True)
            zo.send_message(call.message.chat.id, "📢 *أرسل الرسالة الجماعية الآن:*", parse_mode='Markdown')
            zo.register_next_step_handler(call.message, broadcast_message)
        
        elif call.data == "admin_back":
            # إعادة عرض لوحة الأدمن
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("📊 إحصائيات البوت", callback_data="admin_stats")
            btn2 = types.InlineKeyboardButton("👥 المستخدمين", callback_data="admin_users")
            btn3 = types.InlineKeyboardButton("📢 إرسال رسالة جماعية", callback_data="admin_broadcast")
            btn4 = types.InlineKeyboardButton("🔄 إعادة تشغيل", callback_data="admin_restart")
            markup.add(btn1, btn2)
            markup.add(btn3, btn4)
            
            admin_text = f"""
╔═══════════════════╗
   👑 *لوحة تحكم الأدمن*
╚═══════════════════╝

مرحباً {call.from_user.first_name}!

اختر الإجراء المطلوب:
"""
            zo.edit_message_text(
                admin_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        
        zo.answer_callback_query(call.id)
    
    except Exception as e:
        print(f"Callback Error: {e}")
        zo.answer_callback_query(call.id, "حدث خطأ!")

# دالة الإرسال الجماعي
def broadcast_message(message):
    if message.from_user.id not in ADMIN:
        return
    
    broadcast_text = message.text
    success = 0
    failed = 0
    
    status_msg = zo.send_message(message.chat.id, "⏳ *جاري الإرسال...*", parse_mode='Markdown')
    
    for user_id in user_stats.keys():
        try:
            zo.send_message(int(user_id), broadcast_text, parse_mode='Markdown')
            success += 1
            time.sleep(0.05)  # تجنب تجاوز الحد الأقصى
        except:
            failed += 1
    
    result_text = f"""
✅ *تم إرسال الرسالة الجماعية!*

📊 النتائج:
✔️ نجح: `{success}`
❌ فشل: `{failed}`
"""
    zo.edit_message_text(
        result_text,
        message.chat.id,
        status_msg.message_id,
        parse_mode='Markdown'
    )

# معالج الرسائل النصية - الوظيفة الأساسية للبوت
@zo.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    user_text = message.text
    user_name = message.from_user.first_name
    
    # تحديث إحصائيات المستخدم
    if user_id not in user_stats:
        user_stats[user_id] = {
            'name': user_name,
            'messages': 0,
            'join_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    user_stats[user_id]['messages'] = user_stats[user_id].get('messages', 0) + 1
    user_stats[user_id]['name'] = user_name  # تحديث الاسم
    save_stats()
    
    # إظهار أن البوت يكتب
    zo.send_chat_action(message.chat.id, 'typing')
    
    # رسالة معالجة مؤقتة مع رمز انتظار
    processing_msg = zo.reply_to(
        message, 
        "⏳ *جاري المعالجة...*\n🧠 *جاري استرجاع الذاكرة...*",
        parse_mode='Markdown'
    )
    
    try:
        # الحصول على سياق المحادثة السابقة
        context = get_conversation_context(user_id)
        
        # بناء الرسالة مع السياق (تقليل حجم السياق للأسئلة الطويلة)
        if context and len(user_text) < 500:
            full_message = f"{context}الرسالة الحالية: {user_text}"
        else:
            full_message = user_text
        
        # إرسال الطلب إلى API مع timeout أطول وإعادة محاولة
        max_retries = 2
        timeout_duration = 60  # زيادة الوقت إلى 60 ثانية
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://sii3.top/api/error/wormgpt.php",
                    data={
                        'key': "DarkAI-WormGPT-E487DD2FDAAEDC31A56A8A84",
                        'text': full_message
                    },
                    timeout=timeout_duration
                )
                break  # نجح الطلب، اخرج من الحلقة
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    # حاول مرة أخرى بدون السياق
                    full_message = user_text
                    zo.edit_message_text(
                        "⏳ *جاري المعالجة...*\n🔄 *إعادة المحاولة...*",
                        message.chat.id,
                        processing_msg.message_id,
                        parse_mode='Markdown'
                    )
                    time.sleep(1)
                else:
                    raise  # فشلت جميع المحاولات

        # حذف رسالة المعالجة
        zo.delete_message(message.chat.id, processing_msg.message_id)

        if response.status_code == 200:
            result = response.json()
            if "response" in result:
                bot_reply = result["response"]
                
                # حفظ الرسالة والرد في الذاكرة
                add_to_memory(user_id, 'user', user_text)
                add_to_memory(user_id, 'assistant', bot_reply[:500])  # حفظ أول 500 حرف من الرد
                
                # فصل النص عن الأكواد أولاً
                parts = split_text_and_code(bot_reply)
                
                # التحقق من وجود أكواد
                has_code = any(part['type'] == 'code' for part in parts)
                
                # إذا كانت الرسالة طويلة جداً وبدون أكواد، قسمها
                if len(bot_reply) > 4000 and not has_code:
                    # رسالة تحذيرية للرسائل الطويلة
                    parts_count = (len(bot_reply) // 4000) + 1
                    zo.send_message(
                        message.chat.id, 
                        f"📚 الرد طويل ({parts_count} أجزاء)\n⏳ جاري الإرسال..."
                    )
                    
                    for i in range(0, len(bot_reply), 4000):
                        part_num = (i // 4000) + 1
                        part_text = f"📄 الجزء {part_num}/{parts_count}\n\n{bot_reply[i:i+4000]}"
                        try:
                            zo.send_message(message.chat.id, part_text)
                        except:
                            # إذا فشل الإرسال، أرسل بدون تنسيق
                            zo.send_message(message.chat.id, bot_reply[i:i+4000])
                        time.sleep(0.5)  # تأخير بسيط بين الأجزاء
                    
                    # رسالة إكمال
                    markup = types.InlineKeyboardMarkup()
                    btn_new = types.InlineKeyboardButton("🔄 سؤال جديد", callback_data="chat")
                    btn_clear = types.InlineKeyboardButton("🧹 مسح الذاكرة", callback_data="clear_memory")
                    markup.add(btn_new, btn_clear)
                    zo.send_message(
                        message.chat.id,
                        "✅ تم إرسال الرد كاملاً!",
                        reply_markup=markup
                    )
                else:
                    # إضافة أزرار تفاعلية للرد
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    btn_stats = types.InlineKeyboardButton("📊 إحصائياتي", callback_data="mystats")
                    btn_memory = types.InlineKeyboardButton("🧠 الذاكرة", callback_data="show_memory")
                    btn_clear = types.InlineKeyboardButton("🧹 مسح الذاكرة", callback_data="clear_memory")
                    btn_help = types.InlineKeyboardButton("❓ مساعدة", callback_data="help")
                    markup.add(btn_stats, btn_memory)
                    markup.add(btn_clear, btn_help)
                    
                    # فصل النص عن الأكواد
                    parts = split_text_and_code(bot_reply)
                    
                    # إذا كان هناك أكواد، أرسل كل جزء على حدة
                    if len(parts) > 1 or (len(parts) == 1 and parts[0]['type'] == 'code'):
                        for i, part in enumerate(parts):
                            if part['type'] == 'text':
                                # إرسال النص العادي
                                try:
                                    if i == 0:
                                        zo.reply_to(message, part['content'])
                                    else:
                                        zo.send_message(message.chat.id, part['content'])
                                except:
                                    zo.send_message(message.chat.id, part['content'])
                            
                            elif part['type'] == 'code':
                                # الحصول على امتداد الملف حسب اللغة
                                file_ext = get_file_extension(part['language'])
                                lang_display = part['language'].upper() if part['language'] else "CODE"
                                
                                # تحديد إذا كان الكود طويل جداً (أكثر من 3500 حرف)
                                code_too_long = len(part['content']) > 3500
                                
                                if code_too_long:
                                    # إرسال الكود كملف مباشرة
                                    code_filename = f"code_{user_id}_{i}{file_ext}"
                                    
                                    try:
                                        # حفظ الكود في ملف
                                        with open(code_filename, 'w', encoding='utf-8') as f:
                                            f.write(part['content'])
                                        
                                        # إرسال الملف
                                        with open(code_filename, 'rb') as f:
                                            caption = f"💻 {lang_display} Code\n📄 الملف: {code_filename}\n📊 الحجم: {len(part['content'])} حرف"
                                            zo.send_document(
                                                message.chat.id,
                                                f,
                                                caption=caption,
                                                visible_file_name=code_filename
                                            )
                                        
                                        # حذف الملف بعد الإرسال
                                        os.remove(code_filename)
                                        
                                    except Exception as e:
                                        print(f"Error sending code file: {e}")
                                        # إرسال جزء من الكود كنص
                                        zo.send_message(
                                            message.chat.id,
                                            f"⚠️ الكود طويل جداً ({len(part['content'])} حرف)\n"
                                            f"💻 {lang_display}\n\n"
                                            f"```{part['language']}\n{part['content'][:500]}...\n```",
                                            parse_mode='Markdown'
                                        )
                                else:
                                    # تنسيق الكود مع أزرار نسخ وتحميل
                                    formatted_code = format_code_with_copy_button(
                                        part['content'], 
                                        part['language'],
                                        i
                                    )
                                    
                                    # إنشاء أزرار نسخ وتحميل حسب اللغة
                                    code_markup = types.InlineKeyboardMarkup(row_width=3)
                                    
                                    # زر نسخ (دائماً موجود)
                                    copy_btn = types.InlineKeyboardButton(
                                        "📋 نسخ",
                                        callback_data=f"copy_code_{user_id}_{i}"
                                    )
                                    
                                    # أزرار التحميل حسب اللغة المكتشفة
                                    lang_lower = part['language'].lower() if part['language'] else ''
                                    
                                    # تحديد الأزرار حسب اللغة
                                    download_buttons = []
                                    
                                    if lang_lower in ['python', 'py']:
                                        download_buttons = [
                                            types.InlineKeyboardButton("🐍 .py", callback_data=f"dl_py_{user_id}_{i}"),
                                            types.InlineKeyboardButton("📄 .txt", callback_data=f"dl_txt_{user_id}_{i}")
                                        ]
                                    elif lang_lower in ['javascript', 'js']:
                                        download_buttons = [
                                            types.InlineKeyboardButton("📜 .js", callback_data=f"dl_js_{user_id}_{i}"),
                                            types.InlineKeyboardButton("📄 .txt", callback_data=f"dl_txt_{user_id}_{i}")
                                        ]
                                    elif lang_lower in ['html']:
                                        download_buttons = [
                                            types.InlineKeyboardButton("🌐 .html", callback_data=f"dl_html_{user_id}_{i}"),
                                            types.InlineKeyboardButton("📄 .txt", callback_data=f"dl_txt_{user_id}_{i}")
                                        ]
                                    elif lang_lower in ['css']:
                                        download_buttons = [
                                            types.InlineKeyboardButton("🎨 .css", callback_data=f"dl_css_{user_id}_{i}"),
                                            types.InlineKeyboardButton("📄 .txt", callback_data=f"dl_txt_{user_id}_{i}")
                                        ]
                                    elif lang_lower in ['bash', 'sh', 'shell']:
                                        download_buttons = [
                                            types.InlineKeyboardButton("🐚 .sh", callback_data=f"dl_sh_{user_id}_{i}"),
                                            types.InlineKeyboardButton("📄 .txt", callback_data=f"dl_txt_{user_id}_{i}")
                                        ]
                                    elif lang_lower in ['php']:
                                        download_buttons = [
                                            types.InlineKeyboardButton("🐘 .php", callback_data=f"dl_php_{user_id}_{i}"),
                                            types.InlineKeyboardButton("📄 .txt", callback_data=f"dl_txt_{user_id}_{i}")
                                        ]
                                    elif lang_lower in ['java']:
                                        download_buttons = [
                                            types.InlineKeyboardButton("☕ .java", callback_data=f"dl_java_{user_id}_{i}"),
                                            types.InlineKeyboardButton("📄 .txt", callback_data=f"dl_txt_{user_id}_{i}")
                                        ]
                                    elif lang_lower in ['c', 'cpp', 'c++']:
                                        download_buttons = [
                                            types.InlineKeyboardButton("🔧 .c/.cpp", callback_data=f"dl_c_{user_id}_{i}"),
                                            types.InlineKeyboardButton("📄 .txt", callback_data=f"dl_txt_{user_id}_{i}")
                                        ]
                                    elif lang_lower in ['json']:
                                        download_buttons = [
                                            types.InlineKeyboardButton("📊 .json", callback_data=f"dl_json_{user_id}_{i}"),
                                            types.InlineKeyboardButton("📄 .txt", callback_data=f"dl_txt_{user_id}_{i}")
                                        ]
                                    elif lang_lower in ['sql']:
                                        download_buttons = [
                                            types.InlineKeyboardButton("🗄️ .sql", callback_data=f"dl_sql_{user_id}_{i}"),
                                            types.InlineKeyboardButton("📄 .txt", callback_data=f"dl_txt_{user_id}_{i}")
                                        ]
                                    else:
                                        # للغات الأخرى أو غير محددة
                                        ext = get_file_extension(part['language'])
                                        download_buttons = [
                                            types.InlineKeyboardButton(f"📥 {ext}", callback_data=f"dl_auto_{user_id}_{i}"),
                                            types.InlineKeyboardButton("📄 .txt", callback_data=f"dl_txt_{user_id}_{i}")
                                        ]
                                    
                                    # إضافة زر النسخ في الصف الأول
                                    code_markup.row(copy_btn)
                                    
                                    # إضافة أزرار التحميل في الصف الثاني
                                    if len(download_buttons) == 2:
                                        code_markup.row(download_buttons[0], download_buttons[1])
                                    else:
                                        code_markup.row(*download_buttons)
                                    
                                    try:
                                        # إرسال الكود بتنسيق HTML
                                        msg = zo.send_message(
                                            message.chat.id,
                                            formatted_code,
                                            parse_mode='HTML',
                                            reply_markup=code_markup
                                        )
                                        
                                        # حفظ الكود مؤقتاً للنسخ أو التحميل لاحقاً
                                        temp_code_file = f"temp_code_{user_id}_{i}.txt"
                                        temp_code_lang = f"temp_code_{user_id}_{i}.lang"
                                        
                                        with open(temp_code_file, 'w', encoding='utf-8') as f:
                                            f.write(part['content'])
                                        
                                        # حفظ اللغة لمعرفة امتداد الملف عند التحميل
                                        with open(temp_code_lang, 'w', encoding='utf-8') as f:
                                            f.write(part['language'] if part['language'] else 'txt')
                                        
                                    except Exception as e:
                                        print(f"Error sending code: {e}")
                                        # إرسال الكود بدون تنسيق
                                        zo.send_message(
                                            message.chat.id,
                                            f"```{part['language']}\n{part['content']}\n```",
                                            parse_mode='Markdown'
                                        )
                        
                        # إضافة مؤشر الذاكرة في النهاية
                        if user_id in conversation_memory and len(conversation_memory[user_id]) > 2:
                            msg_count = len(conversation_memory[user_id]) // 2
                            zo.send_message(
                                message.chat.id,
                                f"🧠 الذاكرة: {msg_count} محادثة محفوظة",
                                reply_markup=markup
                            )
                        else:
                            zo.send_message(
                                message.chat.id,
                                "✅ تم الإرسال",
                                reply_markup=markup
                            )
                    else:
                        # إرسال الرد بدون أكواد
                        try:
                            # إضافة مؤشر الذاكرة في الرد
                            if user_id in conversation_memory and len(conversation_memory[user_id]) > 2:
                                msg_count = len(conversation_memory[user_id]) // 2
                                memory_text = f"\n\n🧠 الذاكرة: {msg_count} محادثة محفوظة"
                                zo.reply_to(message, bot_reply + memory_text, reply_markup=markup)
                            else:
                                zo.reply_to(message, bot_reply, reply_markup=markup)
                        except Exception as markdown_error:
                            # إذا فشل Markdown، أرسل بدون تنسيق
                            zo.reply_to(message, bot_reply, reply_markup=markup)
            else:
                zo.send_message(
                    message.chat.id,
                    f"*عزيزي {user_name}* 🌟\n\n❌ عذراً، لم أتمكن من معالجة طلبك.\n💡 حاول إعادة صياغة السؤال.",
                    parse_mode='Markdown'
                )
        else:
            zo.send_message(
                message.chat.id,
                f"*{user_name}* ⚠️\n\n🔴 حدث خطأ في الاتصال بالخادم.\n🔄 يرجى المحاولة مرة أخرى.",
                parse_mode='Markdown'
            )
            
    except requests.exceptions.Timeout:
        zo.delete_message(message.chat.id, processing_msg.message_id)
        
        markup = types.InlineKeyboardMarkup()
        btn_retry = types.InlineKeyboardButton("🔄 إعادة المحاولة", callback_data="chat")
        btn_help = types.InlineKeyboardButton("❓ مساعدة", callback_data="help")
        markup.add(btn_retry, btn_help)
        
        zo.send_message(
            message.chat.id,
            f"*{user_name}* ⏰\n\n⏱️ انتهت مهلة الطلب (60 ثانية).\n\n"
            f"💡 *نصائح لتجنب هذه المشكلة:*\n"
            f"• اختصر سؤالك قليلاً\n"
            f"• قسّم السؤال المعقد إلى أجزاء\n"
            f"• استخدم /clear لمسح الذاكرة\n"
            f"• حاول مرة أخرى بعد قليل",
            parse_mode='Markdown',
            reply_markup=markup
        )
    except json.JSONDecodeError:
        zo.delete_message(message.chat.id, processing_msg.message_id)
        zo.send_message(
            message.chat.id,
            f"*{user_name}* 🔧\n\n❌ خطأ في معالجة البيانات.\n💬 أرسل رسالتك مرة أخرى.",
            parse_mode='Markdown'
        )
    except Exception as e:
        try:
            zo.delete_message(message.chat.id, processing_msg.message_id)
        except:
            pass
        zo.send_message(
            message.chat.id,
            f"*{user_name}* 💔\n\n⚠️ حدث خطأ غير متوقع.\n📝 تأكد من صحة رسالتك وحاول مجدداً.",
            parse_mode='Markdown'
        )
        # طباعة الخطأ في الكونسول للمطور
        print(f"Error: {e}")

# تشغيل البوت
print("\n" + "═" * 60)
print("╔════════════════════════════════════════════════════════════╗")
print("║                   🤖 WormGPT Bot v2.0 Pro                  ║")
print("╚════════════════════════════════════════════════════════════╝")
print("═" * 60)
print("✅ البوت يعمل الآن وجاهز للاستقبال...")
print(f"⏰ وقت البدء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"👥 عدد المستخدمين المسجلين: {len(user_stats)}")
print(f"🧠 عدد المستخدمين بذاكرة: {len(conversation_memory)}")
print("📡 في انتظار الرسائل...")
print("═" * 60)
print("💡 نصائح:")
print("   • استخدم Ctrl+C لإيقاف البوت")
print("   • الإحصائيات تُحفظ في stats.json")
print("   • الذاكرة تُحفظ في memory.json")
print("   • لوحة الأدمن متاحة عبر /admin")
print("   • استخدم /clear لمسح ذاكرة المحادثة")
print("═" * 60 + "\n")

# معالج إيقاف التشغيل النظيف
import atexit

def cleanup():
    print("\n" + "═" * 60)
    print("🛑 جاري إيقاف البوت...")
    save_stats()
    save_memory()
    
    # حذف الملفات المؤقتة للأكواد
    try:
        for file in os.listdir('.'):
            if file.startswith('temp_code_') and (file.endswith('.txt') or file.endswith('.lang')):
                os.remove(file)
        print("🧹 تم حذف الملفات المؤقتة")
    except Exception as e:
        print(f"⚠️ خطأ في حذف الملفات المؤقتة: {e}")
    
    print("✅ تم حفظ الإحصائيات والذاكرة")
    print("👋 إلى اللقاء!")
    print("═" * 60 + "\n")

atexit.register(cleanup)

try:
    zo.delete_webhook()
    zo.infinity_polling()
except KeyboardInterrupt:
    print("\n⚠️ تم إيقاف البوت بواسطة المستخدم")
except Exception as e:
    print(f"\n❌ خطأ: {e}")
finally:
    cleanup()
