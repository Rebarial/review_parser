from django.contrib import admin
from .models import Organization, Branch, Review

class BranchInline(admin.TabularInline):
    model = Branch
    extra = 0 
    fields = ('address', 'yandex_map_link') 
    show_change_link = True 

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'inn')  
    search_fields = ['title']        
    ordering = ['id']
    inlines = [BranchInline] 

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch', 'author', 'rating', 'published_date')
    list_filter = ('branch', 'rating')     
    search_fields = ['author', 'content']  
    date_hierarchy = 'published_date'      
    ordering = ['-published_date']        