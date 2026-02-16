# GitHubga Yuklash Bo'yicha Qo'llanma (Guide)

Sizning kompyuteringizda **Git** o'rnatilmagan yoki topilmadi. Shuning uchun loyihani GitHubga yuklash uchun quyidagi qadamlarni bajaring.

## 1-qadam: Git Dasturini O'rnatish

1.  [git-scm.com/downloads](https://git-scm.com/downloads) saytiga kiring.
2.  **Download for Windows** tugmasini bosing.
3.  Yuklab olingan faylni ishga tushiring va **Next** tugmalarini bosib o'rnatib chiqing.

## 2-qadam: GitHub Repozitoriy Yaratish

1.  [github.com](https://github.com) saytiga kiring va ro'yxatdan o'ting (agar akkaunt bo'lmasa).
2.  Yuqori o'ng burchakdagi **+** tugmasini bosib, **New repository** ni tanlang.
3.  **Repository name** ga nom bering (masalan: `telegram-qa-bot`).
4.  **Create repository** tugmasini bosing.

## 3-qadam: Loyihani Yuklash (Terminal orqali)

Git o'rnatilgach, loyiha papkasida (`c:\Users\azizb\.gemini\antigravity\playground\deep-void`) terminalni oching (yoki shu yerdagi terminaldan foydalaning) va quyidagi buyruqlarni ketma-ket yozing:

```bash
# 1. Gitni ishga tushirish
git init

# 2. Barcha fayllarni qo'shish
git add .

# 3. O'zgarishlarni saqlash (commit)
git commit -m "Initial commit"

# 4. Asosiy novdani (branch) to'g'irlash
git branch -M main

# 5. Repozitoriyga ulash (havolani o'zgartiring!)
# DIQQAT: Quyidagi havolani o'zingiz yaratgan repozitoriy havolasiga almashtiring
git remote add origin https://github.com/azizmagnat/ahd_advocate_bot.git

# 6. GitHubga yuklash
git push -u origin main
```

## Muammo bo'lsa (GitHub Desktop)

Agar terminal qiyin bo'lsa, [GitHub Desktop](https://desktop.github.com/) dasturini yuklab oling:
1.  Dasturni oching va **File -> Add local repository** tanlang.
2.  Bizning loyiha papkasini tanlang (`deep-void`).
3.  **Publish repository** tugmasini bosing.
