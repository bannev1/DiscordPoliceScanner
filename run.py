import os
import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv
import feedparser

# Load your token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Replace this with your specific news RSS feed URL
# Example: Google News World Section
RSS_FEED_URL = "https://google.com"

# Replace this with the exact channel ID where the bot should post news
# (Enable Developer Mode in Discord, right-click a channel, and choose 'Copy Channel ID')
NEWS_CHANNEL_ID = 123456789012345678 

# Initialize bot with default intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Global variable to track the last sent article
last_sent_url = None

@bot.event
async def on_ready():
	print(f'Logged in as {bot.user.name} ({bot.user.id})')
	# Start the automated news check loop
	check_news_loop.start()

# Runs every 60 minutes. You can also use minutes=30 or seconds=10 for testing.
@tasks.loop(hours=1)
async def check_news_loop():
	global last_sent_url
	
	# Wait until the bot is completely connected
	await bot.wait_until_ready()
	channel = bot.get_channel(NEWS_CHANNEL_ID)
	
	if not channel:
		print(f"Error: Could not find channel with ID {NEWS_CHANNEL_ID}")
		return

	try:
		# Parse the RSS feed
		feed = feedparser.parse(RSS_FEED_URL)
		
		# Ensure the feed has entries
		if not feed.entries:
			return
			
		latest_entry = feed.entries[0]
		latest_url = latest_entry.link

		# If it's a brand new article, send it to Discord
		if latest_url != last_sent_url:
			# We don't want to spam the channel on the very first boot
			if last_sent_url is not None:
				title = latest_entry.title
				summary = latest_entry.get('summary', 'No description available.')
				
				# Create a visually clean Discord Embed
				embed = discord.Embed(
					title=title, 
					url=latest_url, 
					description=summary[:300] + "...", # Truncate description if too long
					color=discord.Color.blue()
				)
				if 'published' in latest_entry:
					embed.set_footer(text=f"Published: {latest_entry.published}")
				
				await channel.send(content="📰 **Latest News Update:**", embed=embed)
			
			# Update the tracker with the newest link
			last_sent_url = latest_url

	except Exception as e:
		print(f"Error fetching news: {e}")

# Run the bot
bot.run(TOKEN)
