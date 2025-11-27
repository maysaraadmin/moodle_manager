"""
Moodle API Threading System
Provides QThread-based workers for all Moodle REST API calls to prevent GUI freezing
"""

# Add the project root to the Python path
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from PyQt5.QtCore import QThread, pyqtSignal, QObject
from typing import Dict, List, Any, Optional, Union
import logging
import os
from services.moodle.moodle_rest import MoodleRestClient

logger = logging.getLogger(__name__)


class MoodleWorkerSignals(QObject):
    """Signals for Moodle API workers"""
    finished = pyqtSignal(object)  # Result data
    error = pyqtSignal(str)  # Error message
    progress = pyqtSignal(int, str)  # Progress percentage and message
    started = pyqtSignal(str)  # Operation started message


class MoodleAPIWorker(QThread):
    """Base worker class for Moodle API calls"""
    
    def __init__(self, client: MoodleRestClient, operation_name: str):
        super().__init__()
        self.client = client
        self.operation_name = operation_name
        self.signals = MoodleWorkerSignals()
        self._is_running = True
        
    def run(self):
        """Execute the API call"""
        try:
            self.signals.started.emit(f"Starting {self.operation_name}...")
            logger.info(f"Starting {self.operation_name}")
            
            # Execute the specific API operation
            result = self.execute_operation()
            
            if self._is_running:
                self.signals.finished.emit(result)
                logger.info(f"Completed {self.operation_name}")
                
        except Exception as e:
            error_msg = f"Error in {self.operation_name}: {str(e)}"
            logger.error(error_msg)
            if self._is_running:
                self.signals.error.emit(error_msg)
    
    def execute_operation(self):
        """Override this method in subclasses to implement specific API calls"""
        raise NotImplementedError("Subclasses must implement execute_operation()")
    
    def stop(self):
        """Stop the worker"""
        self._is_running = False
        self.terminate()
        self.wait()


class ConnectionWorker(MoodleAPIWorker):
    """Worker for Moodle connection"""
    
    def __init__(self, client: MoodleRestClient):
        super().__init__(client, "Moodle Connection")
        
    def execute_operation(self):
        """Execute connection operation"""
        try:
            # First connect to get token
            if self.client.connect():
                # Then get site information
                site_info = self.client.get_site_info()
                if site_info:
                    return site_info
                else:
                    raise Exception("Connected but failed to get site information")
            else:
                raise Exception("Connection failed - invalid credentials or server unreachable")
        except Exception as e:
            # Re-raise the exception to be caught by the error handler
            raise e


class SiteInfoWorker(MoodleAPIWorker):
    """Worker for getting site information"""
    
    def __init__(self, client: MoodleRestClient):
        super().__init__(client, "Get Site Info")
        
    def execute_operation(self):
        """Execute get site info operation"""
        return self.client.get_site_info()


class GetUsersWorker(MoodleAPIWorker):
    """Worker for getting users"""
    
    def __init__(self, client: MoodleRestClient, criteria: List[Dict[str, Any]] = None):
        super().__init__(client, "Get Users")
        self.criteria = criteria
        
    def execute_operation(self):
        """Execute get users operation"""
        return self.client.get_users(self.criteria)


class GetUserByFieldWorker(MoodleAPIWorker):
    """Worker for getting user by field"""
    
    def __init__(self, client: MoodleRestClient, field: str, value: str):
        super().__init__(client, f"Get User by {field}")
        self.field = field
        self.value = value
        
    def execute_operation(self):
        """Execute get user by field operation"""
        return self.client.get_user_by_field(self.field, self.value)


class CreateUserWorker(MoodleAPIWorker):
    """Worker for creating user"""
    
    def __init__(self, client: MoodleRestClient, user_data: Dict[str, Any]):
        super().__init__(client, "Create User")
        self.user_data = user_data
        
    def execute_operation(self):
        """Execute create user operation"""
        return self.client.create_user(**self.user_data)


class UpdateUserWorker(MoodleAPIWorker):
    """Worker for updating user"""
    
    def __init__(self, client: MoodleRestClient, user_data: Dict[str, Any]):
        super().__init__(client, "Update User")
        self.user_data = user_data
        
    def execute_operation(self):
        """Execute update user operation"""
        return self.client.update_user(**self.user_data)


