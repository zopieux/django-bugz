import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from bugz import models


class BugzTestCase(TestCase):
    def setUp(self):
        self.l1 = models.Label.objects.create(name="urgent")
        self.l2 = models.Label.objects.create(name="minor")
        self.l3 = models.Label.objects.create(name="easy")
        self.u1 = get_user_model().objects.create(username="zopieux")
        self.u2 = get_user_model().objects.create(username="seirl")
        self.t1 = models.Ticket.objects.create(
            authored_by=self.u1, title="test title", description="the description"
        )
        self.t2 = models.Ticket.objects.create(
            authored_by=self.u2, title="big issue", description="onoes"
        )

    def test_create_update(self):
        self.t1.title = "the new title"
        self.t1.assignee = self.u2
        update = models.save_ticket_update(
            self.t1, self.u2, labels=[self.l1, self.l2], blocked_by=[self.t2]
        )
        self.assertDictEqual(
            json.loads(update.old_value),
            {"title": "test title", "assignee": None, "labels": [], "blocked_by": []},
        )
        self.t1.refresh_from_db()
        self.assertSetEqual(set(self.t1.labels.all()), {self.l1, self.l2})
        self.assertSetEqual(set(self.t1.blocked_by.all()), {self.t2})

    def test_event_log(self):
        self.t1.title = "title v2"
        models.save_ticket_update(self.t1, self.u1)

        self.t1.open = False
        models.save_ticket_update(self.t1, self.u1)

        self.t1.assignee = self.u2
        models.save_ticket_update(self.t1, self.u1)

        models.save_ticket_comment(self.t1, self.u2, "hello world")

        self.t1.assignee = None
        models.save_ticket_update(self.t1, self.u1)

        models.save_ticket_update(self.t1, self.u1, labels=[self.l1, self.l2])
        models.save_ticket_update(self.t1, self.u1, blocked_by=[self.t2])
        models.save_ticket_update(self.t1, self.u1, labels=[self.l2])
        models.save_ticket_update(self.t1, self.u1, blocked_by=[self.t1])

        log = list(models.build_ticket_log(self.t1))[::-1]
        self.assertEqual(len(log), 10)

        self.assertEqual(log[0].field, "title")
        self.assertEqual(log[0].authored_by, self.u1)
        self.assertEqual(log[0].old_value, "test title")
        self.assertEqual(log[0].new_value, "title v2")

        self.assertEqual(log[1].field, "open")
        self.assertEqual(log[1].old_value, True)
        self.assertEqual(log[1].new_value, False)

        self.assertEqual(log[2].field, "assignee")
        self.assertEqual(log[2].old_value, None)
        self.assertEqual(log[2].new_value, self.u2)

        self.assertEqual(log[3].field, "comment")
        self.assertEqual(log[3].authored_by, self.u2)
        self.assertEqual(log[3].old_value, None)
        self.assertEqual(log[3].new_value, "hello world")

        self.assertEqual(log[4].field, "assignee")
        self.assertEqual(log[4].old_value, self.u2)
        self.assertEqual(log[4].new_value, None)

        self.assertEqual(log[5].field, "labels")
        self.assertEqual(log[5].old_value, None)
        self.assertEqual(log[5].new_value, {self.l1, self.l2})

        self.assertEqual(log[6].field, "blocked_by")
        self.assertEqual(log[6].old_value, None)
        self.assertEqual(log[6].new_value, {self.t2})

        self.assertEqual(log[7].field, "labels")
        self.assertEqual(log[7].old_value, {self.l1})
        self.assertEqual(log[7].new_value, None)

        self.assertEqual(log[8].field, "blocked_by")
        self.assertEqual(log[8].old_value, None)
        self.assertEqual(log[8].new_value, {self.t1})

        self.assertEqual(log[9].field, "blocked_by")
        self.assertEqual(log[9].old_value, {self.t2})
        self.assertEqual(log[9].new_value, None)

        # Delete a referenced label and check it's handled properly.
        self.l1.delete()
        log = list(models.build_ticket_log(self.t1))[::-1]
        self.assertEqual(log[5].field, "labels")
        self.assertEqual(log[5].old_value, None)
        # No l1 anymore.
        self.assertEqual(log[5].new_value, {self.l2})
        # Event #7 for label was silenced since the label doesn't exist.
        self.assertEqual(len(log), 9)
        self.assertEqual(log[7].field, "blocked_by")
