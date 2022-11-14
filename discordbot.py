from time import sleep
from digitalcurrency import getprice, strategy
from discord_components import Select, SelectOption, ComponentsBot, Button
import asyncio
import discord
from fuzzywuzzy import fuzz, process



# 輸入自己Bot的TOKEN碼


Token = "0000"
bot = ComponentsBot("/")
user_coroutine = {}
user = {}
comparelist = ["BTCUSDT","ETHUSDT","SOLUSDT","ADAUSDT","BNBUSDT","SHIBUSDT","MATICUSDT","GMTUSDT","APEUSDT","DOGEUSDT"]

# 起動時呼叫

async def selectbox(channel, channel_id):
    try:
        while user[channel_id]:
            await asyncio.sleep(1)
            try:
                await channel.send("輸入一個貨幣對 EX:BTCUSDT")
                currency = await bot.wait_for("message", 
                check = lambda message: message.author != "digital currency trading#7205" and message.channel.id == channel.id , 
                timeout = 600)
                currency = currency.content
                gp = getprice(currency,frequency = '1m')
                is_correct_currency = gp.check(count= 1)
                comparewin, similarity = process.extractOne(currency, comparelist, scorer = fuzz.ratio)
                print(comparewin,similarity)
                if not is_correct_currency and similarity < 45:
                    await channel.send("輸入了錯誤的貨幣對")
                    await asyncio.sleep(1)
                    continue
                elif not is_correct_currency and similarity >= 45:
                    await channel.send(f"你是不是想選{comparewin}", components =                    
                        [[Button(label="是", style="3", custom_id="button1"), Button(label="否", style="4", custom_id="button2")]])            
                    button_interaction = await bot.wait_for("button_click", 
                    check = lambda i: i.custom_id == "button1" or i.custom_id == "button2")
                    button_ans = button_interaction.custom_id
                    if button_ans == "button1":
                        await button_interaction.send("你選擇<是>")
                        currency = comparewin
                    elif button_ans == "button2":
                        await button_interaction.send("你選擇<否>")
                        continue
                    await asyncio.sleep(1)
                state = "state1"
                options_selector ={
                    "state1":[SelectOption(label="指標策略", value = "1"),SelectOption(label="自訂策略", value = "2"),SelectOption(label="cancel", value = "cancel")],
                    "state2":[SelectOption(label="RSI&MACD&MA", value = "3"),SelectOption(label="VEGAS", value = "4"),SelectOption(label="LIN", value = "6"), SelectOption(label="cancel", value = "cancel")],
                    "state3":[SelectOption(label="此功能尚未開放", value = "5")]
                }
                await channel.send(content = "select an option!", components = [Select(
                                                                placeholder = "select somthing",
                                                                options = options_selector[state],                                            
                                                                custom_id="client"
                )])
                
                interaction = await bot.wait_for("select_option", check=lambda inter: inter.custom_id == "client" )
                res = interaction.values[0]

                if res == "1":
                    await interaction.send("你選擇了指標策略")
                    state = "state2"
                elif res == "2":
                    await interaction.send("你選擇了自訂策略")
                    state = "state3"
                elif res == "cancel":
                    await interaction.send("你關閉了選項")
                    continue
                
                await channel.send(content = "select an option!", components = [Select(
                                                                placeholder = "Choose a trading strategy",
                                                                options = options_selector[state],                                            
                                                                custom_id="client"
                )])

                interaction = await bot.wait_for("select_option", check=lambda inter: inter.custom_id == "client" )
                res = interaction.values[0]
                
                if res == "3":
                    await interaction.send("你選擇了RSI&MACD&MA")
                    await TD(channel, 3, channel_id, currency)
                    
                elif res == "4":
                    await interaction.send("你選擇了vegas")
                    await TD(channel, 4, channel_id, currency)

                elif res == '6':
                    await interaction.send("你選擇了LIN")
                    await TD(channel, 6, channel_id, currency)

                elif res == "cancel":
                    await interaction.send("你關閉了選項")
                    continue
            except asyncio.TimeoutError:
                await channel.send("輸入時間過長")
                user.pop(channel_id)
                break
            except:
                await channel.send("未知錯誤")
                break
    except:
        pass 

