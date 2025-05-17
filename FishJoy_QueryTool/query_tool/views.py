from django.apps import apps
from django.db.models import Count, F, Q, Avg
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from .forms import AddSpotsForm, AddFishForm, AddBaitsForm
from .models import Spots, Fish, Baits, FishCategory, SpotCategory
from .utils import DataMixin


class Home(DataMixin, ListView):
    model = Spots
    template_name = 'query_tool/home.html'
    context_object_name = 'spots'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Home')

        headers = self.model._meta.get_fields()
        context['headers'] = headers
        return {**context, **c_def}

    def get_queryset(self):
        return Spots.objects.order_by('pk').select_related('spot_category')


class FishList(DataMixin, ListView):
    model = Fish
    template_name = 'query_tool/fish.html'
    context_object_name = 'fish'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Fish')

        headers = self.model._meta.get_fields()
        context['headers'] = headers
        return {**context, **c_def}

    def get_queryset(self):
        return Fish.objects.order_by('pk').select_related('fish_category')


class BaitsList(DataMixin, ListView):
    model = Baits
    template_name = 'query_tool/baits.html'
    context_object_name = 'baits'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Baits')

        headers = self.model._meta.get_fields()
        context['headers'] = headers
        return {**context, **c_def}

    def get_queryset(self):
        return Baits.objects.order_by('pk')


def query_tool(request):
    mixin = DataMixin()
    context = mixin.get_user_context(title='Query tool')

    if request.method == 'POST':
        table_name = request.POST.get('table_name')
        model_class = apps.get_model(app_label='query_tool', model_name=table_name)

        if table_name == 'spots':
            context['spots_header'] = Spots._meta.get_fields()

            value_gt = request.POST.get('value_gt')
            value_lt = request.POST.get('value_lt')
            spots_category_slug = request.POST.get('spots_category_slug')
            spots_category_slug_value = request.POST.get('spots_category_slug_value')
            spots_fish = request.POST.get('spots_fish')
            context['q_spots_depth_gt'] = Spots.objects.filter(max_depth__gt=value_gt) if value_gt else None
            context['q_spots_depth_lt'] = Spots.objects.filter(max_depth__lt=value_lt) if value_lt else None
            context['q_spots_cat_gt'] = Spots.objects.filter(spot_category__slug=spots_category_slug.lower()).\
                filter(max_depth__gt=spots_category_slug_value).select_related('spot_category') if spots_category_slug_value else None
            try:
                fish_m = Fish.objects.get(slug=spots_fish.lower()) if spots_fish else None
                context['q_spots_fish'] = Spots.objects.filter(fish=fish_m.id) if fish_m else None
            except Fish.DoesNotExist:
                pass

        elif table_name == 'fish':
            context['fish_header'] = Fish._meta.get_fields()

            fish_spots = request.POST.get('fish_spots')
            fish_same_cat = request.POST.get('fish_same_cat')
            fish_on_all_spots = request.POST.get('fish_on_all_spots')
            fish_bait_name = request.POST.get('fish_bait_name')
            fish_fish_category = request.POST.get('fish_fish_category')
            fish_spots_category = request.POST.get('fish_spots_category')
            fish_value_depth_gt = request.POST.get('fish_value_depth_gt')
            fish_fish_cat = request.POST.get('fish_fish_cat')
            try:
                spot_m = Spots.objects.get(slug=fish_spots.lower()) if fish_spots else None
                context['q_fish_spots'] = Fish.objects.filter(spots=spot_m.id) if spot_m else None

                cat = Fish.objects.filter(slug=fish_same_cat.lower()).values('fish_category') if fish_same_cat else None
                context['q_fish_same_cat'] = Fish.objects.filter(fish_category__in=cat).exclude(slug=fish_same_cat.lower()) if fish_same_cat else None
                context['q_fish_on_all_spots'] = Fish.objects.annotate(num_locations=Count('spots__location'))\
                    .filter(num_locations=Spots.objects.count()) if fish_on_all_spots else None

                context['q_fish_name_cat_cat_value_gt'] = Fish.objects.filter(baits__slug=fish_bait_name.lower()) \
                    .filter(fish_category__slug=fish_fish_category.lower()) \
                    .filter(spots__spot_category__slug=fish_spots_category.lower()) \
                    .filter(spots__max_depth__gt=fish_value_depth_gt)\
                    .distinct() if fish_bait_name and fish_fish_category and fish_spots_category and fish_value_depth_gt else None

                predator_fish_categories = FishCategory.objects.filter(name=fish_fish_cat) if fish_fish_cat else None
                context['fish_fish_cat11'] = Spots.objects.filter(
                    fish__fish_category__in=predator_fish_categories).annotate(
                    num_predator_fish=Count('fish', filter=Q(fish__fish_category__in=predator_fish_categories))).filter(
                    num_predator_fish=len(predator_fish_categories)) if fish_fish_cat else None

            except Spots.DoesNotExist:
                pass

        elif table_name == 'baits':
            context['baits_header'] = Baits._meta.get_fields()

            baits_fish_name = request.POST.get('baits_fish_name')
            baits_price = request.POST.get('baits_price')
            q_baits_on_all_spots = request.POST.get('baits_on_all_spots')
            try:
                fish_m = Fish.objects.get(slug=baits_fish_name.lower()) if baits_fish_name else None
                context['q_baits_fish_price'] = Baits.objects.filter(fish=fish_m.id).filter(price__lt=baits_price) if fish_m else None
                context['q_baits_on_all_spots'] = Baits.objects.annotate(num_fish=Count('fish__name', distinct=True))\
                    .filter(num_fish=Fish.objects.count()) if q_baits_on_all_spots else None

            except:
                pass

    return render(request, 'query_tool/query_tool.html', context)


