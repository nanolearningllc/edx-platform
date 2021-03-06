"""
Unit tests for getting the list of courses for a user through iterating all courses and
by reversing group name formats.
"""
import random

from chrono import Timer
from mock import patch, Mock

from django.test import RequestFactory

from contentstore.views.course import _accessible_courses_list, _accessible_courses_list_from_groups
from contentstore.utils import delete_course_and_groups, reverse_course_url
from contentstore.tests.utils import AjaxEnabledTestClient
from student.tests.factories import UserFactory
from student.roles import CourseInstructorRole, CourseStaffRole, GlobalStaff
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.locations import SlashSeparatedCourseKey
from xmodule.modulestore.django import modulestore
from xmodule.error_module import ErrorDescriptor

TOTAL_COURSES_COUNT = 500
USER_COURSES_COUNT = 50


class TestCourseListing(ModuleStoreTestCase):
    """
    Unit tests for getting the list of courses for a logged in user
    """
    def setUp(self):
        """
        Add a user and a course
        """
        super(TestCourseListing, self).setUp()
        # create and log in a staff user.
        # create and log in a non-staff user
        self.user = UserFactory()
        self.factory = RequestFactory()
        self.request = self.factory.get('/course')
        self.request.user = self.user
        self.client = AjaxEnabledTestClient()
        self.client.login(username=self.user.username, password='test')

    def _create_course_with_access_groups(self, course_location, user=None):
        """
        Create dummy course with 'CourseFactory' and role (instructor/staff) groups
        """
        course = CourseFactory.create(
            org=course_location.org,
            number=course_location.course,
            run=course_location.run
        )

        if user is not None:
            for role in [CourseInstructorRole, CourseStaffRole]:
                role(course.id).add_users(user)

        return course

    def tearDown(self):
        """
        Reverse the setup
        """
        self.client.logout()
        ModuleStoreTestCase.tearDown(self)

    def test_get_course_list(self):
        """
        Test getting courses with new access group format e.g. 'instructor_edx.course.run'
        """
        course_location = SlashSeparatedCourseKey('Org1', 'Course1', 'Run1')
        self._create_course_with_access_groups(course_location, self.user)

        # get courses through iterating all courses
        courses_list = _accessible_courses_list(self.request)
        self.assertEqual(len(courses_list), 1)

        # get courses by reversing group name formats
        courses_list_by_groups = _accessible_courses_list_from_groups(self.request)
        self.assertEqual(len(courses_list_by_groups), 1)
        # check both course lists have same courses
        self.assertEqual(courses_list, courses_list_by_groups)

    def test_errored_course_global_staff(self):
        """
        Test the course list for global staff when get_course returns an ErrorDescriptor
        """
        GlobalStaff().add_users(self.user)

        course_key = SlashSeparatedCourseKey('Org1', 'Course1', 'Run1')
        self._create_course_with_access_groups(course_key, self.user)

        with patch('xmodule.modulestore.mongo.base.MongoKeyValueStore', Mock(side_effect=Exception)):
            self.assertIsInstance(modulestore().get_course(course_key), ErrorDescriptor)

            # get courses through iterating all courses
            courses_list = _accessible_courses_list(self.request)
            self.assertEqual(courses_list, [])

            # get courses by reversing group name formats
            courses_list_by_groups = _accessible_courses_list_from_groups(self.request)
            self.assertEqual(courses_list_by_groups, [])

    def test_errored_course_regular_access(self):
        """
        Test the course list for regular staff when get_course returns an ErrorDescriptor
        """
        GlobalStaff().remove_users(self.user)
        CourseStaffRole(SlashSeparatedCourseKey('Non', 'Existent', 'Course')).add_users(self.user)

        course_key = SlashSeparatedCourseKey('Org1', 'Course1', 'Run1')
        self._create_course_with_access_groups(course_key, self.user)

        with patch('xmodule.modulestore.mongo.base.MongoKeyValueStore', Mock(side_effect=Exception)):
            self.assertIsInstance(modulestore().get_course(course_key), ErrorDescriptor)

            # get courses through iterating all courses
            courses_list = _accessible_courses_list(self.request)
            self.assertEqual(courses_list, [])

            # get courses by reversing group name formats
            courses_list_by_groups = _accessible_courses_list_from_groups(self.request)
            self.assertEqual(courses_list_by_groups, [])
            self.assertEqual(courses_list, courses_list_by_groups)

    def test_get_course_list_with_invalid_course_location(self):
        """
        Test getting courses with invalid course location (course deleted from modulestore).
        """
        course_key = SlashSeparatedCourseKey('Org', 'Course', 'Run')
        self._create_course_with_access_groups(course_key, self.user)

        # get courses through iterating all courses
        courses_list = _accessible_courses_list(self.request)
        self.assertEqual(len(courses_list), 1)

        # get courses by reversing group name formats
        courses_list_by_groups = _accessible_courses_list_from_groups(self.request)
        self.assertEqual(len(courses_list_by_groups), 1)
        # check both course lists have same courses
        self.assertEqual(courses_list, courses_list_by_groups)

        # now delete this course and re-add user to instructor group of this course
        delete_course_and_groups(course_key, commit=True)

        CourseInstructorRole(course_key).add_users(self.user)

        # test that get courses through iterating all courses now returns no course
        courses_list = _accessible_courses_list(self.request)
        self.assertEqual(len(courses_list), 0)

    def test_course_listing_performance(self):
        """
        Create large number of courses and give access of some of these courses to the user and
        compare the time to fetch accessible courses for the user through traversing all courses and
        reversing django groups
        """
        # create list of random course numbers which will be accessible to the user
        user_course_ids = random.sample(range(TOTAL_COURSES_COUNT), USER_COURSES_COUNT)

        # create courses and assign those to the user which have their number in user_course_ids
        for number in range(TOTAL_COURSES_COUNT):
            org = 'Org{0}'.format(number)
            course = 'Course{0}'.format(number)
            run = 'Run{0}'.format(number)
            course_location = SlashSeparatedCourseKey(org, course, run)
            if number in user_course_ids:
                self._create_course_with_access_groups(course_location, self.user)
            else:
                self._create_course_with_access_groups(course_location)

        # time the get courses by iterating through all courses
        with Timer() as iteration_over_courses_time_1:
            courses_list = _accessible_courses_list(self.request)
        self.assertEqual(len(courses_list), USER_COURSES_COUNT)

        # time again the get courses by iterating through all courses
        with Timer() as iteration_over_courses_time_2:
            courses_list = _accessible_courses_list(self.request)
        self.assertEqual(len(courses_list), USER_COURSES_COUNT)

        # time the get courses by reversing django groups
        with Timer() as iteration_over_groups_time_1:
            courses_list = _accessible_courses_list_from_groups(self.request)
        self.assertEqual(len(courses_list), USER_COURSES_COUNT)

        # time again the get courses by reversing django groups
        with Timer() as iteration_over_groups_time_2:
            courses_list = _accessible_courses_list_from_groups(self.request)
        self.assertEqual(len(courses_list), USER_COURSES_COUNT)

        # test that the time taken by getting courses through reversing django groups is lower then the time
        # taken by traversing through all courses (if accessible courses are relatively small)
        self.assertGreaterEqual(iteration_over_courses_time_1.elapsed, iteration_over_groups_time_1.elapsed)
        self.assertGreaterEqual(iteration_over_courses_time_2.elapsed, iteration_over_groups_time_2.elapsed)

    def test_get_course_list_with_same_course_id(self):
        """
        Test getting courses with same id but with different name case. Then try to delete one of them and
        check that it is properly deleted and other one is accessible
        """
        course_location_caps = SlashSeparatedCourseKey('Org', 'COURSE', 'Run')
        self._create_course_with_access_groups(course_location_caps, self.user)

        # get courses through iterating all courses
        courses_list = _accessible_courses_list(self.request)
        self.assertEqual(len(courses_list), 1)

        # get courses by reversing group name formats
        courses_list_by_groups = _accessible_courses_list_from_groups(self.request)
        self.assertEqual(len(courses_list_by_groups), 1)
        # check both course lists have same courses
        self.assertEqual(courses_list, courses_list_by_groups)

        # now create another course with same course_id but different name case
        course_location_camel = SlashSeparatedCourseKey('Org', 'Course', 'Run')
        self._create_course_with_access_groups(course_location_camel, self.user)

        # test that get courses through iterating all courses returns both courses
        courses_list = _accessible_courses_list(self.request)
        self.assertEqual(len(courses_list), 2)

        # test that get courses by reversing group name formats returns both courses
        courses_list_by_groups = _accessible_courses_list_from_groups(self.request)
        self.assertEqual(len(courses_list_by_groups), 2)

        # now delete first course (course_location_caps) and check that it is no longer accessible
        delete_course_and_groups(course_location_caps, commit=True)

        # test that get courses through iterating all courses now returns one course
        courses_list = _accessible_courses_list(self.request)
        self.assertEqual(len(courses_list), 1)

        # test that get courses by reversing group name formats also returns one course
        courses_list_by_groups = _accessible_courses_list_from_groups(self.request)
        self.assertEqual(len(courses_list_by_groups), 1)

        # now check that deleted course is not accessible
        outline_url = reverse_course_url('course_handler', course_location_caps)
        response = self.client.get(outline_url, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 403)

        # now check that other course is accessible
        outline_url = reverse_course_url('course_handler', course_location_camel)
        response = self.client.get(outline_url, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

    def test_course_listing_errored_deleted_courses(self):
        """
        Create good courses, courses that won't load, and deleted courses which still have
        roles. Test course listing.
        """
        course_location = SlashSeparatedCourseKey('testOrg', 'testCourse', 'RunBabyRun')
        self._create_course_with_access_groups(course_location, self.user)

        course_location = SlashSeparatedCourseKey('testOrg', 'doomedCourse', 'RunBabyRun')
        self._create_course_with_access_groups(course_location, self.user)
        modulestore().delete_course(course_location)

        course_location = SlashSeparatedCourseKey('testOrg', 'erroredCourse', 'RunBabyRun')
        course = self._create_course_with_access_groups(course_location, self.user)
        course_db_record = modulestore()._find_one(course.location)
        course_db_record.setdefault('metadata', {}).get('tabs', []).append({"type": "wiko", "name": "Wiki" })
        modulestore().collection.update(
            {'_id': course_db_record['_id']},
            {'$set': {
                'metadata.tabs': course_db_record['metadata']['tabs'],
            }},
        )

        courses_list = _accessible_courses_list_from_groups(self.request)
        self.assertEqual(len(courses_list), 1, courses_list)
