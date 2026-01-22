from django import forms
from .models import Expense, Category, MonthlyBudget

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date', 'description']
        labels = {
            'title': 'Tytuł wydatku',
            'amount': 'Kwota',
            'category': 'Kategoria',
            'date': 'Data',
            'description': 'Opis (opcjonalnie)',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. Zakupy spożywcze'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'np. 150.50'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control flatpickr-datetime', 'type': 'text', 'placeholder': 'Wybierz datę i godzinę'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ExpenseForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Kwota wydatku musi być większa od zera.")
        return amount

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {
            'name': 'Nazwa nowej kategorii',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. Jedzenie, Transport...'}),
        }

class BudgetForm(forms.ModelForm):
    class Meta:
        model = MonthlyBudget
        fields = ['monthly_limit']
        labels = {
            'monthly_limit': 'Miesięczny limit budżetu (PLN)',
        }
        widgets = {
            'monthly_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'np. 3000.00'}),
        }