def delete(request):
    id = request.GET.get('id')
    table_name = request.GET.get('table')

    try:
        model_class = apps.get_model(app_label='query_tool', model_name=table_name)
        model_class.objects.get(id=int(id)).delete()
    except LookupError:
        return HttpResponseBadRequest("<h1>Invalid table name</h1>")

    return redirect('query_tool')


def edit(request):
    mixin = DataMixin()
    context = mixin.get_user_context(title='Update')

    id = request.GET.get('id')
    table_name = request.GET.get('table')

    try:
        model_class = apps.get_model(app_label='query_tool', model_name=table_name)
        row = model_class.objects.get(id=int(id))

        if table_name != 'baits':
            cat_class = \
                apps.get_model(app_label='query_tool',
                               model_name=table_name + 'Category' if table_name == 'fish' else table_name[:-1] + 'Category')

            context['categories'] = cat_class.objects.all()
            context['fish_or_baits'] = \
                Fish.objects.all() if table_name == 'spots' else Baits.objects.all() if table_name == 'fish' else None

        context['row'] = row

    except LookupError:
        return HttpResponseBadRequest("<h1>Invalid table name</h1>")

    return render(request, f'query_tool/update_{table_name}.html', context=context)


def edit_record(request, id):
    if request.method == 'POST':
        table_name = request.POST.get('table_name')

        title = request.POST.get('title')
        slug = request.POST.get('slug')
        location = request.POST.get('location')
        max_depth = request.POST.get('max_depth')
        fish = request.POST.getlist('fish')
        spot_category = request.POST.get('spot_category')
        name = request.POST.get('name')
        average_weight = request.POST.get('average_weight')
        baits = request.POST.getlist('baits')
        fish_category = request.POST.get('fish_category')
        price = request.POST.get('price')

        try:
            model_class = apps.get_model(app_label='query_tool', model_name=table_name)
            row = model_class.objects.get(id=int(id))

            if table_name == 'spots':
                row.title = title
                row.slug = slug
                row.location = location
                row.max_depth = max_depth
                row.fish.clear()
                for f in fish:
                    res = Fish.objects.get(name=f)
                    row.fish.add(res)
                cat = SpotCategory.objects.get(name=spot_category)
                row.spot_category = cat

            elif table_name == 'fish':
                row.name = name
                row.slug = slug
                row.average_weight = average_weight
                row.baits.clear()
                for b in baits:
                    res = Baits.objects.get(name=b)
                    row.baits.add(res)
                cat = FishCategory.objects.get(name=fish_category)
                row.fish_category = cat

            elif table_name == 'baits':
                row.name = name
                row.slug = slug
                row.price = price

            row.save()
        except LookupError:
            return HttpResponseBadRequest("<h1>Invalid table name</h1>")

    return redirect('home')


def add(request):
    if request.method == 'POST':
        table_name = request.POST.get('table')

        try:
            model_class = apps.get_model(app_label='query_tool', model_name=table_name)
        except LookupError:
            return HttpResponseBadRequest("<h1>Invalid table name</h1>")

    return redirect(f'add_{table_name}'.lower())


class AddSpots(DataMixin, CreateView):
    form_class = AddSpotsForm
    template_name = 'query_tool/add_form.html'
    success_url = reverse_lazy('query_tool')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Add spot')
        return {**context, **c_def}


class AddFish(DataMixin, CreateView):
    form_class = AddFishForm
    template_name = 'query_tool/add_form.html'
    success_url = reverse_lazy('query_tool')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Add fish')
        return {**context, **c_def}


class AddBaits(DataMixin, CreateView):
    form_class = AddBaitsForm
    template_name = 'query_tool/add_form.html'
    success_url = reverse_lazy('query_tool')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Add bait')
        return {**context, **c_def}
