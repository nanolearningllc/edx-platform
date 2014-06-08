"""
Acceptance tests for Studio related to the split_test module.
"""

from ..fixtures.course import CourseFixture, XBlockFixtureDesc

from ..pages.studio.component_editor import ComponentEditorView
from test_studio_container import ContainerBase
from ..pages.studio.utils import add_advanced_component
from xmodule.partitions.partitions import Group, UserPartition


class SplitTest(ContainerBase):
    """
    Tests for creating and editing split test instances in Studio.
    """
    __test__ = True

    def setup_fixtures(self):
        course_fix = CourseFixture(
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run'],
            self.course_info['display_name']
        )

        course_fix.add_advanced_settings(
            {
                u"advanced_modules": ["split_test"],
                u"user_partitions": [
                    UserPartition(0, 'Configuration alpha,beta', 'first', [Group("0", 'alpha'), Group("1", 'beta')]).to_json(),
                    UserPartition(1, 'Configuration 0,1,2', 'second', [Group("0", 'Group 0'), Group("1", 'Group 1'), Group("2", 'Group 2')]).to_json()
                ]
            }
        )

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Section').add_children(
                XBlockFixtureDesc('sequential', 'Test Subsection').add_children(
                    XBlockFixtureDesc('vertical', 'Test Unit')
                )
            )
        ).install()

        self.user = course_fix.user

    def test_create_and_select_group_configuration(self):
        """
        Tests creating a split test instance on the unit page, and then
        assigning the group configuration.
        """
        unit = self.go_to_unit_page(make_draft=True)
        add_advanced_component(unit, 0, 'split_test')
        container = self.go_to_container_page()
        container.edit()
        component_editor = ComponentEditorView(self.browser, container.locator)
        component_editor.set_select_value_and_save('Group Configuration', 'Configuration alpha,beta')
        self.verify_ordering(container, [{'alpha': []}, {'beta': []}])
        # TODO: check both are in active group

        # Switch to the other group configuration.
        container.edit()
        component_editor = ComponentEditorView(self.browser, container.locator)
        component_editor.set_select_value_and_save('Group Configuration', 'Configuration 0,1,2')
        expected_ordering = [{'0': []}, {'1': []}, {'2': []}, {'alpha': []}, {'beta': []}]
        self.verify_ordering(container, expected_ordering)
        # TODO: check active vs. inactive groups.

        # Reload the page to make sure the groups were persisted.
        container = self.go_to_container_page()
        self.verify_ordering(container, expected_ordering)
