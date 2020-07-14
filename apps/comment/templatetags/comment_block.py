from django import template

register = template.Library()


@register.inclusion_tag('comment/tags/block.html')
def comment_block(comment_tree, iterations=0):
    return {
        'comment_tree': comment_tree,
        'iterations': iterations + 1,
    }
