from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', PersonView.as_view(), name="persons"),
    url(r'^equipment/(?P<person__id>\d+)/$', EquipmentView.as_view(), name="equipment"),
]
