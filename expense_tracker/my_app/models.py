from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('user', 'name')
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.amount} PLN"

class MonthlyBudget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    monthly_limit = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()

    class Meta:
        unique_together = ('user', 'month', 'year')

    def __str__(self):
        return f"Budżet dla {self.user.username} - {self.month}/{self.year}"