"""API endpoints for course management."""

from decimal import Decimal

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException
from pydantic import BaseModel

from carry_on.api.index import app, verify_password
from carry_on.container import Container
from carry_on.services.authentication_service import AuthenticatedUser
from carry_on.services.course_service import CourseService


class HoleRequest(BaseModel):
    hole_number: int
    par: int
    stroke_index: int


class CourseCreateRequest(BaseModel):
    name: str
    holes: list[HoleRequest]
    slope_rating: str | None = None
    course_rating: str | None = None


@app.post("/api/courses")
@inject
async def create_course(
    course: CourseCreateRequest,
    user: AuthenticatedUser = Depends(verify_password),
    service: CourseService = Depends(Provide[Container.course_service]),
) -> dict:
    """Create a new golf course."""
    try:
        course_id = service.add_course(
            user_id=user.id,
            name=course.name,
            holes=[h.model_dump() for h in course.holes],
            slope_rating=(
                Decimal(course.slope_rating)
                if course.slope_rating is not None
                else None
            ),
            course_rating=(
                Decimal(course.course_rating)
                if course.course_rating is not None
                else None
            ),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "id": course_id.value,
        "message": "Course created successfully",
    }


@app.get("/api/courses/{course_id}")
@inject
async def get_course_detail(
    course_id: str,
    user: AuthenticatedUser = Depends(verify_password),
    service: CourseService = Depends(Provide[Container.course_service]),
) -> dict:
    """Get a specific course with full hole details."""
    course = service.get_course_detail(course_id, user.id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    return {
        "id": course.id.value if course.id else None,
        "name": course.name,
        "number_of_holes": course.number_of_holes,
        "total_par": course.total_par,
        "slope_rating": (
            str(course.slope_rating) if course.slope_rating is not None else None
        ),
        "course_rating": (
            str(course.course_rating) if course.course_rating is not None else None
        ),
        "holes": [
            {
                "hole_number": h.hole_number,
                "par": h.par,
                "stroke_index": h.stroke_index,
            }
            for h in course.holes
        ],
    }


@app.get("/api/courses")
@inject
async def list_courses(
    user: AuthenticatedUser = Depends(verify_password),
    service: CourseService = Depends(Provide[Container.course_service]),
) -> dict:
    """List courses for the authenticated user."""
    courses = service.get_user_courses(user.id)

    return {
        "courses": [
            {
                "id": course.id.value if course.id else None,
                "name": course.name,
                "number_of_holes": course.number_of_holes,
                "total_par": course.total_par,
            }
            for course in courses
        ],
        "count": len(courses),
    }
