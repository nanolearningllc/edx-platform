"""
Module containts utils specific for video_module but not for transcripts.
"""
import requests
import json

from django.conf import settings


def create_youtube_string(module):
    """
    Create a string of Youtube IDs from `module`'s metadata
    attributes. Only writes a speed if an ID is present in the
    module.  Necessary for backwards compatibility with XML-based
    courses.
    """
    youtube_ids = [
        module.youtube_id_0_75,
        module.youtube_id_1_0,
        module.youtube_id_1_25,
        module.youtube_id_1_5
    ]
    youtube_speeds = ['0.75', '1.00', '1.25', '1.50']
    return ','.join([
        ':'.join(pair)
        for pair
        in zip(youtube_speeds, youtube_ids)
        if pair[1]
    ])

def get_video_from_cdn(original_url):
        request_url = settings.VIDEO_CDN_URL + original_url
        cdn_response = requests.get(request_url)
        if cdn_response.status_code == 200:
            cdn_content = json.loads(cdn_response.content)
            return cdn_content['sources'][0]
