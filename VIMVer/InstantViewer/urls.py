from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.home, name="home_page"),
    path('delete_all/', views.delete_all, name="destroyThemAll"),
    path('download/<str:filepath>/', views.export, name='export'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
