import pytest
from mcp_imdb.tools import (
    search_imdb,
    get_movie_details,
    get_actor_details,
    search_people,
    normalize_imdb_id,
    normalize_person_id
)

@pytest.mark.asyncio
async def test_search_imdb():
    # Test movie search
    response = await search_imdb("Inception")
    assert len(response.results) > 0
    assert any("Inception" in result.title for result in response.results)
    
    # Test with content type
    response = await search_imdb("Breaking Bad", content_type="tv")
    assert len(response.results) > 0
    assert any("Breaking Bad" in result.title for result in response.results)

@pytest.mark.asyncio
async def test_get_movie_details():
    # Test with Inception's IMDB ID
    movie = await get_movie_details("tt1375666")
    assert movie.title == "Inception"
    assert movie.director == "Christopher Nolan"
    assert movie.year == "2010"

@pytest.mark.asyncio
async def test_get_actor_details():
    # Test with Leonardo DiCaprio's IMDB ID
    actor = await get_actor_details("nm0000138")
    assert actor.name == "Leonardo DiCaprio"
    assert actor.url == "https://www.imdb.com/name/nm0000138/"

@pytest.mark.asyncio
async def test_search_people():
    response = await search_people("Tom Hanks")
    assert len(response.results) > 0
    assert any("Tom Hanks" in result.name for result in response.results)

@pytest.mark.asyncio
async def test_error_handling():
    # Test invalid movie ID
    with pytest.raises(RuntimeError):
        await get_movie_details("invalid_id")
    
    # Test invalid person ID
    with pytest.raises(RuntimeError):
        await get_actor_details("invalid_id")

# test normalize_imdb_id
@pytest.mark.asyncio
async def test_normalize_imdb_id():
    assert normalize_imdb_id("tt1375666") == "tt1375666"
    assert normalize_imdb_id("1375666") == "tt1375666"

# test normalize_person_id
@pytest.mark.asyncio
async def test_normalize_person_id():
    assert normalize_person_id("nm0000138") == "nm0000138"
    assert normalize_person_id("0000138") == "nm0000138"

@pytest.fixture
def sample_movie_id():
    return "tt1375666"  # Inception

@pytest.fixture
def sample_person_id():
    return "nm0000138"  # Leonardo DiCaprio

@pytest.fixture
def sample_search_query():
    return "Inception" 
