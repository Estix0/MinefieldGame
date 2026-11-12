from .minefield import Minefield

async def setup(bot):
    await bot.add_cog(Minefield(bot))
