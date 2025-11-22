from django.db import models


class Item(models.Model):
    """Модель - продукт"""
    CURRENCY_CHOISES = [
        ('usd', 'USD'),
        ('eur', 'EUR')]
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOISES, default='USD')

    class Meta:
        """Метаданные"""
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        """Строковое представление"""
        return self.name


class Discount(models.Model):
    """Модель - скидка"""
    name = models.CharField(max_length=100)
    percent_off = models.DecimalField(max_digits=5, decimal_places=2)
    stripe_coupon_id = models.CharField(max_length=100, blank=True)

    class Meta:
        """Метаданные"""
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'

    def __str__(self):
        """Строковое представление"""
        return f'{self.name} ({self.percent_off}%)'


class Tax(models.Model):
    """Модель - налог"""
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    stripe_tax_id = models.CharField(max_length=100, blank=True)

    class Meta:
        """Метаданные"""
        verbose_name = 'Налог'
        verbose_name_plural = 'Налоги'

    def __str__(self):
        """Строковое представление"""
        return f'{self.name} ({self.percentage}%)'


class Order(models.Model):
    """Модель - заказ"""
    items = models.ManyToManyField(Item)
    discount = models.ForeignKey(
        Discount, on_delete=models.SET_NULL, null=True, blank=True
    )
    tax = models.ForeignKey(
        Tax, on_delete=models.SET_NULL, null=True, blank=True
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    def calculate_total(self):
        """Расчет итоговой суммы"""
        total = sum(item.price for item in self.items.all())
        if self.discount:
            total -= total * (self.discount.percent_off / 100)
        if self.tax:
            total += total * (self.tax.percentage / 100)
        self.total_amount = total
        self.save()
        return total

    class Meta:
        """Метаданные"""
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        """Строковое представление"""
        return f'Order - {self.id}'
