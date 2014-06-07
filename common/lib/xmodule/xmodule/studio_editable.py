"""
Mixin to support editing in Studio.
"""
from xmodule.x_module import module_attr

class StudioEditableModule(object):
    """
    Helper methods for supporting Studio editing of xblocks/xmodules.

    This class is only intended to be used with an XModule, as it assumes the existence of
    self.descriptor and self.system.
    """

    def render_children(self, context, fragment, can_reorder=False, can_add=False):
        """
        Renders the children of the module with HTML appropriate for Studio. If can_reorder is True,
        then the children will be rendered to support drag and drop.
        """
        contents = []

        for child in self.descriptor.get_children():  # pylint: disable=E1101
            if can_reorder:
                context['reorderable_items'].add(child.location)
            child_module = self.system.get_module(child)  # pylint: disable=E1101
            rendered_child = child_module.render(StudioEditableModule._get_preview_view_name(child_module), context)
            fragment.add_frag_resources(rendered_child)

            contents.append({
                'id': child.location.to_deprecated_string(),
                'content': rendered_child.content
            })

        fragment.add_content(self.system.render_template("studio_render_children_view.html", {  # pylint: disable=E1101
            'items': contents,
            'xblock_context': context,
            'can_add': can_add,
            'can_reorder': can_reorder,
        }))

    @staticmethod
    def _get_preview_view_name(block):
        return 'author_view' if hasattr(block, 'author_view') else 'student_view'

    def get_preview_view_name(self):
        return StudioEditableModule._get_preview_view_name(self)


class StudioEditableDescriptor(object):
    author_view = module_attr('author_view')
    get_preview_view_name = module_attr('get_preview_view_name')
    has_author_view = True
