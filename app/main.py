from logging import exception
from passlib.context import CryptContext

from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware

from starlette.middleware.base import BaseHTTPMiddleware

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from sqlalchemy import create_engine

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from app.core.config import settings
from app.db import database, bdx_database
# from app.utils.dependencies import get_user_manager
from app.models.user import UserRead, UserCreate, UserUpdate
from app.routers.users import fastapi_users, auth_backend, google_oauth_client
from app.routers import items
from app.routers import schedules
from app.utils.middleware import DisallowBlacklistedTokens


app = FastAPI()
app.state.database = database
app.state.bdx_database = bdx_database


dbt_middleware = DisallowBlacklistedTokens()
app.add_middleware(BaseHTTPMiddleware, dispatch=dbt_middleware)


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    bdx_database_ = app.state.bdx_database
    if not database_.is_connected:
        await database_.connect()
    if not bdx_database_.is_connected:
        await bdx_database_.connect()
    
    try:
        jobstores = {
            'default': SQLAlchemyJobStore(
                engine=create_engine(
                    settings.SQLALCHEMY_DATABASE_URI,
                    pool_pre_ping=True
                    )
                )
            }
        app.state.scheduler = AsyncIOScheduler(
            jobstores=jobstores, job_defaults={
                'misfire_grace_time': 60 * 30,
                'coalesce': True
                }
            )
        app.state.scheduler.start()
        logger.info("Created Schedule Object")   
    except Exception as e:    
        logger.error(f"Unable to Create Schedule Object because of {e}")
    
    FastAPICache.init(InMemoryBackend(), prefix=f'{settings.SERVER_NAME}-cache')


    # doesn't work under Win
    # su = await UserModel.objects.get_or_none(email=settings.FIRST_SUPERUSER)
    # if not su:
    #     async with get_user_manager() as user_manager:
    #             user = await user_manager.create(
    #                 UserCreate(
    #                     email=settings.FIRST_SUPERUSER,
    #                     hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
    #                     is_superuser=True,
    #                     is_active=True,
    #                     is_verified=True
    #                     )
    #             )


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    bdx_database_ = app.state.bdx_database
    if database_.is_connected:
        await database_.disconnect()
    if bdx_database_.is_connected:
        await bdx_database_.disconnect()
    app.state.scheduler.shutdown()
    logger.info("Scheduler is shut down")


@app.get('/', tags=['root'])
async def info():
    return {
        'api': settings.SERVER_NAME,
        'version': '0.6a-pre',
        'docs': '/docs',
        'openapi': '/openapi.json'
        }


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        auth_backend,
        settings.SECRET_KEY,
        associate_by_email=True,
        redirect_url=settings.GOOGLE_OAUTH_CALLBACK_REDIRECT_URL
        ),
    prefix="/auth/google",
    tags=["auth"],
)

app.include_router(items.router, tags=["search"])
app.include_router(schedules.router, tags=["scheduler"])
