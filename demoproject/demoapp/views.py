from django.views.generic import TemplateView
from djangow2ui.grid import W2UIGridView
from .models import *

class IndexView(TemplateView):
    template_name = 'index.html'

class PersonBasicView(W2UIGridView):
    model  = Person
    fields = ('id', 'fname', 'lname', 'email', 'sdate')
    template_name = "basic.html"

class PersonView(PersonBasicView):
    template_name = "persons.html"
    class W2UI:
        name = "persons"
    def get_context_data(self, **kwargs):
        context = super(PersonView, self).get_context_data(**kwargs)
        context['equipment'] = EquipmentView()
        return context

class EquipmentView(W2UIGridView):
    model = Equipment
    fields = ('id', 'name')
    editable = False
    class W2UI:
        show__header = False
        show__toolbar = False
        show__footer = False
    def getQueryset(self, request, *args, **kwargs):
        qs = super(EquipmentView, self).getQueryset(request, *args, **kwargs)
        return qs.filter(person__id = kwargs['person__id'])
