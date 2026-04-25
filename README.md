# 🚀 ISS Transit Bot

Questo progetto invia ogni giorno su Telegram un report con i possibili transiti della Stazione Spaziale Internazionale (ISS) davanti al Sole o alla Luna vicino alla tua posizione.

## 📱 Cosa fa

* Controlla ogni giorno automaticamente
* Analizza i prossimi giorni (configurabile)
* Cerca transiti entro un raggio in km
* Ti invia un messaggio Telegram
* Mostra:

  * data e ora
  * durata del transito
  * tipo (centrale, interno, bordo)
  * distanza dalla tua posizione
  * punto su mappa

---

## ⚙️ Requisiti

* Account GitHub
* Account Telegram

---

## 🔧 Setup (5 minuti)

### 1. Copia il progetto

Premi **Fork** in alto a destra oppure copia il repository.

---

### 2. Crea il bot Telegram

Apri Telegram e cerca:

@BotFather

Scrivi:

/newbot

Segui le istruzioni e salva il **token**.

---

### 3. Trova il tuo chat ID

Apri il bot e premi **Start**.

Poi apri questo link nel browser:

https://api.telegram.org/botTUO_TOKEN/getUpdates

Cerca:

"chat":{"id":123456789

Quel numero è il tuo **CHAT_ID**.

---

### 4. Aggiungi i secrets su GitHub

Vai nel repo:

Settings → Secrets and variables → Actions → New repository secret

Aggiungi:

TELEGRAM_BOT_TOKEN → il token del bot
TELEGRAM_CHAT_ID → il tuo chat id

---

### 5. Configura la tua posizione

Apri il file:

config.json

E modifica:

```json
{
  "users": [
    {
      "name": "Il tuo nome",
      "lat": 45.4642,
      "lon": 9.1900,
      "radius_km": 40,
      "grid_step_km": 5,
      "search_hours": 72
    }
  ]
}
```

Puoi trovare lat/lon da Google Maps.

---

### 6. Avvia il bot

Vai su:

Actions → Daily ISS Transit Platform → Run workflow

Se tutto funziona riceverai un messaggio Telegram.

---

## ⏰ Automazione

Il bot gira automaticamente ogni giorno alle 07:00 (ora italiana).

---

## 🔐 Sicurezza

⚠️ Non condividere mai:

* TELEGRAM_BOT_TOKEN
* TELEGRAM_CHAT_ID

Sono salvati nei GitHub Secrets e non sono visibili nel codice.

---

## 🧠 Note

* I transiti sono rari: è normale non ricevere eventi per giorni
* Il sistema analizza anche zone entro un raggio configurabile
* La precisione è circa al secondo

---

## 🚀 Possibili miglioramenti

* Interfaccia web per configurazione
* Supporto multi-utente
* App iPhone

---

Buon divertimento ✨
