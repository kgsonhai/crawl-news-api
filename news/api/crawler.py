from fastapi import FastAPI, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from news.model.newscrawler import NewsCrawler
from news.service.crawler import CrawlerService

crawler_app = FastAPI()
crawler_service = CrawlerService()

origins = [
    "http://localhost:3000"
]

crawler_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@crawler_app.post('/crawler')
async def run_crawler(news_crawler: NewsCrawler):
    background_tasks = BackgroundTasks()
    background_tasks.add_task(crawler_service.run_crawler, news_crawler)
    response = JSONResponse(status_code=200, content="Crawler is running", background=background_tasks)
    return response
