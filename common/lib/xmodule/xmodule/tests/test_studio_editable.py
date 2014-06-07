"""
Tests for StudioEditableModule.
"""

from xmodule.tests.test_vertical import BaseVerticalModuleTest


class StudioEditableModuleTestCase(BaseVerticalModuleTest):
    def test_render_reorderable_children(self):
        """
        Test the behavior of render_reorderable_children.
        """
        reorderable_items = set()
        context = {
            'runtime_type': 'studio',
            'container_view': True,
            'reorderable_items': reorderable_items,
            'read_only': False,
            'root_xblock': self.vertical,
        }

        # Both children of the vertical should be rendered as reorderable
        self.module_system.render(self.vertical, 'author_view', context).content
        self.assertIn(self.vertical.get_children()[0].location, reorderable_items)
        self.assertIn(self.vertical.get_children()[1].location, reorderable_items)
