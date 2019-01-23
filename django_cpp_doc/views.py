from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views import generic

from django.db.models import Q
from .models import Decl, FileDescriptor, Package, PackageName

def index(request):
    return render(request, 'cpp_doc/index.html')

class PackageNameIndexView(generic.ListView):
    model = PackageName
    template_name = 'cpp_doc/package_name_list.html'
    context_object_name = 'package_name_list'

class PackageIndexView(generic.ListView):
    model = Package
    template_name = 'cpp_doc/package_list.html'
    context_object_name = 'package_list'

    def get_queryset(self):
        self.package_name = get_object_or_404(PackageName,
                                              slug=self.kwargs['slug'])
        return Package.objects.filter(package_name=self.package_name)

    def get_context_data(self, **kwargs):
        context = super(PackageIndexView, self).get_context_data(**kwargs)
        context['package_name'] = self.package_name
        return context

class PackageDetailView(generic.DetailView):
    model = Package
    template_name = 'cpp_doc/package_detail.html'

    def get_object(self):
        self.package_name = get_object_or_404(PackageName,
                                              slug=self.kwargs['slug'])
        self.package = get_object_or_404(Package,
                                         package_name=self.package_name,
                                         version=self.kwargs['version'])
        return self.package

    def get_context_data(self, **kwargs):
        context = super(PackageDetailView, self).get_context_data(**kwargs)
        context['package_name'] = self.package_name
        return context

def file_get_context(package, fd=None):
    context = {'package_name': package.package_name, 'package': package}
    try:
        root_fd = FileDescriptor.objects.get(package=package, parent=None)
        context['root_fd'] = root_fd
    except (FileDescriptor.DoesNotExist,
            FileDescriptor.MultipleObjectsReturned):
        raise Http404("No root directory.")

    if fd is None:
        fd = root_fd
    context['fd'] = fd

    directory_list = []
    directory = fd.parent
    if directory:
        while directory.parent is not None:
            directory_list.append(directory)
            directory = directory.parent
    directory_list.reverse()
    context['directory_list'] = directory_list

    return context

def file_root(request, slug, version):
    package_name = get_object_or_404(PackageName, slug=slug)
    package = get_object_or_404(Package, package_name=package_name,
                                version=version)
    context = file_get_context(package)
    return render(request, 'cpp_doc/file_detail.html', context)

def file_detail(request, slug, version, fd_pk):
    package_name = get_object_or_404(PackageName, slug=slug)
    package = get_object_or_404(Package, package_name=package_name,
                                version=version)
    file = get_object_or_404(FileDescriptor, pk=fd_pk, package=package)
    context = file_get_context(package, file)
    return render(request, 'cpp_doc/file_detail.html', context)

def decl_get_context(package, decl=None):
    context = {'package_name': package.package_name, 'package': package}
    try:
        root_decl = Decl.objects.get(package=package, parent=None)
        context['root_decl'] = root_decl
    except (Decl.DoesNotExist,
            Decl.MultipleObjectsReturned):
        raise Http404("No root declaration.")

    if decl is None:
        decl = root_decl
    context['decl'] = decl

    decl_context_list = []
    decl_context = decl.parent
    if decl_context:
        while decl_context.parent is not None:
            decl_context_list.append(decl_context)
            decl_context = decl_context.parent
    decl_context_list.reverse()
    context['decl_context_list'] = decl_context_list
    return context

def decl_root(request, slug, version):
    package_name = get_object_or_404(PackageName, slug=slug)
    package = get_object_or_404(Package, package_name=package_name,
                                version=version)
    context = decl_get_context(package)
    return render(request, 'cpp_doc/decl_detail.html', context)

def decl_detail(request, slug, version, decl_pk):
    package_name = get_object_or_404(PackageName, slug=slug)
    package = get_object_or_404(Package, package_name=package_name,
                                version=version)
    decl = get_object_or_404(Decl, pk=decl_pk, package=package)
    context = decl_get_context(package, decl)
    return render(request, 'cpp_doc/decl_detail.html', context)
