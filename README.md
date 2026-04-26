# 🚀 ISS Transit Platform

Trova automaticamente i transiti della Stazione Spaziale Internazionale (ISS) davanti al Sole ☀️ o alla Luna 🌙 vicino alla tua posizione e ricevi tutto direttamente su Telegram.

---

## 🧠 Cos'è

ISS Transit Platform è un sistema automatico che:

GitHub Actions → Python (calcoli astronomici avanzati) → ISS + Sole + Luna → analisi su area (fino a 40 km) → rilevamento transiti reali → notifica su Telegram

---

## 🍴 Usa il progetto (fork)

Per usare questo bot devi prima copiarlo nel tuo account GitHub.

### Metodo consigliato

1. Clicca su Fork in alto a destra
2. Seleziona il tuo account
3. Attendi la creazione del repository

👉 Ora hai una copia tua del progetto e puoi modificarlo liberamente.

---

## ✨ Funzionalità

- 📡 Calcolo posizione ISS, Sole e Luna (Skyfield)
- 🎯 Ricerca transiti reali (non solo passaggi)
- 🌍 Analisi su area (non solo punto singolo)
- ⏱ Precisione fino al secondo
- 📏 Durata del transito
- 🧭 Traiettoria sul disco (centro / interno / bordo)
- 📬 Notifica automatica ogni giorno su Telegram
- 📱 Web app con mappa e GPS per configurazione

---

## 📁 Struttura

iss-transit-platform ├─ send_telegram.py        ← motore principale ├─ config.json             ← configurazione utente ├─ app/ │  └─ index.html           ← web app (mappa + GPS) └─ .github/workflows/    └─ daily.yml            ← automazione giornaliera

---

## ⚙️ Setup (5 minuti)

### 1. 🤖 Crea bot Telegram

Apri Telegram e cerca:

@BotFather

Poi:

/newbot

Salva il token → sarà TELEGRAM_BOT_TOKEN

---

### 2. 🆔 Ottieni chat ID

Apri nel browser:

https://api.telegram.org/botTUO_TOKEN/getUpdates

Trova:

json "chat": {   "id": 123456789 } 

👉 quello è il tuo TELEGRAM_CHAT_ID

---

### 3. 🔐 GitHub Secrets

Nel tuo repository (fork), vai su:

Settings → Secrets → Actions

Aggiungi:

TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID

---

### 4. 📍 Configura posizione (facile)

Apri la web app:

app/index.html

Oppure tramite GitHub Pages.

Poi:

1. clicca sulla mappa oppure usa GPS
2. premi Genera config
3. premi Copia
4. apri config.json su GitHub
5. incolla
6. commit

---

## 🔧 config.json

Esempio:

json {   "users": [     {       "lat": 46.2465,       "lon": 9.0245,       "radius_km": 40,       "grid_step_km": 5,       "search_hours": 24     }   ] } 

---

## ▶️ Avvio

### Manuale

Actions → Run workflow

---

### Automatico

Ogni giorno:

cron: "0 5 * * *"

👉 circa:
- 07:00 estate
- 06:00 inverno

⚠️ GitHub può ritardare di qualche minuto (normale)

---

## 📬 Output Telegram

Riceverai:

- ✔ messaggio ogni giorno
- ✔ anche se non ci sono eventi
- ✔ dettagli completi se ci sono transiti:

🔹 Evento Oggetto: Sole Tipo: centrale Durata: 0.8 s Distanza: 12 km Mappa: link

---

## 🧭 Web App

Funzionalità:

- 🗺️ mappa interattiva
- 📍 GPS automatico
- 📋 copia config
- 📥 download config.json
- 🔗 link diretto a GitHub

---

## 🔐 Sicurezza

✔ nessun token nel codice  
✔ uso GitHub Secrets  
✔ nessun server  
✔ tutto gira su GitHub  

---

## 🧠 Note

- I transiti ISS sono rari
- È normale ricevere molti “nessun evento”
- Il sistema analizza una zona, non un punto
- Precisione dipende da TLE e step temporali

---

## 🚀 Roadmap

- [ ] miglioramento UI web app
- [ ] mappa con area visuale
- [ ] supporto multi-utente
- [ ] app Mac standalone

---

## 🧾 In breve

> Un sistema automatico che trova transiti ISS reali  
> e li trasforma in notifiche Telegram utilizzabili da chiunque  
> senza server e senza costi.

---

## 📜 Licenza

Progetto personale / astronomia amatori
