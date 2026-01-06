### 🧮 Pifagor Matematika Test Bot (Django + Aiogram)

Bul proekt matematika páninen testlerdi avtomatlastırılǵan túrde ótkeriw ushın móljellengen Telegram bot hám Admin API platformasy. Sistema úlken kólemdegi maǵlıwmatlar (Massive Data) menen islesiwge hám joqarı turaqlılıqqa (High Reliability) baǵdarlanǵan.

### 🚀 Tiykarǵı Imkaniyatları

* Telegram Bot: Registratsiya, tosınnan 10 soraw saylaw (tákrarlanıwsız), qáteler analizi hám jeke statistika.
* Persistent Storage: FSM (yad) PostgreSQL-de saqlanadı — bot restart bolsa da oqıwshı jaǵdayı joǵalmaydı.
* Admin API (DRF): JWT autentifikaciya, Sorawlar CRUD, Oqıwshılar dizimi hám Dashboard.
* Smart Import: Excel hám súwretlerdi .zip arxiv arqalı toplap júklew.
* Dockerized: Nginx, Gunicorn hám PostgreSQL konteynerleri arqalı turaqlı deploy.

### 🛠 Texnikalıq Stek

* Backend: Django 5.x, Django REST Framework
* Bot: Aiogram 3.x (Asynchronous)
* Baza: PostgreSQL 15
* Server: Nginx, Gunicorn, Docker Compose

### 💻 Lokal iske túsiriw (Docker)

1. Proektti klon qılıw: 
   * git clone https://github.com/siziń_username/math-test-bot.git cd math-test-bot
2. .env faylın tayarlaw 

    Proektıń bas papkasında .env faylın ashıń hám mınanı jazıń:

    SECRET_KEY='siziń_jasırın_kodińiz'
    
    DEBUG=True

    DB_NAME=math_bot_db

    DB_USER=postgres

    DB_PASSWORD=sizdin_paroliz

    DB_HOST=db

    DB_PORT=5432

    BOT_TOKEN=712345678:siziń_bot_tokenińiz
3. Docker-di iske túsiriw

    docker-compose up --build -d

4. Admin (Superuser) jaratıw
    docker-compose exec web python manage.py createsuperuser


### 📊 Excel & ZIP Import


Qollanbası Adminler sorawlar bazasın toplap júklewi ushın tómendegi formattaǵı Excel   kestesin tayarlawı hám onı súwretler menen birge ZIP arxivine salıwı kerek.

### 📋 Excel Keste Sxemasy (questions.xlsx)

| | A (text) | B (option_a) | C (option_b) | D (option_c) | E (option_d) | F (correct) | G (image) |
|:---:|:---|:---|:---|:---|:---|:---:|:---|
| **1** | **Soraw teksti** | **A varianti** | **B varianti** | **C varianti** | **D varianti** | **Duris** | **Suwret ati** |
| **2** | 120 / 4 = ? | 20 | 30 | 40 | 50 | b | |
| **3** | Mısaldı sheshiń: | 12 | 15 | 18 | 20 | a | **misal_1.png** |
| **4** | x-dı tabıń: | 5 | 8 | 10 | 12 | c | **formula.jpg** |


⚠️ Import Qaǵıydaları:

1. Durıs juwap (Column F): Tek kishi latın háriplerinde jazıń: a, b, c yamasa d.
2. Súwret (Column G): Eger soraw súwretli bolsa, súwret faylınıń anıq atın (mısalı: formula.jpg) jazıń. Súwret bolmasa, bos qaldırıń.
3. ZIP Arxiv: questions.xlsx faylın hám barlıq súwretlerdi bir ZIP arxivine salıń. 
Itibarlı bolıw kerek: Fayllar papka ishinde emes, arxivtiń eń basında (root) bolıvı shárt.

### 🔍 API Dokumentaciya (Quick View)

| Endpoint | Method | Túsindirme |
| :--- | :--- | :--- |
| `/api/token/` | **POST** | JWT Access/Refresh token alıw |
| `/api/admin/questions/` | **GET/POST** | Sorawlar dizimi hám jańa soraw qosıw |
| `/api/admin/import-questions/` | **POST** | ZIP Import (Excel hám súwretlerdi toplap júklew) |
| `/api/admin/dashboard/` | **GET** | Ulıwma statistika (Admin Dashboard) |
| `/api/admin/attempts/` | **GET** | Test tapsırǵan oqıwshılar nátiyjeleri dizimi |
| `/api/admin/users/` | **GET** | Bot paydalanıwshıları dizimi |

### 🛠 Servislerdi basqarıw
Logları kóriw: docker-compose logs -f

Botty toqtatıw: docker-compose stop bot

Sistemany tazalaw: docker-compose down -v