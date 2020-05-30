from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import (
    BaseUpdateView,
    FormMixin,
    UpdateView,
)
from rules.contrib.views import PermissionRequiredMixin

from bugz import models, forms


class ListTicketView(FormMixin, ListView):
    template_name = "bugz/ticket-list.html"
    context_object_name = "tickets"
    form_class = forms.SearchForm

    def get(self, request, *args, **kwargs):
        self.form = self.get_form()
        self.form.is_valid()
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = {
            "initial": self.get_initial(),
            "prefix": self.get_prefix(),
            "data": self.request.GET,
        }
        return kwargs

    def get_queryset(self):
        qs = models.Ticket.objects.select_related(
            "assignee", "dupe_of"
        ).prefetch_related("blocked_by", "labels")
        return self.form.apply_qs(qs)


class CreateLabelView(PermissionRequiredMixin, CreateView):
    model = models.Label
    fields = ("name", "description", "color")
    permission_required = "bugz.can_create_label"


class CreateTicketView(PermissionRequiredMixin, CreateView):
    template_name = "bugz/ticket-create.html"
    model = models.Ticket
    fields = ("title", "description", "assignee", "blocked_by", "dupe_of", "labels")
    permission_required = "bugz.can_create_ticket"


class DetailTicketView(FormMixin, DetailView):
    template_name = "bugz/ticket-detail.html"
    model = models.Ticket
    form_class = forms.CommentForm

    def get_context_data(self, **kwargs):
        log = list(models.build_ticket_log(self.object))[::-1]
        return {
            **super().get_context_data(**kwargs),
            "log": log,
        }


class CommentTicketView(PermissionRequiredMixin, BaseUpdateView):
    model = models.Ticket
    form_class = forms.CommentForm
    permission_required = "bugz.can_comment_ticket"
    http_method_names = ["post"]

    def get_form_kwargs(self):
        return FormMixin.get_form_kwargs(self)

    def form_valid(self, form):
        models.save_ticket_comment(
            self.object, self.request.user, form.cleaned_data["comment"]
        )
        return redirect(self.object.get_absolute_url())

    def form_invalid(self, form):
        return JsonResponse("no", safe=False)


class UpdateTicketView(PermissionRequiredMixin, UpdateView):
    model = models.Ticket
    fields = (
        "title",
        "description",
        "open",
        "assignee",
        "blocked_by",
        "dupe_of",
        "labels",
        "locked",
    )
