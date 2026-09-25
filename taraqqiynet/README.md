# TaraqqiyNET

O'quvchilarning bilim darajasini (Ingliz tili — IELTS/CEFR, Matematika) aniqlaydigan va
hududlar kesimida statistika yig'adigan platforma.

## Tizim qanday ishlaydi

- **Kirish sahifasi** (`/`) — Programmer.uz uslubidagi qorong'i dizayn. Login/parol kiritilib,
  tasdiqlangandan so'ng foydalanuvchi **"Bo'lim tanlash"** sahifasiga (`/dashboard/`) tushadi —
  u yerda O'quvchi / Markaz / Admin variantlari ko'rinadi, faqat o'z roliga mos bo'lim faol bo'ladi.
- **O'quvchi** (`/student/`) — fan tanlaydi (Ingliz tili yoki Matematika), 10 ta tasodifiy savoldan
  iborat testni topshiradi, natijada foiz va CEFR/daraja hamda hududidagi markazlar ro'yxatini ko'radi.
- **Markaz** (`/center/`) — o'z hududidagi o'quvchilar natijalari va darajalar bo'yicha taqsimotni ko'radi.
- **Admin** (`/admin-panel/`) — barcha hududlar bo'yicha o'rtacha ball, qaysi hudud yordamga muhtojligini
  ko'rsatadigan anonim/agregatlangan statistika.
- **Django admin** (`/admin/`) — savollar banki, foydalanuvchilar, hududlarni boshqarish uchun.

## Mahalliy ishga tushirish

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data      # demo hudud/fan/savollarni yuklaydi
python manage.py createsuperuser --username admin   # keyin rolini admin qiling (pastga qarang)

python manage.py runserver
```

Superuser yaratilgandan keyin uning `role` maydonini admin qilish uchun:

```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model
u = get_user_model().objects.get(username='admin')
u.role = 'admin'
u.save()
"
```

Saytni ochish: http://127.0.0.1:8000/

## Render.com'ga deploy qilish

1. Loyihani GitHub'ga yuklang (yangi repo yarating, shu papkani push qiling).
2. [render.com](https://render.com) da **New + → Web Service** tanlang, GitHub repongizni ulang.
3. Sozlamalar:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn taraqqiynet.wsgi:application`
4. **Environment** bo'limida quyidagi o'zgaruvchilarni qo'shing:
   - `SECRET_KEY` — istalgan uzun tasodifiy satr
   - `DEBUG` — `False`
   - `ALLOWED_HOSTS` — Render bergan domenni avtomatik qo'shadi (`RENDER_EXTERNAL_HOSTNAME`), qo'shimcha domen kerak bo'lsa shu yerga vergul bilan yozing
5. Render'da **PostgreSQL** database yarating (bepul tier), uning "Internal Database URL" manzilini
   nusxalab, web service environment'ga `DATABASE_URL` nomi bilan qo'shing.
6. Deploy tugagach, Render "Shell" orqali bir marta ishga tushiring:
   ```bash
   python manage.py seed_data
   python manage.py createsuperuser
   ```

## Keyingi qadamlar (rejadagi kengaytirish)

- SAT fanini qo'shish (Subject modeliga yangi yozuv + savollar banki)
- Savollar sonini ko'paytirish (hozircha demo uchun 24 ta savol bor)
- Markaz uchun batafsilroq analitika (vaqt bo'yicha dinamika, eksport)
- SMS/parol tiklash, email tasdiqlash
