import requests
from urllib.parse import urljoin
from django.conf import settings
from .models import MoodlePlatform

class MoodleAPI:
    def __init__(self, platform_id):
        self.platform = MoodlePlatform.objects.get(id=platform_id)
        self.base_url = self.platform.url
        self.api_key = self.platform.api_key
        self.endpoint = self.platform.api_endpoint
    
    def _make_request(self, function, **params):
        url = urljoin(self.base_url, self.endpoint)
        params.update({
            'wstoken': self.api_key,
            'moodlewsrestformat': 'json',
            'wsfunction': function
        })
        
        try:
            response = requests.get(url, params=params, timeout=settings.MOODLE_API_SETTINGS['DEFAULT_TIMEOUT'])
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making Moodle API request: {e}")
            return None
    
    def get_site_info(self):
        return self._make_request('core_webservice_get_site_info')
    
    def get_courses(self):
        return self._make_request('core_course_get_courses')
    
    def get_user_courses(self, userid):
        return self._make_request('core_enrol_get_users_courses', userid=userid)
    
    def get_user_by_field(self, field, value):
        return self._make_request('core_user_get_users_by_field', field=field, values=[value])
    
    # Add more API methods as needed