import lib

class Control(lib.commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @lib.commands.command()
    @lib.commands.is_owner()
    async def reload(self, ctx, module: str):
        try:

            lib.bot.reload_extension(module)
            await ctx.send('Succesfully updated {}'.format(module))

        except Exception as e:
            
            await ctx.send('Error reloading ({})'.format(e))

    @lib.commands.command()
    @lib.commands.is_owner()
    async def reload(self, ctx):
        
        lib.seeks1.clear()
        lib.seeks2.clear()
        lib.seeks3.clear()
        lib.games.clear()
        lib.playing.clear()
        lib.move_history.clear()
        lib.color.clear()
        lib.pairs.clear()
        lib.first_moves.clear()
        lib.board_pieces.clear()
        lib.kings.clear()
        


        for f in lib.files:
            try:
                lib.bot.reload_extension(f)
                await ctx.send('> ' + f + ' was updated!')
            except Exception as e:
                await ctx.send('> ' + f + ' is not updated! Error: ' + str(e))
        await ctx.send('> data has been reset!')

def setup(bot):
    bot.add_cog(Control(bot))