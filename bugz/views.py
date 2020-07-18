import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.views.decorators.csrf import requires_csrf_token
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
    fields = ("title", "description")
    permission_required = "bugz.can_create_ticket"


class DetailTicketView(FormMixin, DetailView):
    template_name = "bugz/ticket-detail.html"
    model = models.Ticket
    form_class = forms.CommentForm

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related('labels', 'blocked_by')
            .select_related('assignee', 'dupe_of')
        )

    def get_context_data(self, **kwargs):
        log = list(models.build_ticket_log(self.object))[::-1]
        return {
            **super().get_context_data(**kwargs),
            # Minus one because the description is a fake comment.
            "comment_count": sum(1 for l in log if l.field == "comment") - 1,
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
        comment = models.save_ticket_comment(
            self.object, self.request.user, form.cleaned_data["comment"]
        )
        url = self.object.get_absolute_url()
        return redirect(f"{url}#{models.get_comment_hash(comment)}")

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


class JsonBodyMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            self.request_json = self.get_request_json()

        return super().dispatch(request, *args, **kwargs)

    def get_request_json(self):
        try:
            return json.loads(self.request.body.decode())
        except:
            return None


class JSLabelView(JsonBodyMixin, PermissionRequiredMixin, View):
    def get_permission_required(self):
        if self.request.method == "GET":
            return "bugz.can_list_labels"
        else:
            return "bugz.can_edit_ticket"

    def get_permission_object(self):
        if self.request.method == "POST":
            return self.get_object()

    def get_object(self):
        pk = self.request_json["ticket"]
        return get_object_or_404(models.Ticket, pk=pk)

    def get(self, request, *args, **kwargs):
        labels = [
            dict(pk=label.pk, name=label.name, color=label.color)
            for label in models.Label.objects.all()
        ]
        return JsonResponse(labels, safe=False)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        models.save_ticket_update(
            ticket, self.request.user, labels=self.request_json["labels"]
        )
        return HttpResponse(status=204)
