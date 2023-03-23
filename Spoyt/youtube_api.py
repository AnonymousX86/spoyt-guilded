# -*- coding: utf-8 -*-
from json import loads as json_loads
from os import getenv

import requests

from Spoyt import log


class YouTubeResult:
    def __init__(
            self, 
            video_found: bool, 
            video_id: str = None, 
            video_title: str = None,
            video_description: str = None,
            video_published_date: str = None
    ) -> None:
        self.video_found = video_found
        self.video_id = video_id
        self.video_title = video_title
        self.video_description = video_description
        self.video_published_date = video_published_date

    @property
    def video_link(self) -> str:
        return f'https://www.youtube.com/watch?v={self.video_id}'
    
    @property
    def video_thumbnail(self) -> str:
        return f'https://i.ytimg.com/vi/{self.video_id}/default.jpg'


def find_youtube_id(query: str) -> YouTubeResult:
    yt_r = requests.get(
        'https://www.googleapis.com/youtube/v3/search'
        '?key={}'
        '&part=snippet'
        '&maxResults=1'
        '&q={}'.format(
            getenv('YOUTUBE_API_KEY'),
            query
        )
    )
    content = json_loads(yt_r.content)
    if (error_code := yt_r.status_code) == 200:
        data = YouTubeResult(
            video_found=True,
            video_id=content['items'][0]['id']['videoId'],
            video_title=content['items'][0]['snippet']['title'],
            video_description=content['items'][0]['snippet']['description'],
            video_published_date=content['items'][0]['snippet']['publishTime'][:10]
        )
    elif error_code == 403:
        data = YouTubeResult(
            video_found=False,
            video_description='Bot is not set properly. Ask the bot owner for further information.'
        )
        log.error(content['error']['message'])
    else:
        data = YouTubeResult(
            video_found=False,
            video_description=content['error']['message']
        )
    return data
