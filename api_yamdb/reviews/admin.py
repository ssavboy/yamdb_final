from django.contrib import admin

from reviews.models import Category, Comment, Genre, Review, Title


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug"')
    search_fields = ('name',)


class GenreAdmin(CategoryAdmin):
    pass


class GenreInLine(admin.TabularInline):
    model = Genre


class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'year', 'description')
    search_fields = ('name', 'year')
    list_filter = ('category',)
    inlines = [GenreInLine]


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'review', 'text', 'author', 'pub_date',)
    search_fields = ('review', 'text', 'author', 'pub_date',)
    list_filter = ('review', 'text', 'author', 'pub_date',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'text', 'score', 'author', 'pub_date',)
    search_fields = ('title', 'text', 'author', 'pub_date',)
    list_filter = ('title', 'text', 'score', 'author', 'pub_date',)


admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(Review)
