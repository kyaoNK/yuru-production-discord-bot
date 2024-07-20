from discord import Intents, AutoShardedClient

intents = Intents.default()
intents.message_content = True
intents.members = True
yuru_discord_client = AutoShardedClient(intents=intents, shard_count=2)