class DeleteUserWorker(MoodleAPIWorker):
    """Worker for deleting user"""
    
    def __init__(self, client: MoodleRestClient, user_id: int):
        super().__init__(client, f"Delete User {user_id}")
        self.user_id = user_id
        
    def execute_operation(self):
        """Execute delete user operation"""
        return self.client.delete_user(self.user_id)


class GetCoursesWorker(MoodleAPIWorker):
    """Worker for getting courses"""
    
    def __init__(self, client: MoodleRestClient, ids: List[int] = None):
        super().__init__(client, "Get Courses")
        self.ids = ids
        
    def execute_operation(self):
        """Execute get courses operation"""
        return self.client.get_courses(self.ids)


class CreateCourseWorker(MoodleAPIWorker):
    """Worker for creating course"""
    
    def __init__(self, client: MoodleRestClient, course_data: Dict[str, Any]):
        super().__init__(client, "Create Course")
        self.course_data = course_data
        
    def execute_operation(self):
        """Execute create course operation"""
        return self.client.create_course(**self.course_data)


class UpdateCourseWorker(MoodleAPIWorker):
    """Worker for updating course"""
    
    def __init__(self, client: MoodleRestClient, course_data: Dict[str, Any]):
        super().__init__(client, "Update Course")
        self.course_data = course_data
        
    def execute_operation(self):
        """Execute update course operation"""
        return self.client.update_course(**self.course_data)


class DeleteCourseWorker(MoodleAPIWorker):
    """Worker for deleting course"""
    
    def __init__(self, client: MoodleRestClient, course_id: int):
        super().__init__(client, f"Delete Course {course_id}")
        self.course_id = course_id
        
    def execute_operation(self):
        """Execute delete course operation"""
        return self.client.delete_course(self.course_id)


class GetCourseContentWorker(MoodleAPIWorker):
    """Worker for getting course content"""
    
    def __init__(self, client: MoodleRestClient, course_id: int):
        super().__init__(client, f"Get Course {course_id} Content")
        self.course_id = course_id
        
    def execute_operation(self):
        """Execute get course content operation"""
        return self.client.get_course_content(self.course_id)


class GetEnrolledUsersWorker(MoodleAPIWorker):
    """Worker for getting enrolled users"""
    
    def __init__(self, client: MoodleRestClient, course_id: int):
        super().__init__(client, f"Get Enrolled Users for Course {course_id}")
        self.course_id = course_id
        
    def execute_operation(self):
        """Execute get enrolled users operation"""
        return self.client.get_enrolled_users(self.course_id)


class EnrolUserWorker(MoodleAPIWorker):
    """Worker for enrolling user"""
    
    def __init__(self, client: MoodleRestClient, user_id: int, course_id: int, role_id: int = None):
        super().__init__(client, f"Enrol User {user_id} in Course {course_id}")
        self.user_id = user_id
        self.course_id = course_id
        self.role_id = role_id
        
    def execute_operation(self):
        """Execute enrol user operation"""
        return self.client.enrol_user(self.user_id, self.course_id, self.role_id)


class UnenrolUserWorker(MoodleAPIWorker):
    """Worker for unenrolling user"""
    
    def __init__(self, client: MoodleRestClient, user_id: int, course_id: int, role_id: int = None):
        super().__init__(client, f"Unenrol User {user_id} from Course {course_id}")
        self.user_id = user_id
        self.course_id = course_id
        self.role_id = role_id
        
    def execute_operation(self):
        """Execute unenrol user operation"""
        return self.client.unenrol_user(self.user_id, self.course_id, self.role_id)


class GetGroupsWorker(MoodleAPIWorker):
    """Worker for getting groups"""
    
    def __init__(self, client: MoodleRestClient, course_id: int):
        super().__init__(client, f"Get Groups for Course {course_id}")
        self.course_id = course_id
        
    def execute_operation(self):
        """Execute get groups operation"""
        return self.client.get_user_groups_by_course_id(self.course_id)


