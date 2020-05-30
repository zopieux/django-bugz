from django.contrib import admin

from bugz import models


class TicketAdmin(admin.ModelAdmin):
    raw_id_fields = ["assignee", "blocked_by", "dupe_of"]

    def save_model(self, request, obj, form, change):
        if not change:
            return super().save_model(request, obj, form, change)
        data = form.cleaned_data
        return models.save_ticket_update(
            ticket=obj,
            authored_by=request.user,
            blocked_by=[t.pk for t in data["blocked_by"]],
            labels=[l.pk for l in data["labels"]],
        )


class LabelAdmin(admin.ModelAdmin):
    fields = ["name", "description", "color"]


admin.site.register(models.Ticket, TicketAdmin)
admin.site.register(models.Label, LabelAdmin)
