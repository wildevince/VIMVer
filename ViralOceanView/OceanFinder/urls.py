from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path('', views.index.as_view(), name='index'),
    path('finder', views.finder.as_view(), name='finder'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)