@bot.event
async def on_ready():
    print("logged in") 


@bot.command()
async def resetbot(ctx):
    name = str(ctx.channel)
    channel = discord.utils.get(ctx.guild.channels, name=name)
    channel_id = channel.id
    global user_coroutine, user
    user_coroutine[channel_id] = False
       

 
    


# @bot.command()
# async def test(ctx):
#     # await ctx.send(embed=discord.Embed(title="Hey", description="Tell me something!"))
#     modal = discord.ui.Modal(
#         custom_id="modal",
#         title="Modal Title",
#         components=[
#             discord.ui.TextInput(
#                 style=discord.ui.TextStyleType.SHORT,
#                 custom_id="text-input-1",
#                 label="Short text input",
#             )
#         ],
#     )
#     await ctx.popup(modal)



@bot.command()
async def restartbot(ctx):
    name = str(ctx.channel)
    channel = discord.utils.get(ctx.guild.channels, name=name)
    channel_id = channel.id
    global user_coroutine, user
    user_coroutine[channel_id] = True
    user[channel_id] = True
    await selectbox(channel, channel_id)

    
@bot.event
async def on_guild_channel_create(channel): #監聽頻道創建的事件
    global user_coroutine, user
    user_coroutine[channel.id] = True
    user[channel.id] = True
    print(user_coroutine, user)
    await selectbox(channel, channel.id)

@bot.event
async def on_guild_channel_delete(channel): #監聽頻道刪除的事件
    try:
        global user_coroutine, user
        user_coroutine.pop(channel.id)
        user.pop(channel.id)
        print(user_coroutine, user)
    except:
        pass




async def TD(ctx, ref_res, channel_id, currency):
    gp = getprice(currency, frequency ='4h')
    try:
        discordstate = 1
        statelist = []
        # fre = "1m"
        while user_coroutine[channel_id]:
            if discordstate == 1:
                await ctx.send("策略運行中")
                discordstate = 0

            if ref_res == 3:
                direction, currentprice, stopwin, stoploss = strategy.RSI_MA_SMA(gp.get_closeprice(count = 14),
                                                                                gp.get_closeprice(count = 23),
                                                                                gp.get_closeprice(count = 34),  
                                                                                gp.get_closeprice(count = 76), 
                                                                                gp.get_closeprice(count = 1),
                                                                                gp.get_highprice(count = 10), 
                                                                                gp.get_lowprice(count = 10))
            elif ref_res == 4:
                direction, currentprice, stopwin, stoploss = strategy.vegas(gp.get_closeprice(count = 144),
                                                                            gp.get_closeprice(count = 169),
                                                                            gp.get_closeprice(count = 576),  
                                                                            gp.get_closeprice(count = 676), 
                                                                            gp.get_closeprice(count = 1),
                                                                            gp.get_lowprice(count = 10))
            elif ref_res == 6:
                direction, currentprice, stopwin, stoploss = strategy.LIN(gp.get_closeprice(count = 144),
                                                                            gp.get_closeprice(count = 169),
                                                                            gp.get_closeprice(count = 576),  
                                                                            gp.get_closeprice(count = 676), 
                                                                            gp.get_closeprice(count = 1),
                                                                            gp.get_lowprice(count = 10))

            """
            elif ref_res == 6:
                direction, currentprice, stopwin, stoploss = strategy.vegas(gp.get_closeprice(count = 131),
                                                                            gp.get_closeprice(count = 145),
                                                                            gp.get_closeprice(count = 20),  
                                                                            gp.get_closeprice(count = 94), 
                                                                            gp.get_closeprice(count = 1),
                                                                            gp.get_lowprice(count = 8))
            """

            await asyncio.sleep(3)
            statelist.append(direction)
            if len(statelist) == 5 :
                statelist.pop(0)
                if statelist[3] != statelist[2] and statelist[3] != "None":
                    await ctx.send(f"幣種:BTCUSDT\n進場價格:{currentprice}\n方向:{direction}\n止盈:{stopwin}\n止損:{stoploss}")
            print(channel_id, user_coroutine[channel_id])
    except:
        pass


     
    
    # Bot起動
# client.run(TOKEN)  #上線時使用
bot.run(Token) #測試時使用