import discord
from discord.ext import commands
import openai
import asyncio


keys = open('apikeys', 'r').read().splitlines()


api_keys = keys[2]

owner_id = keys[3] 


server_id = keys[4]

async def simulate_typing(ctx):
    async with ctx.typing():
        await asyncio.sleep(15)


intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix=['>'], intents=intents)


chat_histories = {}


user_names = {}


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    server = bot.get_guild(server_id)
    await process_server_info(server)

    bot.loop.create_task(reset_chat_histories())


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author.bot:  # ignore other bots
        return

    if not message.content.startswith(('>')):
        return

    await bot.process_commands(message) 


@bot.command(name='c')
async def chat_with_bot(ctx, *, input_text):

    wait_message = await ctx.send("Please Wait...")

    async with ctx.channel.typing():

        prompt_prefix = """(Respond like a professional virtual assistant.)""" # we can change it according to our need 
        input_text_with_prefix = prompt_prefix + input_text

        user_id = ctx.author.id


        user_name = user_names.get(user_id, "User")


        if user_id not in chat_histories:
            chat_histories[user_id] = []


        chat_histories[user_id].append({
            "role": "user",
            "content": input_text_with_prefix 
        })


        messages = [
            {
                "role": "system",
                "content": f"boy"
            },
        ]



        messages.extend(chat_histories[user_id][-5:])


    def send_message_to_gpt(message):
        for api_key in api_keys:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=message,
                    api_key=api_key
                )
                return response['choices'][0]['message']['content'].strip()
            except openai.OpenAIError as e:

                print(f"OpenAIError occurred: {e}")

                continue
            except Exception as e:

                print(f"An error occurred: {e}")
                continue
        return None


    output_text = send_message_to_gpt(messages)

    if output_text is None:
        await ctx.send("Error.")
    else:
        await ctx.send(f'{ctx.author.mention} {output_text}')


        await wait_message.delete()


        chat_histories[user_id].append({
            "role": "assistant",
            "content": output_text
        })


async def process_server_info(server):

    server_info = {
        "name": server.name,
        "id": server.id,

    }
    print(server_info)



async def reset_chat_histories():
    while True:
        await asyncio.sleep(1 * 60 * 60)
        chat_histories.clear()
        server = bot.get_guild(server_id)


bot.remove_command("help")


@bot.command(name='help', aliases=['h', 'cmds'])
async def custom_help(ctx):
    Number_of_Server = len(bot.guilds)
    botPing = round(bot.latency * 1000)

    embed = discord.Embed(
        color=discord.Color(0xFFFFFF),
        title='COMMANDS',
        description=f'__**STATISTICAL:**__\n\n> **📊Number of servers:** {Number_of_Server}\n> **🟢Bot Ping:** {botPing}ms\n> \n\n__**COMMANDS:**__'
    )

    embed.add_field(
        name='▶️  Default prefix',
        value='`>`',
        inline=True
    )
    embed.add_field(
        name=':robot:  Chat AI',
        value='`>`\n`Ex: >c Hello.`',
        inline=True
    )

    embed.set_thumbnail(url=bot.user.avatar_url_as(format='png', size=1024))
    embed.set_image(url='Enter image link here')

    await ctx.reply(embed=embed)


# Chạy bot
bot.run(keys[1])
