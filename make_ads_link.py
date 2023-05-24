import urllib.parse

bot_username = "YourBotUsername"
payload = "ads_helo"

# URL encode the payload
encoded_payload = urllib.parse.quote_plus(payload)

deep_link = f"https://t.me/{bot_username}?start={encoded_payload}"

print(deep_link)
