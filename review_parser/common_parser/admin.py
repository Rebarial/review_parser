from django.contrib import admin
from .models import Organization, Branch, Review, BranchIPMapping
from nested_admin import NestedStackedInline, NestedModelAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from twogis_parser.tools.parser import create_2gis_reviews
from yandex_parser.tools.parser import create_yandex_reviews
from vl_parser.tools.parser import create_vlru_reviews
from common_parser.tools.parse import parse_all_providers

class BranchInline(NestedStackedInline):
    model = Branch
    extra = 0 
    show_change_link = True 

@admin.register(Branch)
class BranchAdmin(NestedModelAdmin):
    list_display = ('id', 'organization', 'address')
    list_filter = ('organization',)

    def parsing(self, request, object_id=None):  
        
        branch = Branch.objects.get(id=object_id)

        parse_all_providers(branch)

        return HttpResponseRedirect(reverse_lazy('admin:common_parser_branch_changelist'))
    
    def parsing_yandex(self, request, object_id=None):  
        
        branch = Branch.objects.get(id=object_id)

        create_yandex_reviews(url=branch.yandex_map_url, inn=branch.organization.inn, address=branch.address)

        return HttpResponseRedirect(reverse_lazy('admin:common_parser_branch_changelist'))
    
    def parsing_2gis(self, request, object_id=None):  
        
        branch = Branch.objects.get(id=object_id)

        create_2gis_reviews(url=branch.twogis_map_url, inn=branch.organization.inn, address=branch.address)

        return HttpResponseRedirect(reverse_lazy('admin:common_parser_branch_changelist'))
    
    def parsing_vlru(self, request, object_id=None):  
        
        branch = Branch.objects.get(id=object_id)

        create_vlru_reviews(branch.vlru_url, branch.organization.inn, address=branch.address)

        return HttpResponseRedirect(reverse_lazy('admin:common_parser_branch_changelist'))

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path('<path:object_id>/change/parse/', self.admin_site.admin_view(self.parsing)),
            path('<path:object_id>/change/parse-yandex/', self.admin_site.admin_view(self.parsing_yandex)),
            path('<path:object_id>/change/parse-2gis/', self.admin_site.admin_view(self.parsing_2gis)),
            path('<path:object_id>/change/parse-vlru/', self.admin_site.admin_view(self.parsing_vlru)),
        ]
        return my_urls + urls


    change_form_template = 'admin/branch_custom.html'

@admin.register(Organization)
class OrganizationAdmin(NestedModelAdmin):
    list_display = ('id', 'name', 'inn')  
    search_fields = ['name']        
    ordering = ['id']
    inlines = [BranchInline] 



@admin.register(Review)
class ReviewAdmin(NestedModelAdmin):
    list_display = ('id', 'branch', 'author', 'rating', 'published_date')
    list_filter = ('branch', 'rating')     
    search_fields = ['author', 'content']  
    date_hierarchy = 'published_date'      
    ordering = ['-published_date']        


admin.site.register(BranchIPMapping)