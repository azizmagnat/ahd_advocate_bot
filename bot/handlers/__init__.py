from aiogram import Router
from .common import router as common_router
from .user import router as user_router
from .admin import router as admin_router
from .errors import router as errors_router

main_router = Router()

main_router.include_router(common_router)
main_router.include_router(user_router)
main_router.include_router(admin_router)
main_router.include_router(errors_router)