class CreateGroupWorker(MoodleAPIWorker):
    """Worker for creating group"""
    
    def __init__(self, client: MoodleRestClient, group_data: Dict[str, Any]):
        super().__init__(client, "Create Group")
        self.group_data = group_data
        
    def execute_operation(self):
        """Execute create group operation"""
        return self.client.create_group(**self.group_data)


class DeleteGroupWorker(MoodleAPIWorker):
    """Worker for deleting group"""
    
    def __init__(self, client: MoodleRestClient, group_id: int):
        super().__init__(client, f"Delete Group {group_id}")
        self.group_id = group_id
        
    def execute_operation(self):
        """Execute delete group operation"""
        return self.client.delete_group(self.group_id)


class AddGroupMembersWorker(MoodleAPIWorker):
    """Worker for adding members to a group"""
    
    def __init__(self, client: MoodleRestClient, group_id: int, user_ids: List[int]):
        super().__init__(client, f"Add Members to Group {group_id}")
        self.group_id = group_id
        self.user_ids = user_ids
        
    def execute_operation(self):
        """Execute add group members operation"""
        return self.client.add_group_members(self.group_id, self.user_ids)


class RemoveGroupMembersWorker(MoodleAPIWorker):
    """Worker for removing members from a group"""
    
    def __init__(self, client: MoodleRestClient, group_id: int, user_ids: List[int]):
        super().__init__(client, f"Remove Members from Group {group_id}")
        self.group_id = group_id
        self.user_ids = user_ids
        
    def execute_operation(self):
        """Execute remove group members operation"""
        return self.client.remove_group_members(self.group_id, self.user_ids)


class GetGroupMembersWorker(MoodleAPIWorker):
    """Worker for getting group members"""
    
    def __init__(self, client: MoodleRestClient, group_id: int):
        super().__init__(client, f"Get Members for Group {group_id}")
        self.group_id = group_id
        
    def execute_operation(self):
        """Execute get group members operation"""
        return self.client.get_group_members(self.group_id)


class GetGradeItemsWorker(MoodleAPIWorker):
    """Worker for getting grade items"""
    
    def __init__(self, client: MoodleRestClient, course_id: int):
        super().__init__(client, f"Get Grade Items for Course {course_id}")
        self.course_id = course_id
        
    def execute_operation(self):
        """Execute get grade items operation"""
        return self.client.get_grade_items(self.course_id)


class GetGradesWorker(MoodleAPIWorker):
    """Worker for getting grades"""
    
    def __init__(self, client: MoodleRestClient, course_id: int, user_id: int = None):
        super().__init__(client, f"Get Grades for Course {course_id}")
        self.course_id = course_id
        self.user_id = user_id
        
    def execute_operation(self):
        """Execute get grades operation"""
        return self.client.get_grades(self.course_id, self.user_id)


class UpdateGradesWorker(MoodleAPIWorker):
    """Worker for updating grades"""
    
    def __init__(self, client: MoodleRestClient, course_id: int, grade_items: List[Dict[str, Any]]):
        super().__init__(client, f"Update Grades for Course {course_id}")
        self.course_id = course_id
        self.grade_items = grade_items
        
    def execute_operation(self):
        """Execute update grades operation"""
        return self.client.update_grades(self.course_id, self.grade_items)


class GetRolesWorker(MoodleAPIWorker):
    """Worker for getting roles"""
    
    def __init__(self, client: MoodleRestClient):
        super().__init__(client, "Get Roles")
        
    def execute_operation(self):
        """Execute get roles operation"""
        return self.client.get_roles()


class AssignRoleWorker(MoodleAPIWorker):
    """Worker for assigning role"""
    
    def __init__(self, client: MoodleRestClient, user_id: int, role_id: int, context_id: int, context_level: str = 'course'):
        super().__init__(client, f"Assign Role {role_id} to User {user_id}")
        self.user_id = user_id
        self.role_id = role_id
        self.context_id = context_id
        self.context_level = context_level
        
    def execute_operation(self):
        """Execute assign role operation"""
        return self.client.assign_role(self.user_id, self.role_id, self.context_id, self.context_level)


