from devour.django import common


def _get_event(created=False, deleted=False):
    """
    returns CRUD event type. if you need a custom
    event, set value in context
    """

    event = None
    if deleted:
        event = common.DELETE_EVENT
    elif created:
        event = common.CREATE_EVENT
    elif created is False and deleted is False:
        event = common.UPDATE_EVENT

    return event
