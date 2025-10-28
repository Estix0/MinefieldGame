from redbot.core import commands, Config
import discord
import random
import datetime

class Minefield(commands.Cog):
    """
    Every time you send a message in the designated channel, you have a 1/100 chance to explode.
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2710251800, force_registration=True) # Uwaga: tutaj brakowało identyfikatora
        self.config.register_member(
            current_score=0, 
            high_score=0, 
            times_exploded=0
        )
        self.config.register_guild(
            minefield_channel=None,
            explosion_chance=100
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        minefield_channel_id = await self.config.guild(message.guild).minefield_channel()
        
        if not minefield_channel_id or message.channel.id != minefield_channel_id:
            return

        member = message.author

        explosion_chance = await self.config.guild(message.guild).explosion_chance() 

        roll = random.randint(1, explosion_chance)

        if roll == 1:
            duration = datetime.timedelta(minutes=10)
            reason = "Stepped on a mine in the minefield."
            try:
                await member.timeout(duration, reason=reason)
            except (discord.Forbidden, discord.HTTPException):
                pass 

            user_data = await self.config.member(member).all()
            current = user_data["current_score"]
            high = user_data["high_score"]
            exploded = user_data["times_exploded"]

            new_high_score = max(current, high)
            
            await self.config.member(member).current_score.set(0)
            await self.config.member(member).high_score.set(new_high_score)
            await self.config.member(member).times_exploded.set(exploded + 1)

            embed = discord.Embed(
                title="Explosion!", 
                description=f"{member.mention} stepped on a mine and received a 10-minute timeout.", 
                color=discord.Color.red()
            )
            embed.add_field(name="Final Score", value=f"**{current}**", inline=True)
            embed.add_field(name="Explosions", value=f"**{exploded + 1}**", inline=True)
            
            if new_high_score > high:
                embed.set_footer(text=f"New high score! Previous record: {high}.")
            else:
                embed.set_footer(text=f"Your high score remains {high}.")
                
            await message.channel.send(embed=embed)

        else:
            current_score = await self.config.member(member).current_score()
            await self.config.member(member).current_score.set(current_score + 1)
            

    @commands.group(name="minefield", aliases=["mf"])
    async def minefield(self, ctx):
        """Main command for the minefield game."""

    @commands.admin_or_permissions(manage_guild=True)
    @minefield.command(name="setchannel")
    async def setminefieldchannel(self, ctx, channel: discord.TextChannel):
        """Sets the minefield channel."""
        await self.config.guild(ctx.guild).minefield_channel.set(channel.id)
        embed = discord.Embed(
            title="Minefield Channel Set", 
            description=f"The minefield game channel has been set to {channel.mention}", 
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.admin_or_permissions(manage_guild=True)
    @minefield.command(name="setchance")
    async def set_explosion_chance(self, ctx, chance: int):
        """Sets the explosion chance (100 means 1/100)."""
        
        if chance < 2:
            await ctx.send("The chance must be an integer greater than or equal to 2.")
            return

        await self.config.guild(ctx.guild).explosion_chance.set(chance)
        
        embed = discord.Embed(
            title="Chance Changed", 
            description=f"The explosion chance has been set to **1 in {chance}**.", 
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

    @minefield.command(name="stats")
    async def stats(self, ctx, member: discord.Member = None):
        """
        Displays your stats (or another user's).
        
        If no user is provided, it will display your own stats.
        """
        if member is None:
            member = ctx.author
            
        user_data = await self.config.member(member).all()
        current_score = user_data["current_score"]
        high_score = user_data["high_score"]
        times_exploded = user_data["times_exploded"]

        embed = discord.Embed(
            title=f"Minefield Stats: {member.display_name}", 
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.display_avatar)
        embed.add_field(name="Current Score", value=f"**{current_score}**", inline=True)
        embed.add_field(name="High Score", value=f"**{high_score}**", inline=True)
        embed.add_field(name="Explosions", value=f"**{times_exploded}**", inline=True)
        
        await ctx.send(embed=embed)

    @minefield.command(name="leaderboard", aliases=["lb"])
    async def leaderboard(self, ctx):
        """Print leaderboard."""
        
        all_member_data = await self.config.all_members(ctx.guild)
        
        stats_list = []
        for member_id, data in all_member_data.items():
            member = ctx.guild.get_member(member_id)
            if member and not member.bot:
                stats_list.append((member, data["high_score"], data["times_exploded"]))

        sorted_high_score = sorted(stats_list, key=lambda x: x[1], reverse=True)
        sorted_high_score = [entry for entry in sorted_high_score if entry[1] > 0][:5]
        
        hs_text = ""
        for i, (member, high_score, _) in enumerate(sorted_high_score):
            hs_text += f"**{i+1}. {member.display_name}**: **{high_score}**\n"
        
        if not hs_text:
            hs_text = "No high scores yet."

        sorted_exploded = sorted(stats_list, key=lambda x: x[2], reverse=True)
        sorted_exploded = [entry for entry in sorted_exploded if entry[2] > 0][:5]

        ex_text = ""
        for i, (member, _, times_exploded) in enumerate(sorted_exploded):
            ex_text += f"**{i+1}. {member.display_name}**: **{times_exploded}**\n"

        if not ex_text:
            ex_text = "Nobody has exploded yet."

        embed = discord.Embed(title="Minefield Leaderboard", color=discord.Color.gold())
        embed.add_field(name="Top 5 High Scores", value=hs_text, inline=False)
        embed.add_field(name="Top 5: Most Explosions", value=ex_text, inline=False)

        await ctx.send(embed=embed)
