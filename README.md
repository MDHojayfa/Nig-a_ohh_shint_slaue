# Nig-a_ohh_shint_slaue
Ultimate powered ohsint slaue with 0 cast

# 🔍 Ultimate OSINT Tool (Social Media Intelligence)

> Powerful and interactive Open Source Intelligence (OSINT) tool for Facebook, Instagram, Twitter, and Reddit.  
> Designed to run seamlessly on **Linux** and **Termux (Android)** with zero compromises.  

---

## 🚀 Features

- ✅ Platform selector (FB, IG, Twitter, Reddit)
- ✅ Auto dependency checker with size display and permission prompt
- ✅ Cool CLI animations and themed text
- ✅ Modular and extensible API scraping engine
- ✅ Runs smoothly on Termux & Linux
- ✅ Exports structured data to JSON

---

## 📲 Platforms Supported

| Platform  | Method Used              | Status       |
|-----------|--------------------------|--------------|
| Facebook  | Graph API, Scraping      | ✅ Complete   |
| Instagram | Osintgram, Scraping      | ✅ Complete   |
| Twitter   | Twint (no API needed)    | ✅ Complete   |
| Reddit    | PRAW (Reddit API)        | ✅ Complete   |

---

## 🧰 Requirements

- Python 3.10+
- Git
- Termux / Linux shell
- Internet connection
- Optional: Tor or VPN (for stealthy use)

---

## 🔧 Installation

### 📱 Termux (Android)

```bash
pkg update && pkg upgrade
pkg install git python -y
git clone https://github.com/yourusername/ultimate-osint-tool.git
cd ultimate-osint-tool
python osint_tool.py
```

### 💻 Linux

```bash
sudo apt update && sudo apt install git python3 -y
git clone https://github.com/yourusername/ultimate-osint-tool.git
cd ultimate-osint-tool
python3 osint_tool.py
```

---

## 🧪 First Run Setup

On first run, the tool will:

1. Check for all required dependencies
2. Show the size of each package
3. Ask your permission to install them
4. Show cool animations while installing
5. Start the OSINT wizard

---

## 🕵️ Usage Guide

1. Launch the tool:
   ```bash
   python osint_tool.py
   ```

2. Select a platform: `Facebook`, `Instagram`, `Twitter`, `Reddit`

3. Enter the **username or profile link**

4. Let the tool collect:
   - Public details
   - Post metadata
   - Bio, friends/followers
   - Related images or links
   - And more...

5. Export or view the result in:
   - Pretty console format
   - JSON file for advanced analysis

---

## 📁 Output Example

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

## 👨‍💻 Developer Mode

To add your own platform:

1. Go to `platforms/` folder  
2. Add a file: `yourplatform.py`  
3. Create a function: `def fetch_data(username):`  
4. Register it in `osint_tool.py`

---

## 🔒 Legal Disclaimer

> This tool is for **educational** and **ethical hacking** purposes only.  
> Unauthorized use of this tool against accounts or networks you do not own is illegal.  
> You are responsible for your actions.

---

## 🧊 Want to contribute?

- Fork the repo
- Create your feature branch (`git checkout -b feature/xyz`)
- Commit your changes (`git commit -m 'Add xyz'`)
- Push and make a pull request!

---

## 📮 Contact

For bugs or requests, open an [Issue](https://github.com/yourusername/ultimate-osint-tool/issues) or DM me on Telegram: `@yourhandle`

---

## ⭐ Star This Repo

If you find this project useful, don't forget to ⭐ the repo and share with your cyber friends!
