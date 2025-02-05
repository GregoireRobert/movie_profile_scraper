from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse

from scraper import LetterboxdScraper

app = FastAPI()
scraper = LetterboxdScraper()


class ProfileRequest(BaseModel):
    url: str


@app.get("/import")
async def import_profile(username: str = None):
    # background_tasks.add_task(scraper.get_profile_movies, profile_request.url)
    urls = scraper.get_profile_movies(username)
    return JSONResponse(urls)
