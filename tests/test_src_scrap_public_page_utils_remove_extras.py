import datetime
import pytest

from src.utils.scrap_public_page_utils import remove_extras

@pytest.mark.parametrize(
    "post_links, since, until, expected_result",
    [
        (
            [
                ('https://www.facebook.com/LaVoz.com.ar/posts/10158835645530829', datetime.datetime(2022, 2, 2, 20, 48)),
                ('https://www.facebook.com/LaVoz.com.ar/posts/10158835633240829', datetime.datetime(2022, 2, 2, 20, 37)),
                ('https://www.facebook.com/LaVoz.com.ar/posts/10158835617115829', datetime.datetime(2022, 2, 2, 20, 25)),
                ('https://www.facebook.com/LaVoz.com.ar/posts/10158835520205829', datetime.datetime(2022, 2, 2, 20, 20)),
                ('https://www.facebook.com/LaVoz.com.ar/posts/10158835599145829', datetime.datetime(2022, 2, 2, 20, 13)),
                ('https://www.facebook.com/LaVoz.com.ar/posts/10158835586300829', datetime.datetime(2022, 2, 2, 20, 1))
            ],
            datetime.datetime(2022, 2, 2, 20, 0),
            datetime.datetime(2022, 2, 2, 20, 20),
            [
                ('https://www.facebook.com/LaVoz.com.ar/posts/10158835599145829', datetime.datetime(2022, 2, 2, 20, 13)),
                ('https://www.facebook.com/LaVoz.com.ar/posts/10158835586300829', datetime.datetime(2022, 2, 2, 20, 1))
            ],
        ),
    ],
)
def test_remove_extras(post_links, since, until, expected_result):
    assert remove_extras(post_links, since, until) == expected_result