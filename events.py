from lib import *
from chess_functions import render

class error_handle(commands.Cog):
    #defualt cooldown error
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown, try again after {round(error.retry_after)} seconds.", delete_after=5)

        elif isinstance(error, commands.CommandNotFound): pass

        else:
          e = str(error) + ' at: {}'.format('```'+'\n'.join(traceback.format_exception(etype = type(error), value = error, tb = error.__traceback__)))+'```'
          print(e)

class reaction(commands.Cog):
    @bot.event
    async def on_raw_reaction_add(payload):
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        
        if message.author == bot.user and payload.member.bot == False:
            if payload.member.id not in playing:
                if message.id in seeks1:

                    opponent = seeks1[payload.message_id]
                    opp = bot.get_user(opponent)
                    i = len(games)
                    
                    #data
                    playing[opponent] = i
                    playing[payload.member.id] = i
                    games[i] = deepcopy(boards.standard)
                    move_history[i] = []
                    piece_history[i] =[]
                    first_moves[i] = deepcopy(initials.standard)
                    pairs[opponent] = payload.member.id
                    pairs[payload.member.id] = opponent
                    kings[i] = {'w':(3,0), 'b': (3,7)}
                    board_pieces[i] = deepcopy(pieces.standard)

                    
                    #picks a random color and sets color
                    c = ['w','b']
                    a = random.choice([0,-1])
                    color[payload.member.id] = random.choice(c[a])
                    c.pop(a)
                    if c == ['w']:
                        white_name = opp.name
                        black_name = payload.member.name
                    elif c == ['b']:
                        white_name = payload.member.name
                        black_name = opp.name
                    if payload.member.id == opponent: color[opponent] = ['w','b']
                    else: color[opponent] = c[0]
                    
                    #remove seek data
                    if payload.user_id in seeks2:
                        chnl = bot.get_channel(seeks3[payload.user_id][0])
                        msg = await chnl.fetch_message(seeks3[payload.user_id][1])
                        await msg.delete()

                        r1 = seeks2[payload.user_id]
                        r2 = seeks1[r1]
                        del seeks1[r1]
                        del seeks2[r2]
                        del seeks3[payload.user_id]
                    
                    if opponent in seeks2:
                        r1 = seeks2[opponent]
                        r2 = seeks1[r1]
                        del seeks1[r1]
                        del seeks2[r2]
                        del seeks3[opponent]

                        await message.delete()

                    #creates image
                    w = render(games[i], 'w')
                    font = ImageFont.truetype("Fonts/arial-black.ttf", int(100 - round(len(white_name) * 1.69)))
                    draw = ImageDraw.Draw(w)
                    draw.text((0, 0),white_name,(255,255,255),font=font)

                    #save image, send image, remove image
                    w.save('Temp_Images\{}_white.png'.format(i))
                    f = discord.File('Temp_Images\{}_white.png'.format(i))
                    await channel.send(file = f)
                    os.remove('Temp_Images\{}_white.png'.format(i))
                    
                elif message.embeds[0].description == 'React to accept the challenge!': await message.delete()

            else:
                await channel.send('❌ You cannot play more than one game at once.')
            


class listen(commands.Cog):
    @bot.event
    async def on_member_join(member):
        print(member)
    
    @bot.event
    async def on_message(message):
        await bot.process_commands(message)

def setup(bot):
    bot.add_cog(error_handle(bot))
    bot.add_cog(reaction(bot))
    bot.add_cog(listen(bot))