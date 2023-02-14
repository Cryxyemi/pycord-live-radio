import discord
from discord.ext import commands
from discord.commands import slash_command, Option, SlashCommandGroup, OptionChoice
from discord.utils import basic_autocomplete


async def radio_player(ctx: discord.AutocompleteContext):
    i = [
        OptionChoice("Trashpop", "https://streams.ilovemusic.de/iloveradio19.mp3"),
        OptionChoice("I Love Radio", "https://streams.ilovemusic.de/iloveradio1.mp3"),
        OptionChoice("2 Dance", "https://streams.ilovemusic.de/iloveradio2.mp3"),
        OptionChoice("2000+ Throwbacks", "https://streams.ilovemusic.de/iloveradio37.mp3"),
        OptionChoice("2010+ Throwbacks", "https://streams.ilovemusic.de/iloveradio38.mp3"),
        OptionChoice("Bass by HBZ", "https://streams.ilovemusic.de/iloveradio29.mp3"),
        OptionChoice("Chillhop", "https://streams.ilovemusic.de/iloveradio17.mp3"),
        OptionChoice("Dance 2023", "https://streams.ilovemusic.de/iloveradio36.mp3"),
        OptionChoice("Dance First!", "https://streams.ilovemusic.de/iloveradio103.mp3"),
        OptionChoice("Dance history", "https://streams.ilovemusic.de/iloveradio26.mp3"),
        OptionChoice("Deutschrap Beste", "https://streams.ilovemusic.de/iloveradio6.mp3"),
        OptionChoice("Deutschrap first!", "https://streams.ilovemusic.de/iloveradio104.mp3"),
        OptionChoice("Greatest hits", "https://streams.ilovemusic.de/iloveradio16.mp3"),
        OptionChoice("Hardstyle", "https://streams.ilovemusic.de/iloveradio21.mp3"),
        OptionChoice("Hip Hop", "https://streams.ilovemusic.de/iloveradio3.mp3"),
        OptionChoice("Hip Hop 2023", "https://streams.ilovemusic.de/iloveradio35.mp3"),
        OptionChoice("Hip Hop history", "https://streams.ilovemusic.de/iloveradio27.mp3"),
        OptionChoice("Hip Hop history", "https://streams.ilovemusic.de/iloveradio27.mp3"),
        OptionChoice("Hits 2023", "https://streams.ilovemusic.de/iloveradio109.mp3"),
        OptionChoice("Hits history", "https://streams.ilovemusic.de/iloveradio12.mp3"),
        OptionChoice("X-Max", "https://streams.ilovemusic.de/iloveradio8.mp3"),
        OptionChoice("The 90s", "https://streams.ilovemusic.de/iloveradio24.mp3"),
        OptionChoice("Party hard", "https://streams.ilovemusic.de/iloveradio14.mp3"),
    ]
    
    return i

async def play_state_autocomplete(ctx: discord.AutocompleteContext):
    if ctx.interaction.guild.voice_client:
        if ctx.interaction.guild.voice_client.is_playing():
            return [OptionChoice("Pause", "pause")]
        else:
            return [OptionChoice("Resume", "resume")]


class Player(commands.Cog):
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        
        self.v_clients = {}
        
    music = SlashCommandGroup("music", "Music commands")
        
    @music.command(name="play_state", description="Pause or resume playing")
    async def _play_state(self, ctx: discord.ApplicationContext, option: Option(str, "Resume or Pause", autocomplete=basic_autocomplete(play_state_autocomplete))):
        if option == "pause":
            vc: discord.VoiceClient = self.v_clients.get(ctx.guild.id)
            if not vc.is_playing():
                return await ctx.respond("I am not playing", ephemeral=True)
            
            vc.pause()
            
            return await ctx.respond("Paused playing")
        
        elif option == "resume":
            vc: discord.VoiceClient = self.v_clients.get(ctx.guild.id)
            if not vc.is_paused():
                return await ctx.respond("I am not paused", ephemeral=True)
            
            vc.resume()
            
            return await ctx.respond("Resumed playing")
        
        else:
            return await ctx.respond("Invalid option", ephemeral=True)
        
    @music.command(name="join", description="Play live radio")
    async def _join(self, ctx: discord.ApplicationContext):
        if not ctx.author.voice:
            return await ctx.respond("You are not connected to a voice channel", ephemeral=True)
        
        try:
            vc = await ctx.author.voice.channel.connect()
        except discord.errors.ClientException:
            ctx.guild.voice_client.cleanup()
            await ctx.guild.voice_client.disconnect()
            vc = await ctx.author.voice.channel.connect()
        
        self.v_clients[ctx.guild.id] = vc
        
        await ctx.respond("Joined voice channel")
        
    @music.command(name="stop", description="Stop live radio")
    async def _stop(self, ctx: discord.ApplicationContext):
        if not ctx.author.voice:
            return await ctx.respond("You are not connected to a voice channel", ephemeral=True)
        
        vc: discord.VoiceClient = self.v_clients.get(ctx.guild.id)
        
        if not vc:
            return await ctx.respond("I am not connected to a voice channel", ephemeral=True)
        
        if not vc.is_playing():
            return await ctx.respond("I am not playing anything", ephemeral=True)
        
        vc.stop()
        await ctx.respond("Stopped playing")
        
    @music.command(name="leave", description="Leave voice channel")
    async def _leave(self, ctx: discord.ApplicationContext):
        if not ctx.author.voice:
            return await ctx.respond("You are not connected to a voice channel", ephemeral=True)
        
        vc: discord.VoiceClient = self.v_clients.get(ctx.guild.id)
        
        await vc.disconnect()
        await ctx.respond("Left voice channel")
        
        vc.cleanup()
        
        self.v_clients.pop(ctx.guild.id)
        
    @music.command(name="play", description="Play live radio")
    async def _play(self, ctx: discord.ApplicationContext, radio: Option(str, "Select radio", autocomplete=basic_autocomplete(radio_player))):
        if not "https://streams.ilovemusic.de/" in radio:
            return await ctx.respond("Invalid radio", ephemeral=True)
        
        vc: discord.VoiceClient = self.v_clients.get(ctx.guild.id)
        
        if vc is None or ctx.author.voice.channel != vc.channel:
            if not ctx.author.voice:
                return await ctx.respond("You are not connected to a voice channel", ephemeral=True)
        
            try:
                vc = await ctx.author.voice.channel.connect()
            except discord.errors.ClientException:
                await ctx.guild.voice_client.disconnect()
                vc = await ctx.author.voice.channel.connect()
            
            self.v_clients[ctx.guild.id] = vc
        
        vc.play(discord.FFmpegPCMAudio(radio))
        
        return await ctx.respond("Playing radio")
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.id != self.bot.user.id:
            return
        
        vc: discord.VoiceClient = self.v_clients.get(member.guild.id)
        
        if not vc:
            return
        
        if after.channel is not None:
            after.self_deaf = True
            if vc.is_playing:
                vc.stop()
            return
        
        try:
            vc.cleanup()
        except:
            pass
        
        self.v_clients.pop(member.guild.id)


def setup(bot: discord.Bot):
    bot.add_cog(Player(bot))
