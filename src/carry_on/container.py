"""Dependency injection container for CarryOn application."""

from dependency_injector import containers, providers

from carry_on.infrastructure.mongodb import get_database
from carry_on.infrastructure.repositories.mongo_idea_repository import (
    MongoIdeaRepository,
)
from carry_on.infrastructure.repositories.course.mongo_course_repository import (
    MongoCourseRepository,
)
from carry_on.infrastructure.repositories.training.mongo_stroke_repository import (
    MongoStrokeRepository,
)
from carry_on.infrastructure.repositories.mongo_user_repository import (
    MongoUserRepository,
)
from carry_on.infrastructure.security.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from carry_on.services.authentication_service import AuthenticationService
from carry_on.services.course_service import CourseService
from carry_on.services.idea_service import IdeaService
from carry_on.services.stroke_service import StrokeService


class Container(containers.DeclarativeContainer):
    """Centralized DI container for the CarryOn application."""

    # Infrastructure
    database = providers.Singleton(get_database)

    # Collections (derived from database)
    users_collection = providers.Factory(lambda db: db.users, database)
    strokes_collection = providers.Factory(lambda db: db.strokes, database)
    ideas_collection = providers.Factory(lambda db: db.ideas, database)
    courses_collection = providers.Factory(lambda db: db.courses, database)

    # Security
    password_hasher = providers.Singleton(Argon2PasswordHasher)

    # Repositories
    user_repository = providers.Factory(MongoUserRepository, users_collection)
    stroke_repository = providers.Factory(MongoStrokeRepository, strokes_collection)
    idea_repository = providers.Factory(MongoIdeaRepository, ideas_collection)
    course_repository = providers.Factory(MongoCourseRepository, courses_collection)

    # Services
    authentication_service = providers.Factory(
        AuthenticationService, user_repository, password_hasher
    )
    stroke_service = providers.Factory(StrokeService, stroke_repository)
    idea_service = providers.Factory(IdeaService, idea_repository)
    course_service = providers.Factory(CourseService, course_repository)
