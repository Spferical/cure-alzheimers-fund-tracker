from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'authors', views.AuthorViewSet)
router.register(r'papers', views.PaperViewSet)
router.register(r'projects', views.ProjectViewSet)

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^api/', include(router.urls))
]