class UnassignRoleWorker(MoodleAPIWorker):
    """Worker for unassigning role"""
    
    def __init__(self, client: MoodleRestClient, user_id: int, role_id: int, context_id: int, context_level: str = 'course'):
        super().__init__(client, f"Unassign Role {role_id} from User {user_id}")
        self.user_id = user_id
        self.role_id = role_id
        self.context_id = context_id
        self.context_level = context_level
        
    def execute_operation(self):
        """Execute unassign role operation"""
        return self.client.unassign_role(self.user_id, self.role_id, self.context_id, self.context_level)


class GetAssignmentSubmissionsWorker(MoodleAPIWorker):
    """Worker for getting assignment submissions"""
    
    def __init__(self, client: MoodleRestClient, assignment_id: int):
        super().__init__(client, f"Get Submissions for Assignment {assignment_id}")
        self.assignment_id = assignment_id
        
    def execute_operation(self):
        """Execute get assignment submissions operation"""
        return self.client.get_assignment_submissions(self.assignment_id)


class SendMessageWorker(MoodleAPIWorker):
    """Worker for sending message"""
    
    def __init__(self, client: MoodleRestClient, user_id: int, message: str, message_format: str = 'MOODLE'):
        super().__init__(client, f"Send Message to User {user_id}")
        self.user_id = user_id
        self.message = message
        self.message_format = message_format
        
    def execute_operation(self):
        """Execute send message operation"""
        return self.client.send_instant_message(self.user_id, self.message, self.message_format)


class UploadFileWorker(MoodleAPIWorker):
    """Worker for uploading file"""
    
    def __init__(self, client: MoodleRestClient, filepath: str, filename: str, **kwargs):
        super().__init__(client, f"Upload File {filename}")
        self.filepath = filepath
        self.filename = filename
        self.kwargs = kwargs
        
    def execute_operation(self):
        """Execute upload file operation"""
        return self.client.upload_file(self.filepath, self.filename, **self.kwargs)


class CSVBulkUploadWorker(MoodleAPIWorker):
    """Worker for CSV bulk user upload"""
    
    def __init__(self, client: MoodleRestClient, csv_filepath: str, delimiter: str = ',', encoding: str = 'utf-8', custom_mappings: Dict[str, str] = None):
        super().__init__(client, f"CSV Bulk Upload {os.path.basename(csv_filepath)}")
        self.csv_filepath = csv_filepath
        self.delimiter = delimiter
        self.encoding = encoding
        self.custom_mappings = custom_mappings or {}
        
    def execute_operation(self):
        """Execute CSV bulk upload operation"""
        from utils.helpers.csv_helper import CSVHelper
        
        csv_helper = CSVHelper()
        
        # Set custom mappings if provided
        for csv_col, moodle_field in self.custom_mappings.items():
            csv_helper.set_custom_mapping(csv_col, moodle_field)
        
        # Load CSV file
        csv_data = csv_helper.load_csv_file(self.csv_filepath, self.delimiter, self.encoding)
        
        # Map CSV columns to Moodle fields
        mapped_data = csv_helper.map_csv_to_moodle_fields(csv_data)
        
        # Validate user data
        validation_result = csv_helper.validate_user_data(mapped_data)
        
        # Prepare data for Moodle API
        prepared_users = csv_helper.prepare_moodle_user_data(validation_result['valid_users'])
        
        # Create users in batch
        if prepared_users:
            result = self.client.create_users_batch(prepared_users)
        else:
            result = []
        
        return {
            'created_users': result,
            'validation_result': validation_result,
            'total_rows': len(csv_data),
            'valid_count': len(validation_result['valid_users']),
            'invalid_count': len(validation_result['invalid_users'])
        }


class GetCalendarEventsWorker(MoodleAPIWorker):
    """Worker for getting calendar events"""
    
    def __init__(self, client: MoodleRestClient, **kwargs):
        super().__init__(client, "Get Calendar Events")
        self.kwargs = kwargs
        
    def execute_operation(self):
        """Execute get calendar events operation"""
        return self.client.get_calendar_events(**self.kwargs)


