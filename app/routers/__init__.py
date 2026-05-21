"""Routers"""
from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.user_groups import router as user_groups_router
from app.routers.user_profiles import router as user_profiles_router
from app.routers.user_points import router as user_points_router
from app.routers.categories import router as categories_router
from app.routers.posts import router as posts_router
from app.routers.comments import router as comments_router
from app.routers.tags import router as tags_router

health = health_router
auth = auth_router
users = users_router
user_groups = user_groups_router
user_profiles = user_profiles_router
user_points = user_points_router
categories = categories_router
posts = posts_router
comments = comments_router
tags = tags_router