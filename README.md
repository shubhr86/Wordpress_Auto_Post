# WordPress Auto-Poster

## 📌 Summary
This project is a **WordPress Auto-Poster** that fetches articles from an **RSS feed**, rephrases the content using AI, finds relevant images via **Google Image Search**, and automatically posts them to a **WordPress site**. The script runs on a **GitHub Actions scheduler** and can also be manually triggered.

---

## ✨ Features
✅ **Fetches Articles** – Retrieves articles from an RSS feed.

✅ **AI Rewriting** – Uses AI to rephrase article titles and content for uniqueness.

✅ **Image Search** – Finds relevant images for each article using a search API.

✅ **Auto Posting** – Publishes the article on WordPress automatically.

✅ **Scheduled Execution** – Runs at predefined times using GitHub Actions.

✅ **Manual Trigger Support** – Allows manual execution from GitHub Actions.

✅ **Ensures One Article Per Run** – Posts only one article per execution to avoid spam.

---

## 🔧 Tech Stack Used
- **Python** – Core scripting language
- **Requests** – For fetching articles and interacting with WordPress
- **BeautifulSoup** – For parsing RSS feeds
- **Pyppeteer** – For performing Google Image searches
- **AI API (Together AI)** – For rephrasing content
- **GitHub Actions** – For automation & scheduling

---

## 🚀 How to Use
### 1️⃣ **Fork & Clone the Repository**
```bash
# Clone the repo
git clone https://github.com/shubhr86/Wordpress_Auto_Post.git
cd your-repo
```

### 2️⃣ **Set Up Dependencies**
```bash
pip install -r requirements.txt
```

### 3️⃣ **Configure Environment Variables**
Create a `.env` file (for local testing) or set these as **GitHub Secrets**:
```ini
RSS_FEED_URL=your_rss_feed_url
WP_URL=your_wordpress_site_url
WP_USER=your_wordpress_username
WP_PASS=your_wordpress_password
SERP_API_KEY=your_google_search_api_key
TOGETHER_API_KEY=your_ai_api_key
```

### 4️⃣ **Run the Script Locally**
```bash
python t.py
```

### 5️⃣ **Automate with GitHub Actions**
Modify the `bot.yml` file if needed and push your changes. The workflow will execute at scheduled times and can be triggered manually.

---

## 🛠️ Customization
- Update `RSS_FEED_URL` in GitHub Secrets to change the article source.
- Modify `rephrase_text()` to adjust AI-generated text.
- Adjust the image search logic in `search_image()` to refine image selection.
- Change the **cron schedule** in `.github/workflows/bot.yml` to run at different times.

---

## 🤝 Contributing
Feel free to fork the repo, create a new branch, and submit a **pull request** for any improvements!

---

## 📜 License
This project is licensed under the **MIT License**. See `LICENSE` for details.

---

### 🌟 If you find this project useful, consider giving it a ⭐ on GitHub!


