""" welcome members cog (to be tested)
async def on_join(self, member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"Welcome to the server, {member.mention}!")
"""