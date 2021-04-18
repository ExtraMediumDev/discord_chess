from lib import *
from chess_functions import render, coords, check_square, type_check, validate
 
class Commands(commands.Cog):
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def help(self, ctx):
        if ctx.prefix == '$':
          embed=discord.Embed(title="List of Commands", description='**Invite the bot to your server!** [link](https://discord.com/api/oauth2/authorize?client_id=799713156804116511&permissions=8&scope=bot)\n\nNext Patch Update:\n - Draw by insufficient material\n - Draw request\n - Takeback request\n - Promotion specification', color=0xFFC0CB)

          bot_member = bot.get_user(799713156804116511)
          embed.set_thumbnail(url=bot_member.avatar_url)

          embed.add_field(name="$seek", value="Sends an open challenge that anyone can accept (except for a bot)")
          embed.add_field(name="$move `xxxx`", value="Example: `g1f3`\n - Moves the piece on `g1` to `f3`. Make sure you make valid moves.\n - Chess notation have values ranging from a-h and 1-8.")
          embed.add_field(name="$cancel", value="Cancels your seek")
          embed.add_field(name="$leave", value="Ends the game you are in. Please don't abuse! A resign/draw/timeout feature will be added in the future")
          embed.add_field(name="$ping", value="Tells you the latency or how much time it takes for the bot to respond in miliseconds")
          embed.set_footer(text="This is a pre-release version that is still in development. Please excuse any errors.")
        await ctx.send('> Join our community server to report bugs or ask questions! https://discord.gg/w58kZvpmM5', embed=embed)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def ping(self, ctx):
        if ctx.prefix == '$': await ctx.send(str(round(bot.latency * 1000)) + 'ms')
            

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def seek(self, ctx):
        if ctx.prefix == '$':
            if not(ctx.author.id in seeks2 or ctx.author.id in playing): 
                embed = discord.Embed(title="Outgoing Seek From {}".format(ctx.author.name), description='React to accept the challenge!', color=0x0000FF)

                msg = await ctx.send(embed=embed)
                await msg.add_reaction('☑️')

                seeks1[msg.id] = ctx.author.id
                seeks2[ctx.author.id] = msg.id
                seeks3[ctx.author.id] = (ctx.channel.id, msg.id)

            else:
                await ctx.send('❌ Do not seek if you already have an active seek or are in a game.')

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def cancel(self, ctx):
        if ctx.prefix == '$':
            if ctx.author.id in seeks2:
                r1 = seeks2[ctx.author.id]
                r2 = seeks1[r1]

                del seeks1[r1]
                del seeks2[r2]

                await ctx.send('✅ Your seek was cancelled.')
            else:
                await ctx.send('❌ You have no ongoing seeks or you are in a game.')

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def leave(self, ctx):
        if ctx.prefix == '$':
            if ctx.author.id in playing:
                opponent = pairs[ctx.author.id]
                game_id = playing[ctx.author.id]
                if ctx.author.id == opponent:
                  del playing[ctx.author.id]
                  del pairs[ctx.author.id]
                  del color[ctx.author.id]
                else:
                  del playing[ctx.author.id]
                  del playing[opponent]
                  del pairs[ctx.author.id]
                  del pairs[opponent]
                  del color[ctx.author.id]
                  del color[opponent]

                del games[game_id]
                del move_history[game_id]
                del piece_history[game_id]
                del first_moves[game_id]
                del kings[game_id]
                del board_pieces[game_id]

                await ctx.send('✅ You pretty much abandoned the game.')
            else:
                await ctx.send('❌ You are not in a game.')

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def move(self, ctx, ntn):
        if ctx.prefix == '$':
            author = ctx.message.author

            if author.id in playing:
                if ntn[0] in letters and ntn[2] in letters and ntn[1] in numbers and ntn[3] in numbers and len(ntn) == 4:

                    game_id = playing[author.id]
                    board = games[game_id]
                    m_history = move_history[game_id]
                    opponent = bot.get_user(pairs[author.id])
                    initial = first_moves[game_id]
                    onboard = board_pieces[game_id]

                    #find current turn
                    if len(move_history[game_id]) % 2 == 0: 
                        turn, n_turn = 'w','b'
                    elif len(move_history[game_id]) % 2 == 1: 
                        turn, n_turn = 'b','w'
                    
                    #x1,y1 original coordinates. x2,y2, new coordinates.
                    x1,y1 = coords(ntn[0] + ntn[1])
                    x2,y2 = coords(ntn[2] + ntn[3])

                    #if valid move, replace square with empty and make put piece on new square
                    if color[author.id] == turn or author.id == pairs[author.id]:
                        can_move, x1, y1, x2, y2, kings[game_id] = validate(board,turn,initial,kings[game_id],onboard,x1,y1,x2,y2)
                        if can_move == True:
                            m_history = move_history[game_id]
                            m_history.append((x1,y1,x2,y2))

                            #creates image
                            name = opponent.name
                            rendered = render(board, n_turn)
                            font = ImageFont.truetype("Fonts/arial-black.ttf", int(100 - round(len(name) * 1.69)))
                            draw = ImageDraw.Draw(rendered)
                            draw.text((0, 0),name,(255,255,255),font=font)

                            #saves image, sends image, deletes image
                            rendered.save('Temp_Images\{}.png'.format(game_id))
                            f = discord.File('Temp_Images\{}.png'.format(game_id))
                            await ctx.send(file = f)
                            os.remove('Temp_Images\{}.png'.format(game_id))
                        
                        elif can_move == 'danger':
                          await ctx.send('❌ Beware of endangering your king!')
                        elif can_move == 'checkmate' or can_move == 'stalemate': 
                          winner, loser = author.name, opponent.name

                          #creates image
                          rendered = render(board, n_turn)
                          font = ImageFont.truetype("Fonts/arial-black.ttf", int(100 - round(len(loser) * 1.69)))
                          draw = ImageDraw.Draw(rendered)
                          draw.text((0, 0),loser,(255,255,255),font=font)

                          #saves image, sends image, deletes image
                          rendered.save('Temp_Images\{}.png'.format(game_id))
                          f = discord.File('Temp_Images\{}.png'.format(game_id))
                          await ctx.send(file = f)
                          os.remove('Temp_Images\{}.png'.format(game_id))

                          if author.id == opponent.id:
                            del playing[author.id]
                            del pairs[author.id]
                            del color[author.id]
                          else:
                            del playing[author.id]
                            del playing[opponent.id]
                            del pairs[author.id]
                            del pairs[opponent.id]
                            del color[author.id]
                            del color[opponent.id]

                          del games[game_id]
                          del move_history[game_id]
                          del piece_history[game_id]
                          del first_moves[game_id]
                          del kings[game_id]
                          del board_pieces[game_id]
                          
                          if can_move == 'checkmate':
                            embed = discord.Embed(title= winner + ' has won!', description = 'Say GG to each other', color=0xFFFF00)
                            await ctx.send(embed = embed)
                          if can_move == 'stalemate':
                            embed = discord.Embed(title= winner + ' and ' + loser + 'has drawn', description = 'Say GG to each other', color=0xFFFFFF)
                            await ctx.send(embed = embed)
                        else:
                            await ctx.send('❌ Invalid move')
                    else:
                        await ctx.send('❌ Wait for your turn')
                else:
                    await ctx.send('❌ Wrong notation. $notation to see how to do notation.')
            else:
                await ctx.send('❌ You aren\'t playing a game.')


                



                
        
        


def setup(bot):
    bot.add_cog(Commands(bot))