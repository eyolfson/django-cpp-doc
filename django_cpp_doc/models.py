from django.db import models
from django.contrib.postgres.fields import ArrayField

class PackageName(models.Model):
    name = models.CharField(max_length=256,
                            null=False,
                            blank=False)
    slug = models.SlugField(max_length=50,
                            null=False,
                            blank=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'cpp_doc_package_name'
        ordering = ['name']

class Package(models.Model):
    package_name = models.ForeignKey(PackageName,
                                     on_delete=models.CASCADE,
                                     null=False,
                                     blank=False,
                                     related_name='versions')
    version = models.CharField(max_length=50,
                               null=False,
                               blank=False)

    def __str__(self):
        return '{} {}'.format(str(self.package_name), self.version)

    class Meta:
        db_table = 'cpp_doc_package'
        ordering = ['package_name', 'version']

class FileDescriptor(models.Model):
    package = models.ForeignKey(Package,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='file_descriptors')
    parent = models.ForeignKey('FileDescriptor',
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True,
                               related_name='children')
    name = models.CharField(max_length=256,
                            null=False,
                            blank=True)
    path = models.CharField(max_length=4096,
                            null=False,
                            blank=True)

    def __str__(self):
        if self.parent is None:
            return 'Files'
        else:
            return self.path

    class Meta:
        db_table = 'cpp_doc_file_descriptor'
        verbose_name = 'File Descriptor'
        verbose_name_plural = 'File Descriptors'
        unique_together = ('package', 'parent', 'name')
        ordering = ['path']

class CompileCommand(models.Model):
    package = models.ForeignKey(Package,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='compile_commands')
    directory = models.ForeignKey(FileDescriptor,
                                  on_delete=models.CASCADE,
                                  null=False,
                                  blank=False,
                                  related_name='compile_command_directories')
    file = models.ForeignKey(FileDescriptor,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='compile_command_files')
    output = models.ForeignKey(FileDescriptor,
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True,
                               related_name='compile_command_outputs')
    command_line = ArrayField(
        models.CharField(max_length=256),
        size=256,
        null=False,
        blank=True,
    )

    def __str__(self):
        return '{}: {}'.format(str(self.package), ' '.join(self.command_line))

    class Meta:
        db_table = 'cpp_doc_compile_command'
        verbose_name = 'Compile Command'
        verbose_name_plural = 'Compile Commands'
        unique_together = ('package', 'file', 'output')

class Linkage(models.Model):
    package = models.ForeignKey(Package,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='linkages')
    file = models.ForeignKey(FileDescriptor,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='linkage_files')
    output = models.ForeignKey(FileDescriptor,
                               on_delete=models.CASCADE,
                               null=False,
                               blank=False,
                               related_name='linkage_outputs')

    def __str__(self):
        return '{}: {}'.format(str(self.package), str(self.output_file))

    class Meta:
        db_table = 'cpp_doc_linkage'
        verbose_name = 'Linkage'
        verbose_name_plural = 'Linkages'
        unique_together = ('package', 'file', 'output')

class PresumedLoc(models.Model):
    file = models.ForeignKey(FileDescriptor,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='presumed_locs')
    line = models.IntegerField()
    col = models.IntegerField()

    def __str__(self):
        return "{}:{}:{}".format(str(self.file), self.line, self.col)

    def get_github_url(self):
        import os.path

        package = self.file.package
        version = package.version
        slug = package.package_name.slug

        if slug == 'ninja':
            return "https://github.com/ninja-build/ninja/tree/v1.7.2/{}#L{}".format(version, self.file.path, self.line)
        elif slug == 'mosh':
            return "https://github.com/mobile-shell/mosh/tree/mosh-{}/{}#L{}".format(version, self.file.path, self.line)
        elif slug == 'fish':
            path = os.path.relpath(self.file.path, 'fish-shell-{}'.format(version))
            return "https://github.com/fish-shell/fish-shell/tree/{}/{}#L{}".format(version, path, self.line)
        elif slug == 'opencv':
            return "https://github.com/opencv/opencv/tree/{}/{}#L{}".format(version, self.file.path, self.line)
        elif slug == 'protobuf':
            return "https://github.com/google/protobuf/tree/v{}/{}#L{}".format(version, self.file.path, self.line)
        elif slug == 'bitcoin':
            return "https://github.com/bitcoin/bitcoin/tree/v{}/{}#L{}".format(version, self.file.path, self.line)
        elif slug == 'libsequence':
            path = os.path.relpath(self.file.path, '{}-{}'.format(slug, version))
            return 'https://github.com/molpopgen/libsequence/tree/{}/{}#L{}'.format(version, path, self.line)
        elif slug == 'llvm':
            if version == '4.0.0':
                version_tag = 'release_40'
            elif version == '5.0.0':
                version_tag = 'release_50'
            else:
                return None

            if self.file.path.startswith('tools/clang/tools/extra'):
              return "https://github.com/llvm-mirror/clang-tools-extra/tree/{}/{}#L{}".format(version_tag, self.file.path[24:], self.line)
            elif self.file.path.startswith('tools/clang'):
              return "https://github.com/llvm-mirror/clang/tree/{}/{}#L{}".format(version_tag, self.file.path[12:], self.line)
            elif self.file.path.startswith('tools/lldb'):
              return "https://github.com/llvm-mirror/lldb/tree/{}/{}#L{}".format(version_tag, self.file.path[11:], self.line)
            elif self.file.path.startswith('tools/lld'):
              return "https://github.com/llvm-mirror/lld/tree/{}/{}#L{}".format(version_tag, self.file.path[10:], self.line)
            elif self.file.path.startswith('projects/compiler-rt'):
              return "https://github.com/llvm-mirror/compiler-rt/tree/{}/{}#L{}".format(version_tag, self.file.path[21:], self.line)
            elif self.file.path.startswith('build'):
              return None
            else:
              return "https://github.com/llvm-mirror/llvm/tree/{}/{}#L{}".format(version_tag, self.file.path, self.line)
        else:
            return None

    class Meta:
        db_table = 'cpp_doc_presumed_loc'
        verbose_name = 'Presumed Loc'
        verbose_name_plural = 'Presumed Locs'
        unique_together = ('file', 'line', 'col')

class Decl(models.Model):
    package = models.ForeignKey(Package,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='decl_contexts')
    path = models.CharField(max_length=8192,
                            null=False,
                            blank=True)
    name = models.CharField(max_length=8192,
                            null=False,
                            blank=True)
    parent = models.ForeignKey('Decl',
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True,
                               related_name='children')
    presumed_loc = models.ForeignKey(PresumedLoc,
                                     on_delete=models.CASCADE,
                                     null=True,
                                     blank=True,
                                     related_name='decls')

    def namespaces(self):
        return self.children.filter(namespace__isnull=False)

    def methods(self):
        return self.children.filter(method__isnull=False)

    def fields(self):
        return self.children.filter(field__isnull=False)

    def records(self):
        return self.children.filter(record__isnull=False)

    def __str__(self):
        if self.parent is None:
            return 'Declarations'
        else:
            return self.path

    def get_name(self):
        if self.parent is None:
            return 'Declarations'
        elif self.name == '':
            return '(anonymous)'
        else:
            return self.name

    class Meta:
        db_table = 'cpp_doc_decl'
        ordering = ['path']
        verbose_name = 'Decl'
        verbose_name_plural = 'Decls'
        unique_together = ('package', 'path')

class NamespaceDecl(models.Model):
    decl = models.OneToOneField(Decl,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                primary_key=True,
                                related_name='namespace')

    def __str__(self):
        return str(self.decl)

    class Meta:
        db_table = 'cpp_doc_namespace_decl'
        verbose_name = 'Namespace Decl'
        verbose_name_plural = 'Namespace Decls'

class RecordDecl(models.Model):
    decl = models.OneToOneField(Decl,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                primary_key=True,
                                related_name='record')
    is_abstract = models.BooleanField()
    is_dependent = models.BooleanField()

    def __str__(self):
        return str(self.decl)

    def public_view_methods(self):
        return PublicView.objects.filter(record=self, decl__method__isnull=False)

    def public_view_fields(self):
        return PublicView.objects.filter(record=self, decl__field__isnull=False)

    class Meta:
        db_table = 'cpp_doc_record_decl'
        verbose_name = 'Record Decl'
        verbose_name_plural = 'Record Decls'

class MethodDecl(models.Model):
    decl = models.OneToOneField(Decl,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                primary_key=True,
                                related_name='method')
    is_const = models.BooleanField()
    is_pure = models.BooleanField()
    ACCESS_CHOICES = (
        (0, "Public"),
        (1, "Protected"),
        (2, "Private"),
        (3, "None"),
    )
    access = models.PositiveIntegerField(
        choices=ACCESS_CHOICES,
    )
    mangled_name = models.CharField(max_length=4096,
                                    null=False,
                                    blank=True)

    def __str__(self):
        return str(self.decl)

    class Meta:
        db_table = 'cpp_doc_method_decl'
        verbose_name = 'Method Decl'
        verbose_name_plural = 'Method Decls'


class FieldDecl(models.Model):
    decl = models.OneToOneField(Decl,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                primary_key=True,
                                related_name='field')
    is_mutable = models.BooleanField()
    ACCESS_CHOICES = (
        (0, "Public"),
        (1, "Protected"),
        (2, "Private"),
        (3, "None"),
    )
    access = models.PositiveIntegerField(
        choices=ACCESS_CHOICES,
    )

    def __str__(self):
        return str(self.decl)

    class Meta:
        db_table = 'cpp_doc_field_decl'
        verbose_name = 'Field Decl'
        verbose_name_plural = 'Field Decls'

class FunctionDecl(models.Model):
    decl = models.OneToOneField(Decl,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                primary_key=True,
                                related_name='function')

    def __str__(self):
        return str(self.decl)

    class Meta:
        db_table = 'cpp_doc_function_decl'
        verbose_name = 'Function Decl'
        verbose_name_plural = 'Function Decls'

class ClangImmutabilityCheckMethodBase(models.Model):
    MUTATE_RESULT_CHOICES = (
        (1, "No"),
        (2, "Maybe"),
    )
    RETURN_RESULT_CHOICES = (
        (1, "Noop"),
        (2, "Field (Transitive)"),
        (3, "Field (Non-transitive)"),
        (4, "Other"),
    )
    mutate_result = models.PositiveIntegerField(
        choices=MUTATE_RESULT_CHOICES,
    )
    return_result = models.PositiveIntegerField(
        choices=RETURN_RESULT_CHOICES,
    )

    class Meta:
        abstract = True

class ClangImmutabilityMethodDependence(models.Model):
    method = models.ForeignKey(MethodDecl,
                               on_delete=models.CASCADE,
                               null=False,
                               blank=False,
                               related_name='dependencies')
    callee = models.ForeignKey(MethodDecl,
                               on_delete=models.CASCADE,
                               null=False,
                               blank=False,
                               related_name='called_by')
    class Meta:
        db_table = 'cpp_doc_immutability_method_dependence'
        unique_together = ('method', 'callee')

class ClangImmutabilityCheckMethodResult(models.Model):
    method = models.OneToOneField(MethodDecl,
                                  on_delete=models.CASCADE,
                                  null=False,
                                  blank=False,
                                  primary_key=True,
                                  related_name='check_result')
    should_be_const = models.BooleanField()

    class Meta:
        db_table = 'cpp_doc_immutability_check_method_result'
        verbose_name = 'Check Method Result'
        verbose_name_plural = 'Check Method Results'

class ClangImmutabilityCheckMethod(ClangImmutabilityCheckMethodBase):
    method = models.OneToOneField(MethodDecl,
                                  on_delete=models.CASCADE,
                                  null=False,
                                  blank=False,
                                  primary_key=True,
                                  related_name='immutability_check')

    def __str__(self):
        return str(self.method)

    class Meta(ClangImmutabilityCheckMethodBase.Meta):
        db_table = 'cpp_doc_clang_immutability_check_method'
        verbose_name = 'Check Method'
        verbose_name_plural = 'Check Methods'

class ClangImmutabilityCheckField(models.Model):
    field = models.OneToOneField(FieldDecl,
                                 on_delete=models.CASCADE,
                                 null=False,
                                 blank=False,
                                 primary_key=True,
                                 related_name='immutability_check')
    is_transitive = models.BooleanField()
    is_explicit = models.BooleanField()

    def __str__(self):
        return str(self.field)

    class Meta:
        db_table = 'cpp_doc_clang_immutability_check_field'
        verbose_name = 'Check Fields'
        verbose_name_plural = 'Check Fields'

# class LLVMImmutabilityIssue(models.Model):
#     record = models.ForeignKey(RecordDecl,
#                                on_delete=models.CASCADE,
#                                related_name='llvm_immutability_issues')
#     method = models.ForeignKey(MethodDecl,
#                                on_delete=models.CASCADE,
#                                related_name='llvm_immutability_issues')
#     description = models.CharField(max_length=4096,
#                                    null=False,
#                                    blank=True)

#     class Meta:
#         db_table = 'cpp_doc_llvm_immutability_issue'
#         verbose_name = 'LLVM Immutability Issue'
#         verbose_name_plural = 'LLVM Immutability Issues'
#         unique_together = ('record', 'description')

class RecordCountsBase(models.Model):
    num_methods = models.PositiveIntegerField()

    num_mutable_methods = models.PositiveIntegerField()
    num_mutable_no_easy = models.PositiveIntegerField()
    num_mutable_no_easy_non_stub = models.PositiveIntegerField()
    num_mutable_no_odd = models.PositiveIntegerField()
    num_mutable_maybe = models.PositiveIntegerField()
    num_mutable_no_ret_noop = models.PositiveIntegerField()
    num_mutable_no_ret_field_t = models.PositiveIntegerField()
    num_mutable_no_ret_field_nt = models.PositiveIntegerField()
    num_mutable_no_ret_other = models.PositiveIntegerField()
    num_mutable_maybe_ret_noop = models.PositiveIntegerField()
    num_mutable_maybe_ret_field_t = models.PositiveIntegerField()
    num_mutable_maybe_ret_field_nt = models.PositiveIntegerField()
    num_mutable_maybe_ret_other = models.PositiveIntegerField()

    num_const_methods = models.PositiveIntegerField()
    num_const_no_easy = models.PositiveIntegerField()
    num_const_no_odd = models.PositiveIntegerField()
    num_const_maybe = models.PositiveIntegerField()
    num_const_no_ret_noop = models.PositiveIntegerField()
    num_const_no_ret_field_t = models.PositiveIntegerField()
    num_const_no_ret_field_nt = models.PositiveIntegerField()
    num_const_no_ret_other = models.PositiveIntegerField()
    num_const_maybe_ret_noop = models.PositiveIntegerField()
    num_const_maybe_ret_field_t = models.PositiveIntegerField()
    num_const_maybe_ret_field_nt = models.PositiveIntegerField()
    num_const_maybe_ret_other = models.PositiveIntegerField()

    num_fields = models.PositiveIntegerField()
    num_mutable_fields = models.PositiveIntegerField()
    num_explicit_fields = models.PositiveIntegerField()
    num_transitive_fields = models.PositiveIntegerField()
    num_only_explicit_fields = models.PositiveIntegerField()
    num_only_transitive_fields = models.PositiveIntegerField()
    num_neither_explicit_transitive_fields = models.PositiveIntegerField()
    num_both_explicit_transitive_fields = models.PositiveIntegerField()

    class Meta:
        abstract = True

class RecordCounts(RecordCountsBase):
    record = models.OneToOneField(RecordDecl,
                                  on_delete=models.CASCADE,
                                  null=False,
                                  blank=False,
                                  primary_key=True,
                                  related_name='counts')

    def __str__(self):
        return str(self.record)

    class Meta(RecordCountsBase.Meta):
        db_table = 'cpp_doc_record_counts'
        verbose_name = 'Record Counts'
        verbose_name_plural = 'Record Counts'

class PublicView(models.Model):
    record = models.ForeignKey(RecordDecl,
                               on_delete=models.CASCADE,
                               related_name='public_view')
    decl = models.ForeignKey(Decl,
                             on_delete=models.CASCADE,
                             related_name='public_view',
                             blank=True,
                             null=True)

    class Meta:
        db_table = 'cpp_doc_public_view'
        verbose_name = 'Public View'
        verbose_name_plural = 'Public Views'
        unique_together = ('record', 'decl')
