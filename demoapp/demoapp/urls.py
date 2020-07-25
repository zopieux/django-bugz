from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path("admin/", admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path("", include("bugz.urls")),
]

if settings.DEBUG:
    import debug_toolbar
    import django.contrib.staticfiles.views

    urlpatterns.extend(
        [
            path("__debug__/", include(debug_toolbar.urls)),
            re_path(
                r'^static/(?P<path>.*)$',
                django.contrib.staticfiles.views.serve,
            ),
        ]
    )
