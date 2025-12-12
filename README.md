# Advanced YouTube Downloader Telegram Bot
A fully functional Telegram bot that allows users to download YouTube videos or audio directly to Telegram as documents. 
Features include:

- Video / Audio selection
- Video quality selection (1080p, 720p, etc.)
- Audio bitrate selection
- 2GB file size alert
- Download progress indication
- 24/7 uptime ready (Replit / Heroku)
- Optional channel join message
1. Clone the repository:
   ```bash
   git clone https://github.com/YourUsername/YourBotRepo.git
   cd YourBotRepo
pip install -r requirements.txt
TOKEN=YOUR_BOT_TOKEN

#### Heroku Deployment
```markdown
1. Push the repository to GitHub.

2. Create a new app on Heroku.

3. Set Config Vars:

4. Deploy from GitHub branch.

5. Open the app and your bot will run 24/7.
- YouTube video/audio download
- Inline selection for video/audio
- Video quality selection
- Audio bitrate selection
- Handles large files up to 2GB
- 24/7 uptime with Flask server
- Channel join message support
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [pytube](https://github.com/pytube/pytube)
- Flask for uptime server
