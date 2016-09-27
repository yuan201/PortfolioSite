from django.contrib import admin

from .models import Benchmark, BenchmarkConstitute, BenchmarkPerformance

admin.site.register(Benchmark)
admin.site.register(BenchmarkConstitute)
admin.site.register(BenchmarkPerformance)
