from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', IndexView.as_view(), name="index"),
    url(r'^basic/$', PersonBasicView.as_view(), name="basic"),
    url(r'^persons/$', PersonView.as_view(), name="persons"),
    url(r'^equipment/(?P<person__id>\d+)/$', EquipmentView.as_view(), name="equipment"),
]
