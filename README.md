# Nig-a_ohh_shint_slaue

> ⚡ Ultimate cross-platform OSINT slaue with 0 cast – fast, modular & blazing 🔥

---

## 🔍 Ultimate OSINT Tool (Social Media Intelligence)

Powerful and interactive Open Source Intelligence (OSINT) tool for:
- Facebook
- Instagram
- Twitter (X)
- Reddit

🖥️ Runs perfectly on **Linux** and **Termux (Android)** – no compromises, no paid API keys!

---

## 🚀 Features

- ✅ Select platform (FB, IG, Twitter, Reddit)
- ✅ Auto dependency checker with size and permission prompts
- ✅ Cool CLI animations + themed text
- ✅ Modular scraping & API engine
- ✅ JSON export support
- ✅ Lightweight, fast & 100% free

---

## 📲 Supported Platforms

| Platform  | Method Used           | Status      |
|----------|------------------------|-------------|
| Facebook | Graph API, scraping    | ✅ Done      |
| Instagram| Osintgram + scraping   | ✅ Done      |
| Twitter  | Twint (no API needed)  | ✅ Done      |
| Reddit   | PRAW (Reddit API)      | ✅ Done      |

---

## 🧰 Requirements

- Python 3.10+
- Git
- Termux or Linux shell
- Internet connection 🌐
- (Optional) VPN / Tor for stealth mode 🕶️

---

## 🔧 Installation

### 📱 Termux (Android)

```bash
pkg update && pkg upgrade
pkg install git python -y
git clone https://github.com/yourusername/Nig-a_ohh_shint_slaue.git
cd Nig-a_ohh_shint_slaue
python osint_tool.py
```

### 💻 Linux

```bash
sudo apt update && sudo apt install git python3 -y
git clone https://github.com/yourusername/Nig-a_ohh_shint_slaue.git
cd Nig-a_ohh_shint_slaue
python3 osint_tool.py
```

---

## ⚙️ First Time Setup Instructions

On the first run:
1. All dependencies will be checked ✅
2. You’ll see required sizes 📦
3. It will ask for your permission ✅
4. Installation with CLI animations 🌀
5. Tool launches with interactive wizard 🚀

---

## 🕵️ How To Use

```bash
python osint_tool.py
```

Then:
- Choose a platform
- Input the username or profile URL
- Let the tool collect:
  - Public info, posts, metadata
  - Friends/followers data
  - Images, captions, links
  - JSON-ready export 📁

---

## 📁 Output Format

```json
{
  "username": "example_user",
  "platform": "Instagram",
  "full_name": "John Doe",
  "followers": 1200,
  "bio": "Security enthusiast | Runner",
  "latest_posts": [
    {"date": "2025-07-30", "likes": 340, "caption": "Hiking again!"}
  ]
}
```

---

## 🔑 Instagram Login Setup

For Instagram functions to work properly, you need to add your account credentials in the `credentials.json` file in the project root.

Example format:

```json
{
  "instagram": {
    "username": "your_instagram_username",
    "password": "your_instagram_password"
  }
}
```

⚠️ **Important:**
- Use a dedicated or dummy account for OSINT purposes if possible.
- Never commit your real credentials to GitHub or share this file.
- This file is only used locally on your machine.

---

## 👨‍💻 Developer Mode

Want to add your own platform module?

1. Go to `platforms/`
2. Create `yourplatform.py`
3. Define:
```python
def fetch_data(username):
    return {...}
```
4. Register it in `osint_tool.py`

---

## 🔒 Legal Note

> 🛑 This tool is for **educational and ethical purposes only**.  
> Do not use against anyone you don’t have legal access to.  
> Use responsibly. You are accountable for your actions.

---

## 💡 Pillow Installation Fix (If You Get Errors)

If you face errors while installing the Pillow library, it's likely due to missing build dependencies or JPEG development libraries.

Follow the instructions below based on your platform:

---

### 🛠️ Termux (Android)

Run the following commands in Termux before installing Pillow:

```bash
pkg update
pkg install python
pkg install clang make libjpeg-turbo libjpeg-turbo-dev zlib zlib-dev freetype freetype-dev libtiff
```

Then upgrade pip and install Pillow:

```bash
pip install --upgrade pip setuptools wheel
pip install Pillow
```

---

### 🐧 Ubuntu/Debian (Reference)

Run the following commands to install required packages:

```bash
sudo apt-get update
sudo apt-get install python3-dev python3-pip build-essential libjpeg-dev zlib1g-dev libfreetype6-dev libtiff-dev
pip3 install Pillow
```

Then re-run the script. Pillow should install and work without errors.

---

## 💥 Contribute Like a Beast

- Fork this repo
- Make your changes
- Push and pull request 🙌

```bash
git checkout -b feature/your-feature
# edit your code
git commit -m "Added awesome feature"
git push origin feature/your-feature
```

---

## 📮 Contact / Report Bugs

Open an issue: https://github.com/MDHojayfa/Nig-a_ohh_shint_slaue/issues  
Telegram: [@urniggar](https://t.me/urniggar)

---

## ⭐ Star This Project

If you love OSINT and hacking tools, give it a star ⭐ and share it with your community!

---

🛠 Built with love ❤️, CLI power ⚡, and zero excuses 🧠
