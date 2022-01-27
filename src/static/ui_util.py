searchbox = document.getElementById("searchbox")
results_element = document.getElementById("results")
tree_element = document.getElementById("thetree")


def find_attr_parents(element, attr):
    val = element.getAttribute(attr)
    if val and len(val) > 0:
        return val
    parent = element.parentElement
    if parent:
        return find_attr_parents(parent, attr)
