import logging
import time
from fastapi import FastAPI, Request
from app.config import settings
from app.database import Base, engine
from app.logger import logger
from app.routers import all_news, send_news, queue, modified_text, media, setting_routers

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)

app.include_router(media.router)
app.include_router(all_news.router)
app.include_router(send_news.router)
app.include_router(queue.router)
app.include_router(modified_text.router)
app.include_router(setting_routers.router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    route = request.scope.get("route")
    path_template = route.path if route else request.url.path
    
    logger.info(
        f"method={request.method} path='{request.url.path}' status={response.status_code} duration={process_time:.4f}",
        extra={
            "tags": {
                "method": request.method,
                "path_template": path_template,  
                "path_raw": request.url.path,    
                "status": response.status_code,
                "duration": process_time
            }
        }
    )
    
    return response

if __name__ == "__main__":
    try:
        import uvicorn
        logging.debug("Starting uvicorn")
        uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
    except Exception as error:
        logging.error(error)
