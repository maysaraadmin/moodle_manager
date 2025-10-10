#!/usr/bin/env python3
"""
API Routes for Moodle Manager FastAPI Backend
Organized REST endpoints for Moodle operations
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse

from main import app_state
from data_models import (
    MoodleAPIResponse, ErrorResponse,
    User, Course, Group, Enrollment,
    GradeItem, Grade, Role, AssignmentSubmission,
    CalendarEvent, Message, FileInfo,
    MoodleUserCreateRequest, MoodleUserUpdateRequest,
    MoodleCourseCreateRequest, MoodleCourseUpdateRequest,
    MoodleGroupCreateRequest, MoodleEnrollmentRequest,
    MoodleGradeUpdateRequest, MoodleRoleAssignmentRequest,
    MoodleMessageRequest, MoodleFileUploadRequest,
    MoodleCalendarEventRequest
)

router = APIRouter()


# Dependency to check API availability
def get_moodle_api():
    """Dependency to ensure Moodle API is available"""
    if not app_state.moodle_api:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Moodle API not initialized"
        )
    return app_state.moodle_api


def get_auth_manager():
    """Dependency to ensure auth manager is available"""
    if not app_state.auth_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication manager not initialized"
        )
    return app_state.auth_manager


# ===== SITE INFORMATION =====

@router.get("/site/info", response_model=MoodleAPIResponse)
async def get_site_info(api: MoodleRESTAPI = Depends(get_moodle_api)):
    """Get Moodle site information"""
    try:
        result = await api.core_webservice_get_site_info()
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get site info: {str(e)}"
        )


# ===== USER MANAGEMENT =====

@router.get("/users", response_model=MoodleAPIResponse)
async def get_users(
    criteria: Optional[str] = Query(None, description="Search criteria"),
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Get users with optional search criteria"""
    try:
        result = await api.core_user_get_users(criteria=criteria)
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )


@router.get("/users/{user_id}", response_model=MoodleAPIResponse)
async def get_user(user_id: int, api: MoodleRESTAPI = Depends(get_moodle_api)):
    """Get specific user by ID"""
    try:
        result = await api.core_user_get_users(criteria=[{"key": "id", "value": str(user_id)}])
        if result and len(result) > 0:
            return MoodleAPIResponse(success=True, data=result[0])
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )


@router.post("/users", response_model=MoodleAPIResponse)
async def create_user(
    user_data: MoodleUserCreateRequest,
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Create a new Moodle user"""
    try:
        result = await api.core_user_create_users(users=[user_data.dict()])
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.put("/users/{user_id}", response_model=MoodleAPIResponse)
async def update_user(
    user_id: int,
    user_data: MoodleUserUpdateRequest,
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Update an existing Moodle user"""
    try:
        # Add user ID to the update data
        update_data = user_data.dict()
        update_data["id"] = user_id

        result = await api.core_user_update_users(users=[update_data])
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete("/users/{user_id}", response_model=MoodleAPIResponse)
async def delete_user(user_id: int, api: MoodleRESTAPI = Depends(get_moodle_api)):
    """Delete a Moodle user"""
    try:
        result = await api.core_user_delete_users(userids=[user_id])
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


# ===== COURSE MANAGEMENT =====

@router.get("/courses", response_model=MoodleAPIResponse)
async def get_courses(api: MoodleRESTAPI = Depends(get_moodle_api)):
    """Get all courses"""
    try:
        result = await api.core_course_get_courses()
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get courses: {str(e)}"
        )


@router.get("/courses/{course_id}", response_model=MoodleAPIResponse)
async def get_course(course_id: int, api: MoodleRESTAPI = Depends(get_moodle_api)):
    """Get specific course by ID"""
    try:
        result = await api.core_course_get_courses(courseids=[course_id])
        if result and len(result) > 0:
            return MoodleAPIResponse(success=True, data=result[0])
        else:
            raise HTTPException(status_code=404, detail="Course not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get course: {str(e)}"
        )


