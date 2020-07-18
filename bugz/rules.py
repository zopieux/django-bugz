from rules import predicate, is_staff, add_rule, is_authenticated


@predicate
def ticket_is_unlocked(user, ticket):
    return not ticket.locked


@predicate
def is_own_ticket(user, ticket):
    return ticket.created_by == user


@predicate
def is_own_comment_author(user, revision):
    return revision.user == user


can_edit_ticket = is_staff | (
    is_authenticated & ticket_is_unlocked & is_own_ticket
)

add_rule("bugz.can_comment_ticket", is_staff | ticket_is_unlocked)
add_rule("bugz.can_edit_ticket", can_edit_ticket)
add_rule("bugz.can_create_ticket", is_authenticated)
add_rule("bugz.can_list_labels", is_authenticated)
add_rule("bugz.can_create_label", is_staff)
add_rule(
    "bugz.can_edit_comment",
    is_staff | (is_authenticated & is_own_comment_author),
)
add_rule("bugz.can_lock_ticket", is_staff)
add_rule("bugz.can_delete_comment", is_staff)
add_rule("bugz.can_delete_ticket", is_staff)
