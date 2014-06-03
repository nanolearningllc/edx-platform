"""
Module containts utils specific for video_module but not for transcripts.
"""
import requests
import json


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
        cdn_url = "http://api.xuetangx.com/edx/video?s3_url={}"
        cdn_video_url = requests.get(cdn_url.format(original_url))
        if cdn_video_url.status_code == 200:
            cdn_result = json.loads(cdn_video_url.content)
            return cdn_result['sources'][0]
        