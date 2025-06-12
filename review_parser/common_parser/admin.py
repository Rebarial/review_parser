from django.contrib import admin
from .models import Organization, Branch, Review

class BranchInline(admin.StackedInline):
    model = Branch
    extra = 0 
    show_change_link = True 

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'inn')  
    search_fields = ['name']        
    ordering = ['id']
    inlines = [BranchInline] 
    actions = ['parse_2gis']



@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch', 'author', 'rating', 'published_date')
    list_filter = ('branch', 'rating')     
    search_fields = ['author', 'content']  
    date_hierarchy = 'published_date'      
    ordering = ['-published_date']        