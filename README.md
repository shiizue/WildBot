# 🦌 About WildBot
---
WildBot is a Discord bot that uses the [iNaturalist API](https://api.inaturalist.org/v1/docs/) to send random wildlife observation images for any given animal from iNaturalist's database.

## 🛠️ Built With

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat&logo=python&logoColor=white) ![discord.py](https://img.shields.io/badge/discord.py-2.0+-5865F2?style=flat&logo=discord&logoColor=white) ![iNaturalist API](https://img.shields.io/badge/iNaturalist-API-74AC00?style=flat)

## 📝 How it Works:
---
1. User searches for an animal by sending a Discord message with a command: `!animal goat`
2. Bot searches animal taxa in [iNaturalist](https://api.inaturalist.org/v1/taxa) to find taxon IDs matching searched animal
3. Resulting taxon IDs are ranked by best match to the original search term, prioritizing exact common name matches. The first ID result when searching for the original animal is used as a fallback.
4. A random observation within 100 returned ID search results is chosen.
5. Bot sends a message to Discord with the observation photo, link to the observation's page, and metadata using rich embeds.
# 🎮 Commands
---
- **`!animal [animal_name]`** - Sends a random observation photo of any animal species from iNaturalist's database using embeds. Includes common name, scientific name, location, date, observer, and link to original iNaturalist page for the observation.
  
![Example usage of !animal command](https://media.licdn.com/dms/image/v2/D562DAQH4VRjGXDq57g/profile-treasury-image-shrink_8192_8192/B56ZwRcVyQJIAg-/0/1769819168390?e=1770426000&v=beta&t=-vHu6vhQloSh84p8RfWS0lc_QEcWMP_GrI6OaTBMfEc)

- **`!deer`** - Fun shortcut command for deer observations specifically

- **`!taxonhelp [animal_name]`** - Search taxonomy database and get scientific names for a given animal to provide suggestions for more accurate or specific searches.

![Example usage of taxonhelp command](https://media.licdn.com/dms/image/v2/D562DAQHDNw3SqwxCNA/profile-treasury-image-shrink_1920_1920/B56ZwRcm1bJIAc-/0/1769819238047?e=1770426000&v=beta&t=VKGxjHlgZvg6G1Xp0G8xBmkkNmevaGloZA3l_Lh2Hko)

# 🚀 Local Setup Instructions
---
### 1. Clone the repository

```bash 
git clone https://github.com/shiizue/wildbot.git cd wildbot 
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a Discord Bot

1. Visit the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and name it
3. Go to the "Bot" tab and click "Add Bot"
4. Enable **Message Content Intent** under **Privileged Gateway Intents**.
5. Copy your bot token

### 4. Create a `.env` file with your Discord bot token

```
   DISCORD_TOKEN=your_token_here
```

No API key is needed for iNaturalist's API since it is public and does not require authentication.
### 5. Invite WildBot to your server

1. In the Developer Portal, go to "OAuth2" → "URL Generator"
2. Select scopes: `bot` 
3. Select permissions: `Send Messages`, `Embed Links`, `Attach Files`, `Read Message History` 
4. Copy and visit the generated link to invite the bot

### 6. Run the bot

```bash
python bot.py
```

You should see `Logged in as WildBot#1234`

# 🎯 Roadmap
---
- [ ] Add error handling and comprehensive logging
- [ ] Implement caching to reduce API calls
- [ ] Create "favorite animals" feature for a user to save a list of their favorite animals and return random observations only within that list
- [ ] Add "random animals" command for a completely random animal observation
- [ ] Add filtering observations by location
