from django.contrib import admin

from .models import *

admin.site.register(Package)
admin.site.register(FileDescriptor)
admin.site.register(CompileCommand)

admin.site.register(Decl)
admin.site.register(NamespaceDecl)
admin.site.register(RecordDecl)
admin.site.register(MethodDecl)
admin.site.register(FunctionDecl)

admin.site.register(PresumedLoc)
admin.site.register(ClangImmutabilityCheckMethod)