@router.post("/courses", response_model=MoodleAPIResponse)
async def create_course(
    course_data: MoodleCourseCreateRequest,
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Create a new Moodle course"""
    try:
        result = await api.core_course_create_courses(courses=[course_data.dict()])
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create course: {str(e)}"
        )


@router.put("/courses/{course_id}", response_model=MoodleAPIResponse)
async def update_course(
    course_id: int,
    course_data: MoodleCourseUpdateRequest,
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Update an existing Moodle course"""
    try:
        update_data = course_data.dict()
        update_data["id"] = course_id

        result = await api.core_course_update_courses(courses=[update_data])
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update course: {str(e)}"
        )


@router.delete("/courses/{course_id}", response_model=MoodleAPIResponse)
async def delete_course(course_id: int, api: MoodleRESTAPI = Depends(get_moodle_api)):
    """Delete a Moodle course"""
    try:
        result = await api.core_course_delete_courses(courseids=[course_id])
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete course: {str(e)}"
        )


@router.get("/courses/{course_id}/contents", response_model=MoodleAPIResponse)
async def get_course_contents(course_id: int, api: MoodleRESTAPI = Depends(get_moodle_api)):
    """Get course contents (modules, activities, etc.)"""
    try:
        result = await api.core_course_get_contents(courseid=course_id)
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get course contents: {str(e)}"
        )


# ===== ENROLLMENT MANAGEMENT =====

@router.get("/enrollments/users/{user_id}", response_model=MoodleAPIResponse)
async def get_user_courses(user_id: int, api: MoodleRESTAPI = Depends(get_moodle_api)):
    """Get courses a user is enrolled in"""
    try:
        result = await api.core_enrol_get_users_courses(userid=user_id)
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user courses: {str(e)}"
        )


@router.get("/enrollments/courses/{course_id}", response_model=MoodleAPIResponse)
async def get_enrolled_users(course_id: int, api: MoodleRESTAPI = Depends(get_moodle_api)):
    """Get users enrolled in a course"""
    try:
        result = await api.core_enrol_get_enrolled_users(courseid=course_id)
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get enrolled users: {str(e)}"
        )


@router.post("/enrollments", response_model=MoodleAPIResponse)
async def enroll_user(
    enrollment_data: MoodleEnrollmentRequest,
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Enroll a user in a course"""
    try:
        result = await api.enrol_manual_enrol_users(
            enrolments=[enrollment_data.dict()]
        )
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enroll user: {str(e)}"
        )


@router.delete("/enrollments", response_model=MoodleAPIResponse)
async def unenroll_user(
    user_id: int = Query(..., description="User ID to unenroll"),
    course_id: int = Query(..., description="Course ID to unenroll from"),
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Unenroll a user from a course"""
    try:
        result = await api.enrol_manual_unenrol_users(
            unenrolments=[{"userid": user_id, "courseid": course_id}]
        )
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unenroll user: {str(e)}"
        )


# ===== GROUP MANAGEMENT =====

@router.get("/groups/courses/{course_id}", response_model=MoodleAPIResponse)
async def get_course_groups(course_id: int, api: MoodleRESTAPI = Depends(get_moodle_api)):
    """Get groups in a course"""
    try:
        result = await api.core_group_get_course_groups(courseid=course_id)
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get course groups: {str(e)}"
        )


