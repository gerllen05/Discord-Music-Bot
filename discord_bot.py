import discord
from discord.ext import commands
import random
from discord import FFmpegPCMAudio
import yt_dlp
import json

class DiscordBot:
    def __init__(self, api_key):
        self.intents = discord.Intents.all()
        self.intents.members = True

        self.queue = {}

        self.client = commands.Bot(command_prefix= '+', intents=self.intents)
        self.client.run(api_key)

    def check_queue(self, ctx, id):
        if self.queue[id] != []:
            voice = ctx.guild.voice_client
            source = self.queue[id].pop(0)
            voice.play(source)

    async def add_to_queue(self, ctx, source):
            voice = ctx.guild.voice_client
            guild_id = ctx.message.guild.id
            if guild_id in self.queue:
                self.queue[guild_id].append(source)
            else:
                self.queue[guild_id] = [source]
            await ctx.send("Песня добавлена в очередь")
    
    def handle_commands(self):
        #   Функция, которая стартуется после запуска бота   
        @self.client.event
        async def on_ready():
            print("This bot is ready to use")
            print("------------------------")

        #   Функция стартуется, когда присоединяется человек к серверу
        @self.client.event
        async def on_member_join(member):
            channel = self.client.get_channel(1076545999998292099)
            await channel.send("Здравствуйте, с вами разговаривает личный помощник Михаила - Москардини. Добро пожаловать на сервер.")

        #   Функция стартуется, когда человек ливает с сервера
        @self.client.event
        async def on_member_remove(member):
            channel = self.client.get_channel(1076545999998292099)
            await channel.send("Ну и пиздуй гнида")
            
        #   Пишет приветствие
        @self.client.command()
        async def hello(ctx):
            await ctx.send("Здравствуйте, с вами разговаривает личный помощник Михаила - Москардини. Приятно познакомиться.")

        #   Присоединяется к голосовому каналу и говорит своё приветствие
        @self.client.command(pass_context = True)
        async def join(ctx):
            if (ctx.author.voice):
                channel = ctx.message.author.voice.channel
                voice = await channel.connect()
                source = FFmpegPCMAudio('music/greetings.mp3')
                player = voice.play(source)
            else:
                await ctx.send("Вы не находитесь в голосовом канале, чтобы впустить меня в гости, вы должны находиться в канале!")

        #   Ливает из голосового канала
        @self.client.command(pass_context = True)
        async def leave(ctx):
            if(ctx.voice_client):
                await ctx.guild.voice_client.disconnect()
                await ctx.send("Я вышел из голосового канала")
            else:
                await ctx.send("Я не нахожусь в голосовом канале")

        #   Ставит на паузу аудио
        @self.client.command(pass_context = True)
        async def pause(ctx):
            voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
            if voice.is_playing():
                voice.pause()
            else:
                await ctx.send("Никакой голосовой файл, сейчас не проигрывается")

        #   Восстанавливает воспроизведение аудио
        @self.client.command(pass_context = True)
        async def resume(ctx):
            voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
            if voice.is_paused():
                voice.resume()
            else:
                await ctx.send("Сейчас ничего не стоит на паузе")

        #   Останавливает воспроизведение аудио
        @self.client.command(pass_context = True)
        async def skip(ctx):
            voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
            voice.stop()

        # @self.client.command(pass_context = True)
        # async def play(ctx, args):
        #     voice = ctx.guild.voice_client
        #     song = "music/"+args+".mp3"
        #     source = FFmpegPCMAudio(song)
        #     player = voice.play(source, after=lambda x=None: check_queue(ctx,ctx.message.guild.id))


        @self.client.command(pass_context = True)
        async def play(ctx, *, url):
            voice_channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                await voice_channel.connect()

            ydl_opts = {
            'format': 'bestaudio',
            'noplaylist':'True',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }], }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # info = ydl.extract_info(url, download=False)
                info = ydl.extract_info("ytsearch:%s" % url, download=False)['entries'][0]
                with open('info.json', 'w') as file:
                    json.dump(info, fp=file, indent=2)
                title = info["title"]
                await ctx.send(f"Дорогой пользователь, поставил пластинку с песней: {title}")
                url2 = info['url']
                source = discord.FFmpegPCMAudio(url2)
                voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
                if not voice.is_playing():
                    vc = ctx.guild.voice_client
                    vc.play(source, after=lambda x=None: self.check_queue(ctx,ctx.message.guild.id))
                else:
                    await self.add_to_queue(ctx, source)

        @self.client.command()
        async def roll(ctx):
            rndnum = random.randint(1, 10)
            await ctx.send("Ваше рандомное число: "+str(rndnum))

        @self.client.command()
        async def help_me(ctx):
            await ctx.send("Доброго времени суток, с вами разговаривает личный помощник Михаила - Москардини. Сейчас я вам отправлю список моих команд.")
            await ctx.send("join - Я захожу в ваш голосовой канал.")
            await ctx.send("leave - Я выхожу из голосового канала в котором находился.")
            await ctx.send("roll - Я выведу рандомно число в диапазоне от 1 до 10.")
            await ctx.send("На этом мой список команд заканчиваеться. В будущем ожидается пополнение. Приятного отдыха.")



    