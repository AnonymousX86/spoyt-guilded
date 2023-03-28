# -*- coding: utf-8 -*-
from logging import basicConfig, INFO
from os import getenv
from socket import gethostbyname, gethostname

from guilded import Client, Color, Embed, Forbidden, ChatMessage, NotFound
from rich.logging import RichHandler

from Spoyt.spotify_api import TrackEmbed, model_track, search_spotify
from Spoyt.youtube_api import YouTubeResult, find_youtube_id
from Spoyt import log


class EmptyEmbed(Embed):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = '\u00a0'
        self.color = Color.gilded()


def main():
    basicConfig(
        level=INFO,
        format='%(message)s',
        datefmt='[%x]',
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    client = Client()

    @client.event
    async def on_ready():
        log.info(f'Logged in as {client.user}')

    @client.event
    async def on_message(message: ChatMessage):
        if message.author_id == client.user_id:
            return
        elif message.content == 'debug':
            await message.channel.send(f'\u2139 {gethostbyname(gethostname())}')
            return
        elif not message.content.startswith('[https://open.spotify.com/track/'):
            return

        spotify_msg = await message.channel.send(embed=Embed(
            title=':hourglass_flowing_sand: Spotify link found!',
            description='Connecting to super secret database...',
            color=Color.green()
        ))

        track_id = message.content[1::].split(']')[0].split('?')[0].split('&')[0].split('/')[-1]
        spotify_query = search_spotify(track_id)

        if not spotify_query:
            await spotify_msg.edit(embed=Embed(
                title='Oh no',
                description='Spotify is out of service',
                color=Color.red()
            ))
            return

        track = model_track(spotify_query)
        track_embed = TrackEmbed(track)

        try:
            await message.delete()
        except Forbidden or NotFound:
            pass
        else:
            track_embed.add_author(message.author)

        await spotify_msg.edit(embed=track_embed)

        youtube_msg = await message.channel.send(embed=Embed(
            title=':hourglass_flowing_sand: Searching YouTube',
            color=Color.gilded()
        ))

        youtube_query = '{} {}'.format(track.name, ' '.join(track.artists))
        result = find_youtube_id(
            query=youtube_query
        )

        if not result.video_found:
            await youtube_msg.edit(embed=Embed(
                title='Video not found',
                description=result.video_description,
                color=Color.dark_red()
            ))
            return

        await youtube_msg.edit(embed=Embed(
                title=result.video_title,
                description='[{0}]({0})'.format(result.video_link),
                color=Color.gilded()
        ).add_field(
            name='Description',
            value=result.video_description,
            inline=False
        ).add_field(
            name='Published',
            value=result.video_published_date
        ).set_thumbnail(
            url=result.video_thumbnail
        ).set_author(
            name=f'{message.author.display_name} (probably) shared:',
            icon_url=message.author.display_avatar.url
        ))

    client.run(getenv('BOT_TOKEN'))

if __name__ == '__main__':
    main()
