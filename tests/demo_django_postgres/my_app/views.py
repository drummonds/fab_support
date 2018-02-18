try:
    from django.urls import reverse, reverse_lazy
except ImportError:
    from django.core.urlresolvers import reverse, reverse_lazy

from django.views.generic import ListView

from .models import MyData


class HomeView(ListView):
    template_name = 'name_list.html'
    # redirect_field_name = ''
    model = MyData

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update({'objects': MyData.objects.all(), 'version': 'Hi'})
        return context