class UploadUserPictureWorker(MoodleAPIWorker):
    """Worker for uploading user profile picture"""
    
    def __init__(self, client: MoodleRestClient, user_id: int, picture_filepath: str, overwrite: bool = True):
        super().__init__(client, f"Upload Picture for User {user_id}")
        self.user_id = user_id
        self.picture_filepath = picture_filepath
        self.overwrite = overwrite
        
    def execute_operation(self):
        """Execute upload user picture operation"""
        return self.client.upload_user_picture(self.user_id, self.picture_filepath, self.overwrite)


class SubmitBackupWorker(MoodleAPIWorker):
    """Worker for submitting backup request"""
    
    def __init__(self, client: MoodleRestClient, course_id: int, settings: Dict[str, Any] = None):
        super().__init__(client, f"Submit Backup for Course {course_id}")
        self.course_id = course_id
        self.settings = settings
        
    def execute_operation(self):
        """Execute submit backup operation"""
        return self.client.submit_backup(self.course_id, self.settings)


class GetBackupStatusWorker(MoodleAPIWorker):
    """Worker for getting backup status"""
    
    def __init__(self, client: MoodleRestClient, backup_id: str):
        super().__init__(client, f"Get Backup Status for {backup_id}")
        self.backup_id = backup_id
        
    def execute_operation(self):
        """Execute get backup status operation"""
        return self.client.get_backup_status(self.backup_id)


class SubmitRestoreWorker(MoodleAPIWorker):
    """Worker for submitting restore request"""
    
    def __init__(self, client: MoodleRestClient, backup_file_path: str, target_course_id: int, settings: Dict[str, Any] = None):
        super().__init__(client, f"Submit Restore to Course {target_course_id}")
        self.backup_file_path = backup_file_path
        self.target_course_id = target_course_id
        self.settings = settings
        
    def execute_operation(self):
        """Execute submit restore operation"""
        return self.client.submit_restore(self.backup_file_path, self.target_course_id, self.settings)


