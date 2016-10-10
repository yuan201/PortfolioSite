from decimal import Decimal

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import DetailView, ListView, FormView, RedirectView

from .models import Benchmark, BenchmarkConstitute, BenchmarkPerformance
from .forms import ConstituteCreateForm
from core.mixins import TitleHeaderMixin


class BenchmarkCreateView(TitleHeaderMixin, CreateView):
    model = Benchmark
    fields = ['name', 'description']
    template_name = 'benchmark/benchmark_create.html'

    # todo remove jumbotron in template and probably the title and header stuff
    def __init__(self, *args, **kwargs):
        super(BenchmarkCreateView, self).__init__(*args, **kwargs)
        self.title = "Benchmark"
        self.header = "Create Benchmark"


class BenchmarkDetailView(DetailView):
    model = Benchmark
    template_name = 'benchmark/benchmark_detail.html'

    def get_context_data(self, **kwargs):
        context = super(BenchmarkDetailView, self).get_context_data(**kwargs)
        context['constitutes'] = BenchmarkConstitute.objects.filter(benchmark=self.object)
        context['performances'] = BenchmarkPerformance.objects.filter(benchmark=self.object)
        return context


class BenchmarkListView(ListView):
    model = Benchmark
    template_name = 'benchmark/benchmark_list.html'


class ConstituteCreateView(TitleHeaderMixin, FormView):
    model = BenchmarkConstitute
    form_class = ConstituteCreateForm
    template_name = 'benchmark/constitute_create_update.html'

    # todo remove jumbotron and probably title and header stuff here
    def __init__(self, *args, **kwargs):
        super(ConstituteCreateView, self).__init__(*args, **kwargs)
        self.title = 'Constitute'
        self.header = 'Create Constitute'

    def get_context_data(self, **kwargs):
        context = super(ConstituteCreateView, self).get_context_data(**kwargs)
        benchmark = get_object_or_404(Benchmark, pk=self.kwargs['pk'])
        context['benchmark'] = benchmark
        return context

    def form_valid(self, form):
        form.save_constitute()
        return super(ConstituteCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ConstituteCreateView, self).get_form_kwargs()
        kwargs['benchmark'] = get_object_or_404(Benchmark, pk=self.kwargs['pk'])
        return kwargs

    def get_success_url(self):
        benchmark = get_object_or_404(Benchmark, pk=self.kwargs['pk'])
        return reverse('benchmarks:detail', args=[benchmark.id])


class ConstituteDeleteView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        constitute = get_object_or_404(BenchmarkConstitute, pk=kwargs['pk'])
        redirect = reverse('benchmarks:detail', args=[constitute.benchmark.id])
        constitute.delete()
        return redirect


class ConstituteUpdateView(TitleHeaderMixin, UpdateView):
    model = BenchmarkConstitute
    fields = ['security', 'percent']
    template_name = 'benchmark/constitute_create_update.html'

    # todo remove jumbotron in template and probably get rid of header stuff
    def __init__(self, *args, **kwargs):
        super(ConstituteUpdateView, self).__init__(*args, **kwargs)
        self.header = "Update Constitute"


class ConstituteNormalizeView(RedirectView):
    """
    Normalize the percent of all constitutes so they add up to 1
    update performance database after normalize
    """
    def get_redirect_url(self, *args, **kwargs):
        benchmark = get_object_or_404(Benchmark, pk=self.kwargs['pk'])
        benchmark.normalize_and_update()
        return reverse('benchmarks:detail', args=[benchmark.id])