@router.post("/groups", response_model=MoodleAPIResponse)
async def create_group(
    group_data: MoodleGroupCreateRequest,
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Create a new group"""
    try:
        result = await api.core_group_create_groups(groups=[group_data.dict()])
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create group: {str(e)}"
        )


@router.delete("/groups/{group_id}", response_model=MoodleAPIResponse)
async def delete_group(group_id: int, api: MoodleRESTAPI = Depends(get_moodle_api)):
    """Delete a group"""
    try:
        result = await api.core_group_delete_groups(groupids=[group_id])
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete group: {str(e)}"
        )


@router.get("/groups/{group_id}/members", response_model=MoodleAPIResponse)
async def get_group_members(group_id: int, api: MoodleRESTAPI = Depends(get_moodle_api)):
    """Get members of a group"""
    try:
        result = await api.core_group_get_group_members(groupid=group_id)
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get group members: {str(e)}"
        )


@router.post("/groups/{group_id}/members", response_model=MoodleAPIResponse)
async def add_group_member(
    group_id: int,
    user_id: int = Query(..., description="User ID to add to group"),
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Add a user to a group"""
    try:
        result = await api.core_group_add_group_members(
            members=[{"groupid": group_id, "userid": user_id}]
        )
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add group member: {str(e)}"
        )


@router.delete("/groups/{group_id}/members", response_model=MoodleAPIResponse)
async def remove_group_member(
    group_id: int,
    user_id: int = Query(..., description="User ID to remove from group"),
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Remove a user from a group"""
    try:
        result = await api.core_group_delete_group_members(
            members=[{"groupid": group_id, "userid": user_id}]
        )
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove group member: {str(e)}"
        )


# ===== GRADE MANAGEMENT =====

@router.get("/grades/courses/{course_id}/items", response_model=MoodleAPIResponse)
async def get_grade_items(course_id: int, api: MoodleRESTAPI = Depends(get_moodle_api)):
    """Get grade items for a course"""
    try:
        result = await api.core_grade_get_grade_items(courseid=course_id)
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get grade items: {str(e)}"
        )


@router.get("/grades/users/{user_id}/courses/{course_id}", response_model=MoodleAPIResponse)
async def get_user_grades(
    user_id: int,
    course_id: int,
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Get grades for a specific user in a course"""
    try:
        result = await api.core_grade_get_grades(
            courseid=course_id,
            userid=user_id
        )
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user grades: {str(e)}"
        )


@router.post("/grades", response_model=MoodleAPIResponse)
async def update_grades(
    grade_data: MoodleGradeUpdateRequest,
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Update grades"""
    try:
        result = await api.core_grades_update_grades(grades=[grade_data.dict()])
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update grades: {str(e)}"
        )


# ===== ASSIGNMENT SUBMISSIONS =====

@router.get("/assignments/submissions", response_model=MoodleAPIResponse)
async def get_assignment_submissions(
    assignment_id: int = Query(..., description="Assignment ID"),
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Get assignment submissions"""
    try:
        result = await api.mod_assign_get_submissions(assignmentid=assignment_id)
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get assignment submissions: {str(e)}"
        )


# ===== MESSAGING =====

@router.post("/messages", response_model=MoodleAPIResponse)
async def send_message(
    message_data: MoodleMessageRequest,
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Send a message to users"""
    try:
        result = await api.core_message_send_instant_message(
            message=message_data.dict()
        )
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


# ===== CALENDAR EVENTS =====

@router.get("/calendar/events", response_model=MoodleAPIResponse)
async def get_calendar_events(
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Get calendar events"""
    try:
        events_filter = {}
        if course_id:
            events_filter["courseids"] = [course_id]

        result = await api.core_calendar_get_calendar_events(**events_filter)
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get calendar events: {str(e)}"
        )


@router.post("/calendar/events", response_model=MoodleAPIResponse)
async def create_calendar_event(
    event_data: MoodleCalendarEventRequest,
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Create a calendar event"""
    try:
        result = await api.core_calendar_create_calendar_events(
            events=[event_data.dict()]
        )
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create calendar event: {str(e)}"
        )


# ===== FILE OPERATIONS =====

@router.post("/files/upload", response_model=MoodleAPIResponse)
async def upload_file(
    file_data: MoodleFileUploadRequest,
    api: MoodleRESTAPI = Depends(get_moodle_api)
):
    """Upload a file to Moodle"""
    try:
        # Note: File upload implementation would need actual file handling
        # This is a placeholder for the API structure
        result = {"message": "File upload not yet implemented", "data": file_data.dict()}
        return MoodleAPIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