class MoodleThreadManager:
    """Manager for Moodle API threads"""
    
    def __init__(self):
        self.active_threads = []
        
    def create_connection_worker(self, client: MoodleRestClient) -> ConnectionWorker:
        """Create connection worker"""
        worker = ConnectionWorker(client)
        self.active_threads.append(worker)
        return worker
    
    def create_site_info_worker(self, client: MoodleRestClient) -> SiteInfoWorker:
        """Create site info worker"""
        worker = SiteInfoWorker(client)
        self.active_threads.append(worker)
        return worker
    
    def create_get_users_worker(self, client: MoodleRestClient, criteria: List[Dict[str, Any]] = None) -> GetUsersWorker:
        """Create get users worker"""
        worker = GetUsersWorker(client, criteria)
        self.active_threads.append(worker)
        return worker
    
    def create_get_user_by_field_worker(self, client: MoodleRestClient, field: str, value: str) -> GetUserByFieldWorker:
        """Create get user by field worker"""
        worker = GetUserByFieldWorker(client, field, value)
        self.active_threads.append(worker)
        return worker
    
    def create_create_user_worker(self, client: MoodleRestClient, user_data: Dict[str, Any]) -> CreateUserWorker:
        """Create create user worker"""
        worker = CreateUserWorker(client, user_data)
        self.active_threads.append(worker)
        return worker
    
    def create_update_user_worker(self, client: MoodleRestClient, user_data: Dict[str, Any]) -> UpdateUserWorker:
        """Create update user worker"""
        worker = UpdateUserWorker(client, user_data)
        self.active_threads.append(worker)
        return worker
    
    def create_delete_user_worker(self, client: MoodleRestClient, user_id: int) -> DeleteUserWorker:
        """Create delete user worker"""
        worker = DeleteUserWorker(client, user_id)
        self.active_threads.append(worker)
        return worker
    
    def create_get_courses_worker(self, client: MoodleRestClient, ids: List[int] = None) -> GetCoursesWorker:
        """Create get courses worker"""
        worker = GetCoursesWorker(client, ids)
        self.active_threads.append(worker)
        return worker
    
    def create_create_course_worker(self, client: MoodleRestClient, course_data: Dict[str, Any]) -> CreateCourseWorker:
        """Create create course worker"""
        worker = CreateCourseWorker(client, course_data)
        self.active_threads.append(worker)
        return worker
    
    def create_update_course_worker(self, client: MoodleRestClient, course_data: Dict[str, Any]) -> UpdateCourseWorker:
        """Create update course worker"""
        worker = UpdateCourseWorker(client, course_data)
        self.active_threads.append(worker)
        return worker
    
    def create_delete_course_worker(self, client: MoodleRestClient, course_id: int) -> DeleteCourseWorker:
        """Create delete course worker"""
        worker = DeleteCourseWorker(client, course_id)
        self.active_threads.append(worker)
        return worker
    
    def create_get_course_content_worker(self, client: MoodleRestClient, course_id: int) -> GetCourseContentWorker:
        """Create get course content worker"""
        worker = GetCourseContentWorker(client, course_id)
        self.active_threads.append(worker)
        return worker
    
    def create_get_enrolled_users_worker(self, client: MoodleRestClient, course_id: int) -> GetEnrolledUsersWorker:
        """Create get enrolled users worker"""
        worker = GetEnrolledUsersWorker(client, course_id)
        self.active_threads.append(worker)
        return worker
    
    def create_enrol_user_worker(self, client: MoodleRestClient, user_id: int, course_id: int, role_id: int = None) -> EnrolUserWorker:
        """Create enrol user worker"""
        worker = EnrolUserWorker(client, user_id, course_id, role_id)
        self.active_threads.append(worker)
        return worker
    
    def create_unenrol_user_worker(self, client: MoodleRestClient, user_id: int, course_id: int, role_id: int = None) -> UnenrolUserWorker:
        """Create unenrol user worker"""
        worker = UnenrolUserWorker(client, user_id, course_id, role_id)
        self.active_threads.append(worker)
        return worker
    
    def create_get_groups_worker(self, client: MoodleRestClient, course_id: int) -> GetGroupsWorker:
        """Create get groups worker"""
        worker = GetGroupsWorker(client, course_id)
        self.active_threads.append(worker)
        return worker
    
    def create_create_group_worker(self, client: MoodleRestClient, group_data: Dict[str, Any]) -> CreateGroupWorker:
        """Create create group worker"""
        worker = CreateGroupWorker(client, group_data)
        self.active_threads.append(worker)
        return worker
    
    def create_delete_group_worker(self, client: MoodleRestClient, group_id: int) -> DeleteGroupWorker:
        """Create delete group worker"""
        worker = DeleteGroupWorker(client, group_id)
        self.active_threads.append(worker)
        return worker
    
    def create_add_group_members_worker(self, client: MoodleRestClient, group_id: int, user_ids: List[int]) -> AddGroupMembersWorker:
        """Create add group members worker"""
        worker = AddGroupMembersWorker(client, group_id, user_ids)
        self.active_threads.append(worker)
        return worker
    
    def create_remove_group_members_worker(self, client: MoodleRestClient, group_id: int, user_ids: List[int]) -> RemoveGroupMembersWorker:
        """Create remove group members worker"""
        worker = RemoveGroupMembersWorker(client, group_id, user_ids)
        self.active_threads.append(worker)
        return worker
    
    def create_get_group_members_worker(self, client: MoodleRestClient, group_id: int) -> GetGroupMembersWorker:
        """Create get group members worker"""
        worker = GetGroupMembersWorker(client, group_id)
        self.active_threads.append(worker)
        return worker
    
    def create_get_grade_items_worker(self, client: MoodleRestClient, course_id: int) -> GetGradeItemsWorker:
        """Create get grade items worker"""
        worker = GetGradeItemsWorker(client, course_id)
        self.active_threads.append(worker)
        return worker
    
    def create_get_grades_worker(self, client: MoodleRestClient, course_id: int, user_id: int = None) -> GetGradesWorker:
        """Create get grades worker"""
        worker = GetGradesWorker(client, course_id, user_id)
        self.active_threads.append(worker)
        return worker
    
    def create_update_grades_worker(self, client: MoodleRestClient, course_id: int, grade_items: List[Dict[str, Any]]) -> UpdateGradesWorker:
        """Create update grades worker"""
        worker = UpdateGradesWorker(client, course_id, grade_items)
        self.active_threads.append(worker)
        return worker
    
    def create_get_roles_worker(self, client: MoodleRestClient) -> GetRolesWorker:
        """Create get roles worker"""
        worker = GetRolesWorker(client)
        self.active_threads.append(worker)
        return worker
    
    def create_assign_role_worker(self, client: MoodleRestClient, user_id: int, role_id: int, context_id: int, context_level: str = 'course') -> AssignRoleWorker:
        """Create assign role worker"""
        worker = AssignRoleWorker(client, user_id, role_id, context_id, context_level)
        self.active_threads.append(worker)
        return worker
    
    def create_unassign_role_worker(self, client: MoodleRestClient, user_id: int, role_id: int, context_id: int, context_level: str = 'course') -> UnassignRoleWorker:
        """Create unassign role worker"""
        worker = UnassignRoleWorker(client, user_id, role_id, context_id, context_level)
        self.active_threads.append(worker)
        return worker
    
    def create_get_assignment_submissions_worker(self, client: MoodleRestClient, assignment_id: int) -> GetAssignmentSubmissionsWorker:
        """Create get assignment submissions worker"""
        worker = GetAssignmentSubmissionsWorker(client, assignment_id)
        self.active_threads.append(worker)
        return worker
    
    def create_send_message_worker(self, client: MoodleRestClient, user_id: int, message: str, message_format: str = 'MOODLE') -> SendMessageWorker:
        """Create send message worker"""
        worker = SendMessageWorker(client, user_id, message, message_format)
        self.active_threads.append(worker)
        return worker
    
    def create_upload_file_worker(self, client: MoodleRestClient, filepath: str, filename: str, **kwargs) -> UploadFileWorker:
        """Create upload file worker"""
        worker = UploadFileWorker(client, filepath, filename, **kwargs)
        self.active_threads.append(worker)
        return worker
    
    def create_csv_bulk_upload_worker(self, client: MoodleRestClient, csv_filepath: str, delimiter: str = ',', encoding: str = 'utf-8', custom_mappings: Dict[str, str] = None) -> CSVBulkUploadWorker:
        """Create CSV bulk upload worker"""
        worker = CSVBulkUploadWorker(client, csv_filepath, delimiter, encoding, custom_mappings)
        self.active_threads.append(worker)
        return worker
    
    def create_upload_user_picture_worker(self, client: MoodleRestClient, user_id: int, picture_filepath: str, overwrite: bool = True) -> UploadUserPictureWorker:
        """Create upload user picture worker"""
        worker = UploadUserPictureWorker(client, user_id, picture_filepath, overwrite)
        self.active_threads.append(worker)
        return worker
    
    def create_get_calendar_events_worker(self, client: MoodleRestClient, **kwargs) -> GetCalendarEventsWorker:
        """Create get calendar events worker"""
        worker = GetCalendarEventsWorker(client, **kwargs)
        self.active_threads.append(worker)
        return worker
    
    def create_submit_backup_worker(self, client: MoodleRestClient, course_id: int, settings: Dict[str, Any] = None) -> SubmitBackupWorker:
        """Create submit backup worker"""
        worker = SubmitBackupWorker(client, course_id, settings)
        self.active_threads.append(worker)
        return worker
    
    def create_get_backup_status_worker(self, client: MoodleRestClient, backup_id: str) -> GetBackupStatusWorker:
        """Create get backup status worker"""
        worker = GetBackupStatusWorker(client, backup_id)
        self.active_threads.append(worker)
        return worker
    
    def create_submit_restore_worker(self, client: MoodleRestClient, backup_file_path: str, target_course_id: int, settings: Dict[str, Any] = None) -> SubmitRestoreWorker:
        """Create submit restore worker"""
        worker = SubmitRestoreWorker(client, backup_file_path, target_course_id, settings)
        self.active_threads.append(worker)
        return worker
    
    def cleanup_finished_threads(self):
        """Clean up finished threads"""
        finished_threads = [thread for thread in self.active_threads if thread.isFinished()]
        for thread in finished_threads:
            thread.deleteLater()
            self.active_threads.remove(thread)
    
    def stop_all_threads(self):
        """Stop all active threads"""
        for thread in self.active_threads:
            if thread.isRunning():
                thread.stop()
        self.active_threads.clear()
