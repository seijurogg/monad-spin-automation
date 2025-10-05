Monad Spin Bot is an advanced automation script built with Python and Playwright that interacts with the Monad Spin MiniApp https://farcaster.xyz/miniapps/TLIZwXHJazk2/monad-spin on farcaster.xyz
.
It automatically navigates the app, performs spins, tracks results, and confirms wallet transactions — with colorful logs and safe shutdown handling.

✨ Features

🔹 Automatic navigation to Monad Spin on Farcaster

🔹 Smart Testnet switching when required

🔹 Automated spin cycle with result parsing

🔹 Wallet confirmation through Farcaster mini-app modal

🔹 Colorful real-time logs (colorama)

🔹 Graceful shutdown support

🔹 Win/loss tracking and total winnings summary

⚙️ Requirements

Python 3.10+

Install dependencies:

pip install -r requirements.txt


Install Playwright browsers:

playwright install

⚠️ Important Setup Notes

Before running the bot:

Use a clean browser profile.
Do not use your main everyday browser profile.
For example:

If you normally use Chrome, create a new Brave or other browser for the bot.

This prevents cookie/session conflicts and keeps your main browser safe.

Log in to Farcaster manually in that clean browser profile before running the bot.

Visit https://farcaster.xyz

Make sure you’re logged in and can open Monad Spin manually once.

Confirm your wallet connection on your mobile Farcaster app when prompted.
The bot cannot bypass wallet authorization — you must confirm transactions from your phone.

Set up your environment variables (see below).

🔧 Environment Variables

Create a .env file in the project root:

COMET_USER_DATA_DIR = "C:\\Users\\name\AppData\\Local\\Perplexity\\Comet\\User Data"
COMET_EXECUTABLE_PATH = "C:\\Users\\name\AppData\\Local\\Perplexity\\Comet\\Application\\comet.exe"


These define:

COMET_EXECUTABLE_PATH — full path to the browser executable (Chrome/Brave/) for bot.

COMET_USER_DATA_DIR — path to the user data directory that stores your Farcaster session.

🚀 Usage

Run the bot:

python monad_spin.py


What happens:

Launches your chosen browser (with your Farcaster login).

Navigates to Monad Spin.

Closes popups and switches to Monad Testnet (if needed).

Starts the automated spin cycle.

Logs every step, win/loss, and transaction.

You can stop the bot safely anytime with Ctrl + C.

🧩 Project Structure
.
├── monad_spin.py        # Main bot script
├── .env                 # Browser + user data configuration
├── requirements.txt     # Dependencies
└── README.md            # Documentation

🧪 Example Output
➤ Starting Monad Spin bot...
✓ Browser launched successfully
➤ Navigating to farcaster.xyz...
✓ Page loaded successfully
🎰 Spin #1/10 | Wins: 0 | Losses: 0
🎉 WIN! Total wins: 1
💰 Prize: 0.00001 WBTC
💰 Current balance:
   WBTC: 0.00001
⏳ Waiting 8s before next spin...

🧠 Tips

Keep the browser window visible — do not minimize it.

If the bot can’t find a button, it will skip and retry.

Randomized delays make it behave more human-like.

⚠️ Disclaimer

This project is for educational and testing purposes only.
Automating web interactions may violate platform terms of service — use responsibly.
