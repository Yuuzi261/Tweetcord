import pytest

from core.classes import ParsedTweet
from src.notification.utils import is_match_media_type


def make_parsed_tweet(media_count: int) -> ParsedTweet:
    return ParsedTweet({
        'tweet': {
            'raw_text': {'text': 'hello'},
            'media': {'all': [{'type': 'photo', 'url': f'https://example.com/{i}.jpg'} for i in range(media_count)]},
        }
    })


@pytest.mark.parametrize('media_count, media_type, expected', [
    (0, '11', True),
    (2, '11', True),
    (0, '10', True),   # no media only
    (2, '10', False),
    (0, '01', False),  # media only
    (2, '01', True),
])
def test_is_match_media_type_with_parsed_tweet(media_count, media_type, expected):
    assert is_match_media_type(make_parsed_tweet(media_count), media_type) is expected
