# Q&A Arxiv Gruppasini Sozlash

## Qadamlar:

1. **Telegram'da guruh yaratish:**
   - Telegram'da yangi guruh yarating (masalan: "AHD Q&A Arxiv")
   - Guruhni **private** (yopiq) qilib qo'ying

2. **Botni guruhga qo'shish:**
   - Yaratgan guruhingizga botni admin qilib qo'shing
   - Bot xabar yuborish huquqiga ega bo'lishi kerak

3. **Guruh ID sini olish:**
   
   **Usul 1: @userinfobot orqali**
   - Guruhga @userinfobot ni qo'shing
   - Bot avtomatik guruh ID sini yuboradi
   - Misol: `-1001234567890`
   
   **Usul 2: Bot orqali**
   - Guruhga biror xabar yuboring
   - Bot loglaridan ID ni topish mumkin

4. **Railway'da sozlash:**
   - Railway dashboard → Variables
   - Yangi variable qo'shing:
     ```
     ARCHIVE_GROUP_ID=-1001234567890
     ```
   - Deploy qiling

5. **Test qilish:**
   - Botda savol-javob jarayonini yakunlang
   - Admin javob berganidan keyin arxiv guruhiga xabar keladi

## Xabar formati:

```
📚 Yangi Savol-Javob Arxivi

🆔 Murojaat: #123
📅 Sana: 16.02.2026

❓ Savol:
[Foydalanuvchi savoli]

💬 Javob:
[Admin javobi]

━━━━━━━━━━━━━━━━━━━
```

## Muhim:
- Agar `ARCHIVE_GROUP_ID` sozlanmasa, arxivlash ishlamaydi (xato bermaydi)
- Guruh ID doim **manfiy** son (-1001234567890)
- Bot guruhda admin bo'lishi shart
