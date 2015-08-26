from django.db.models import Q
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.db.models.constants import LOOKUP_SEP
from django.views.generic import View, TemplateView
from django.utils.decorators import method_decorator
from django.core.exceptions import ImproperlyConfigured 
from django.views.decorators.csrf import ensure_csrf_cookie
import django.db.models.fields as djf
import json, copy

class W2UIGridView(TemplateView):
    http_method_names = TemplateView.http_method_names + [ 'json' ]
    template_name = "w2ui/grid.html"
    model = None
    queryset = None
    editable = True
    fields = ()
    _default_settings = {
        "name"   : "grid",
        "method" : "JSON",
        "url"    : ".",
        "show"   : {
            "header"        : True,
            "toolbar"       : True,
            "toolbarAdd"    : True,
            "toolbarDelete" : True,
            "toolbarSave"   : True,
            "toolbarEdit"   : True,
            "footer"        : True,
            "lineNumbers"   : True,
            "selectColumn"  : True,
            "expandColumn"  : False,
        },
    }

    def __init__(self, *args, **kwargs):
        super(W2UIGridView, self).__init__(*args, **kwargs)
        self.settings = copy.deepcopy(self._default_settings)
        _w2ui = getattr(self, "W2UI", None)
        for k in dir(_w2ui):
            if k.startswith('_'): continue
            pieces = k.split('__')
            s = self.settings
            for piece in pieces[:-1]:
                s = s[piece]
            s[pieces[-1]] = getattr(_w2ui, k)

        if not self.queryset and not self.model:
            raise ImproperlyConfigured("Specify model or queryset")
        if not self.queryset:
            self.queryset = self.model.objects.all()
        elif not self.model:
            self.model = self.queryset.model

        opts = self.model._meta
        self.settings["recid"] = opts.pk.name

        if not self.settings.get("header",None):
            self.settings["header"] = "List of %s" % opts.verbose_name_plural

        if not self.fields:
            self.fields = [ getattr(f,'name') for f in opts.fields ]

        self.settings["columns"] = []
        self.settings["searches"] = []
        search = {
            "field": self.settings["recid"],
            "caption": opts.pk.verbose_name,
            "type": self.get_field_type(opts.pk),
        }
        self.settings["searches"].append(search)
        for fname in self.fields:
            f = self.resolve_field(fname)
            t = self.get_field_type(f)
            field = {
                "field"    : fname,
                "caption"  : f.verbose_name,
                "sortable" : True,
                "resizable": True,
                "size"     : 1, # needed to force column rendering
            }
            if t:
                if self.editable and f.editable and f.model == self.model:
                    field["editable"] = { "type": t }
                if f != opts.pk:
                    search = {
                        "field"  : fname,
                        "caption": f.verbose_name,
                        "type"   : t,
                    }
                    self.settings["searches"].append(search)
            self.settings["columns"].append(field)

        if not self.editable:
            keys = [
                "toolbarAdd", "toolbarDelete", "toolbarSave", "toolbarEdit", "selectColumn",
            ]
            for k in keys:
                self.settings["show"][k] = False

    def get_context_data(self, **kwargs):
        context = super(W2UIGridView, self).get_context_data(**kwargs)
        context[self.settings["name"]] = self
        return context

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(W2UIGridView, self).dispatch(*args, **kwargs)

    def getQueryset(self, request, *args, **kwargs):
        return self.queryset

    def json(self, request, *args, **kwargs):
        status = 200
        try:
            qs = self.getQueryset(request, *args, **kwargs)
            req = json.loads(request.body)
            if req["cmd"] == "get-records":
                data = self.getRecords(req, qs)
            elif req["cmd"] == "delete-records":
                data = self.deleteRecords(req, qs)
            elif req["cmd"] == "save-records":
                data = self.saveRecords(req, qs)
            else:
                raise Exception("unsupported cmd '%s'" % req["cmd"])
        except Exception as e:
            status = 200
            data = {
               "status"  : "error",
               "message" : str(e),
            }
        return JsonResponse(data, safe=False, status=status)

    def getRecords(self, req, qs):
        filters = Q()
        for search in req.get("search",[]):
            if search["operator"] == "is":
                q = Q(**{'%s__exact' % search["field"] : search["value"] })
            elif search["operator"] == "between":
                q = Q(**{'%s__range' % search["field"] : search["value"] })
            elif search["operator"] == "less":
                q = Q(**{'%s__lt' % search["field"] : search["value"] })
            elif search["operator"] == "more":
                q = Q(**{'%s__gt' % search["field"] : search["value"] })
            elif search["operator"] == "in":
                q = Q(**{'%s__in' % search["field"] : search["value"] })
            elif search["operator"] == "not in":
                q = ~Q(**{'%s__in' % search["field"] : search["value"] })
            elif search["operator"] == "begins":
                q = Q(**{'%s__startswith' % search["field"] : search["value"] })
            elif search["operator"] == "contains":
                q = Q(**{'%s__contains' % search["field"] : search["value"] })
            elif search["operator"] == "null":
                q = Q(**{'%s__isnull' % search["field"] : True })
            elif search["operator"] == "not null":
                q = Q(**{'%s__isnull' % search["field"] : False })
            elif search["operator"] == "ends":
                q = Q(**{'%s__endswith' % search["field"] : search["value"] })
            else:
                raise Exception("Unsupported search operator '%s'" % search["operator"])

            if req["searchLogic"] == "OR":
                filters |= q
            else:
                filters &= q
    
        ordering = []
        for sort in req.get("sort",[]):
            order = sort["field"]
            if sort["direction"] == "desc":
                order = "-" + order
            ordering.append(order)
    
        limits = (req["offset"], req["offset"]+req["limit"])
       
        records = qs.filter(filters)
        records = records.order_by(*ordering)
        count   = records.count()
        page    = records.values(*self.fields)[limits[0] : limits[1]]

        data = {
            "status":  "success",
            "total":   count,
            "records": list(page),
        }
        return data
        
    def deleteRecords(self, req, qs):
        if not self.editable:
            raise Exception("Grid is not editable")
        qs.filter(pk__in=req["selected"]).delete()
        return { "status":  "success" }

    def saveRecords(self, req, qs):
        if not self.editable:
            raise Exception("Grid is not editable")
        for row in req["changes"]:
            obj = qs.get(pk=row["recid"])
            del row["recid"]
            for k,v in row.items():
                setattr(obj,k,v)
            obj.save()
        data = {
            "status"  : "success",
        }
        return data

    def resolve_field(self, fname):
        opts = self.model._meta
        pieces = fname.split(LOOKUP_SEP)
        for piece in pieces[:-1]:
            f = opts.get_field_by_name(piece)[0]
            opts = f.related_model._meta
        f = opts.get_field_by_name(pieces[-1])[0]
        return f

    def get_field_type(self, field):
        _TYPE_MAP = {
            djf.AutoField:                  "int",
            djf.BigIntegerField:            "int",
            djf.IntegerField:               "int",
            djf.PositiveIntegerField:       "int",
            djf.PositiveSmallIntegerField:  "int",
            djf.SmallIntegerField:          "int",
            djf.FloatField:                 "float",
            djf.DecimalField:               "float",
            djf.BinaryField:                None,
            djf.BooleanField:               "text", # TODO: enum with fixed choices, maybe checkbox?
            djf.NullBooleanField:           "text", # 
            djf.CharField:                  "text",
            djf.CommaSeparatedIntegerField: "text",
            djf.EmailField:                 "text",
            djf.FilePathField:              "text",
            djf.GenericIPAddressField:      "text",
            djf.IPAddressField:             "text",
            djf.SlugField:                  "text",
            djf.TextField:                  "text",
            djf.URLField:                   "text",
            djf.UUIDField:                  "text",
            djf.DateField:                  "date",
            djf.DateTimeField:              "datetime",
            djf.DurationField:              "text",
            djf.TimeField:                  "time",
        }
        return _TYPE_MAP.get(type(field),"text")

    def get_settings(self):
        return mark_safe(json.dumps(self.settings, indent=4))
