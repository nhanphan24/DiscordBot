'''
Created on Jul 27, 2018

@author: nhanp

This bot is designed to play music in Discord voice channel. It is useful
since everyone in the channel can listen to the same song while they play
game or having conservations in the call. The bot takes song requests from
the users
'''
from discord.ext import commands
from collections import defaultdict

bot = commands.Bot(command_prefix = '!')

@bot.event
async def on_ready():
    '''Called when the bot is ready to receive commands. It shows in the
    console
    '''
    print(bot.user.name, 'is online')


class MusicPlayer:
    '''The Music class allows the users to play music in there channel'''
    def __init__(self):
        '''Create two dictionaries with self.current_song storing the song
        that is playing while self.queced_songs stores the songs in queue
        '''
        self.current_song = dict()
        self.queued_songs = defaultdict(list)
        
    @commands.command(pass_context = True)
    async def come(self, context):
        '''User to use this command to call the bot into the user that the
        user is in
        '''
        channel = context.message.author.voice.voice_channel
        await bot.join_voice_channel(channel)
    
    @commands.command(pass_context = True)
    async def leave(self, context):
        '''This command asks the bot to leave voice channel, which deletes
        songs in queue and stops the song that's playing
        '''
        server = context.message.server
        voice_client = bot.voice_client_in(server)
        try:
            await context.invoke(self.stop)
        finally:
            await bot.say(bot.user.name +' is leaving the voice channel')
            await voice_client.disconnect()
    
    @commands.command(pass_context = True)
    async def play(self, context, *, song: str):
        '''This command lets the user choose what song they want to hear. If
        the bot is not in the voice channel, self.come will be called for the
        bot to join the channel. If a song is currently playing, the requested
        song will be added to queue
        '''
        server = context.message.server
        if not bot.is_voice_connected(server):
            await context.invoke(self.come)
        voice_client = bot.voice_client_in(server)
        search = {'default_search': 'auto', 'quiet': True}
        music = await voice_client.create_ytdl_player(song, ytdl_options = search, 
                                                      after = lambda : self._play_queued_songs(server.id))
        
        if server.id in self.current_song:
            self.queued_songs[server.id].append(music)
            await bot.say('a song is playing; \'' + str(music.title) + '\' is added to queue')
            await context.invoke(self.queue)
            
        else:
            self.current_song[server.id] = music
            await context.invoke(self.playing)
            music.start()
    
    def _play_queued_songs(self, server_id):
        '''This function plays the first song in queue'''
        if len(self.queued_songs[server_id]) != 0:
            music = self.queued_songs[server_id].pop(0)
            self.current_song[server_id] = music
            music.start()
        else:
            self.current_song = dict()
    
    @commands.command(pass_context = True)
    async def playing(self, context):
        '''Shows which song is playing'''
        server_id = context.message.server.id
        try:
            music = self.current_song[server_id]
        except KeyError:
            await bot.say('No song is playing right now')
            return False
        if music.duration >= 60:
            duration_min, duration_sec = divmod(music.duration, 60)
        else:
            duration_min, duration_sec = 0, music.duration
        await bot.say('playing: ' + str(music.title) + ' [duration: ' + str(duration_min) + 'm ' + str(duration_sec) + 's]')

    @commands.command(pass_context = True)
    async def pause(self, context):
        '''Pause the song'''
        self.current_song[context.message.server.id].pause()
    
    @commands.command(pass_context = True)
    async def resume(self, context):
        '''Resume the song'''
        self.current_song[context.message.server.id].resume()
    
    @commands.command(pass_context = True)
    async def skip(self, context):
        '''Skip to next song in queue'''
        server_id = context.message.server.id
        if self.queued_songs[server_id] == []:
            await bot.say('there is no song in queue; unable to skip')
        else:
            self.current_song[server_id].stop()
            self.current_song = dict()
            self._play_queued_songs(server_id)
            await context.invoke(self.playing)
    
    @commands.command(pass_context = True)
    async def stop(self, context):
        '''Stop playing any audio and delete the queue list but unlike 'leave'
        command, the bot stays in the voice channel'''
        server_id = context.message.server.id
        if server_id in self.current_song:
            self.current_song[server_id].stop()
            del self.current_song[server_id]
        if server_id in self.queued_songs:
            del self.queued_songs[server_id]
    
    @commands.command(pass_context = True)
    async def delete(self, context, *, song: str):
        '''This command allows the users to delete the songs in queue'''
        server_id = context.message.server.id
        for queue_num in range(len(self.queued_songs[server_id])):
            if song.lower() in self.queued_songs[server_id][queue_num].title.lower():
                await bot.say('deleting \'' + self.queued_songs[server_id][queue_num].title + '\' from queue list')
                del self.queued_songs[server_id][queue_num]
                await context.invoke(self.queue)
                break
        else:
            await bot.say(song + ' was not deleted because it cannot be found in queue list')
    
    @commands.command(pass_context = True)
    async def queue(self, context):
        '''This command lets the users know the list of songs in queue'''
        server_id = context.message.server.id
        if len(self.queued_songs[server_id]) == 0:
            await bot.say('no song in queue')
            return
        await bot.say('queue list:')
        for song_num in range(len(self.queued_songs[server_id])):
            await bot.say(str(song_num + 1) + '. ' + self.queued_songs[server_id][song_num].title)
                 
    
if __name__ == '__main__':
    bot.add_cog(MusicPlayer())
    bot.run('Bot taken goes here')
