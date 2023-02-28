from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", include("feeds.urls")),
    path("", include("profiles.urls")),
    path("", include("notifications.urls")),
    path("", include("trends.urls")),
    path("", include("tweets.urls")),
    path("", include("twitterx.urls")),
    path("", include("users.urls")),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)