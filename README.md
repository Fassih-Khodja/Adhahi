I missed the first registration period for odhiya, and now it is very difficult to find one. I have to check the website constantly to see if any have been added, and that is a lot. That is why I created this bot.

Adhahi wilaya watcher

This script polls the Adhahi wilaya availability endpoint and sends a Telegram message when any availability changes.

Setup

1) Install dependencies

   pip install -r requirements.txt

2) Set environment variables

   export TG_BOT_TOKEN="YOUR_BOT_TOKEN"
   export TG_CHAT_ID="1437177618"

   # Optional override:
   export ADHAHI_WILAYAS_URL="https://adhahi.dz/api/v1/public/wilaya-quotas"
   export ADHAHI_STATE_DIR="/path/to/persistent/state"
   export ADHAHI_CONNECT_TIMEOUT="10"
   export ADHAHI_READ_TIMEOUT="40"
   export ADHAHI_MAX_RETRIES="3"
   export ADHAHI_BACKOFF_SECONDS="2"

3) Run

   python adhahi_watch.py

Scheduling (cron)

Every 5 minutes:

   */5 * * * * /usr/bin/python3 /path/to/adhahi_watch.py

GitHub Actions

This repo includes a workflow in .github/workflows/adhahi-watch.yml.
Add these secrets in your GitHub repository:

- TG_BOT_TOKEN
- TG_CHAT_ID
- ADHAHI_WILAYAS_URL (optional)

The workflow uses the GitHub Actions cache to persist state between runs.
