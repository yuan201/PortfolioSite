from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import DetailView, ListView, FormView, RedirectView

from .models import Benchmark, BenchmarkConstitute
from .forms import ConstituteCreateForm
from core.mixins import TitleHeaderMixin


class BenchmarkCreateView(TitleHeaderMixin, CreateView):
    model = Benchmark
    fields = ['name', 'description']
    template_name = 'benchmark/benchmark_create.html'

    def __init__(self):
        super(BenchmarkCreateView, self).__init__()
        self.title = "Benchmark"
        self.header = "Create Benchmark"


class BenchmarkDetailView(DetailView):
    model = Benchmark
    template_name = 'benchmark/benchmark_detail.html'

    def get_context_data(self, **kwargs):
        context = super(BenchmarkDetailView, self).get_context_data(**kwargs)
        context['constitutes'] = BenchmarkConstitute.objects.filter(benchmark=self.object)
        return context


class BenchmarkListView(ListView):
    model = Benchmark
    template_name = 'benchmark/benchmark_list.html'


class ConstituteCreateView(TitleHeaderMixin, FormView):
    model = BenchmarkConstitute
    form_class = ConstituteCreateForm
    template_name = 'benchmark/constitute_create_update.html'

    def __init__(self):
        super(ConstituteCreateView, self).__init__()
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
        benchmark = constitute.benchmark
        constitute.delete()
        return reverse('benchmarks:detail', args=[benchmark.id])


class ConstituteUpdateView(TitleHeaderMixin, UpdateView):
    model = BenchmarkConstitute
    fields = ['security', 'percent']
    template_name = 'benchmark/constitute_create_update.html'

    def __init__(self):
        super(ConstituteUpdateView, self).__init__()
        self.header = "Update Constitute"


class ConstituteNormalizeView(RedirectView):
    """Normalize the percent of all constitutes so they add up to 1"""
    def get_redirect_url(self, *args, **kwargs):
        benchmark = get_object_or_404(Benchmark, pk=self.kwargs['pk'])
        total_percent = .0
        for cst in benchmark.constitutes.all():
            total_percent += cst.percent

        for cst in benchmark.constitutes.all():
            cst.percent = cst.percent/total_percent
            cst.save()

        return reverse('benchmarks:detail', args=[benchmark.id])
