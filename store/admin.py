from django.contrib import admin

from store.models import Discount, Order, Tax, Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Класс для отображения модели в админке"""
    list_display = ('id', 'name')


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    """Класс для отображения модели в админке"""
    list_display = ('id', 'name')


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    """Класс для отображения модели в админке"""
    list_display = ('id', 'name')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Класс для отображения модели в админке"""
    list_display = ('id',)