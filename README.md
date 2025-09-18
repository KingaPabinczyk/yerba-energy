# Mini Shop

Prosty sklep internetowy zbudowany w Pythonie przy użyciu Flask, Jinja2 i SQLAlchemy.

---

## Wymagania

- Python 3.10+

- Docker (jeśli chcesz uruchomić w kontenerze)

- Git

---

## Uruchomienie lokalnie (bez Dockera)

1. Sklonuj repozytorium:

git clone https://github.com/twoj_user/twoj_projekt.git
cd twoj_projekt

2. Utwórz i aktywuj wirtualne środowisko:

python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

3. Zainstaluj wymagane pakiety:

pip install -r requirements.txt

4. Uruchom aplikację:

python run.py

5. Otwórz przeglądarkę i przejdź pod adres:
   
http://127.0.0.1:5000

## Uruchomienie przy użyciu Dockera

1. Zbuduj obraz Dockera:

docker build -t mini-shop .

2. Uruchom kontener:

docker run -p 5000:5000 mini-shop

3. Otwórz przeglądarkę i przejdź pod adres:

http://127.0.0.1:5000

Struktura projektu

-app/
-- static/ # pliki statyczne (obrazy)
-- templates/ # szablony Jinja2
-- forms.py # definicje formularzy Flask-WTF
-- models.py # definicje modeli SQLAlchemy
-- routes.py # widoki i logika aplikacji

-data/
-- mini_shop.db # plik z bazą SQLite

-Dockerfile
-requirements.txt
-run.py # punkt startowy aplikacji

