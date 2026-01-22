import json
import csv
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Expense, Category, MonthlyBudget
from .forms import ExpenseForm, CategoryForm, BudgetForm
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Rejestracja pomyślna! Witaj, {user.username}!")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'my_app/register.html', {'form': form})

@login_required
def dashboard(request):
    today = timezone.now()
    
    polish_months_locative = {
        1: 'styczniu', 2: 'lutym', 3: 'marcu', 4: 'kwietniu', 5: 'maju', 6: 'czerwcu',
        7: 'lipcu', 8: 'sierpniu', 9: 'wrześniu', 10: 'październiku', 11: 'listopadzie', 12: 'grudniu'
    }

    budget, created = MonthlyBudget.objects.get_or_create(
        user=request.user, 
        year=today.year, 
        month=today.month,
        defaults={'monthly_limit': 0}
    )
    monthly_budget = budget.monthly_limit
    
    current_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_end = current_month_start - relativedelta(microseconds=1)
    last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_expenses_this_month = Expense.objects.filter(user=request.user, date__gte=current_month_start).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses_last_month = Expense.objects.filter(user=request.user, date__gte=last_month_start, date__lt=current_month_start).aggregate(Sum('amount'))['amount__sum'] or 0
    
    remaining_budget = monthly_budget - total_expenses_this_month
    recent_expenses = Expense.objects.filter(user=request.user).order_by('-date')[:5]
    
    context = {
        'monthly_budget': monthly_budget,
        'total_expenses_this_month': total_expenses_this_month,
        'total_expenses_last_month': total_expenses_last_month,
        'last_month_name': polish_months_locative.get(last_month_start.month),
        'current_month_name': polish_months_locative.get(today.month),
        'remaining_budget': remaining_budget,
        'recent_expenses': recent_expenses,
    }
    return render(request, 'my_app/dashboard.html', context)

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, "Wydatek został pomyślnie dodany!")
            return redirect('dashboard')
    else:
        form = ExpenseForm(user=request.user)
    return render(request, 'my_app/add_expense.html', {'form': form, 'title': 'Dodaj wydatek'})

@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Wydatek został zaktualizowany.")
            return redirect('dashboard')
    else:
        form = ExpenseForm(instance=expense, user=request.user)
    return render(request, 'my_app/add_expense.html', {'form': form, 'title': 'Edytuj wydatek'})

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, "Wydatek został usunięty.")
        return redirect('dashboard')
    return render(request, 'my_app/confirm_delete.html', {'object': expense, 'type': 'Wydatek'})

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user).order_by('name')
    return render(request, 'my_app/categories.html', {'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                category = form.save(commit=False)
                category.user = request.user
                category.save()
                messages.success(request, "Nowa kategoria została dodana.")
                return redirect('category_list')
            except:
                messages.error(request, "Taka kategoria już istnieje.")
    else:
        form = CategoryForm()
    return render(request, 'my_app/add_category.html', {'form': form})

@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    related_expenses_count = Expense.objects.filter(category=category).count()
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                Expense.objects.filter(category=category).delete()
                category_name = category.name
                category.delete()
                
            messages.success(request, f"Kategoria '{category_name}' i jej {related_expenses_count} wydatków zostało usuniętych.")
            return redirect('category_list')
            
        except Exception as e:
            messages.error(request, f"Wystąpił błąd podczas usuwania: {e}")
            return redirect('category_list')
    
    return render(request, 'my_app/confirm_delete.html', {
        'object': category, 
        'type': 'Kategorię',
        'related_count': related_expenses_count
    })

@login_required
def set_budget(request):
    today = timezone.now()
    budget, created = MonthlyBudget.objects.get_or_create(
        user=request.user,
        year=today.year,
        month=today.month,
        defaults={'monthly_limit': 0}
    )
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, "Budżet został zaktualizowany.")
            return redirect('dashboard')
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'my_app/set_budget.html', {'form': form})

@login_required
def reports(request):
    expenses = Expense.objects.filter(user=request.user).select_related('category')
    categories = Category.objects.filter(user=request.user)

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    category_id = request.GET.get('category')

    if start_date_str:
        expenses = expenses.filter(date__gte=start_date_str)
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            expenses = expenses.filter(date__lte=end_date)
        except (ValueError, TypeError):
            pass 
    if category_id:
        expenses = expenses.filter(category_id=category_id)

    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    category_summary = expenses.values('category__name').annotate(total=Sum('amount')).order_by('-total')

    context = {
        'expenses': expenses,
        'categories': categories,
        'total_expenses': total_expenses,
        'category_summary_json': json.dumps(list(category_summary), cls=DecimalEncoder),
        'start_date': start_date_str,
        'end_date': end_date_str,
        'selected_category': int(category_id) if category_id else None,
    }
    return render(request, 'my_app/reports.html', context)

@login_required
def ajax_add_category(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_name = data.get('name')

            if not category_name:
                return JsonResponse({'error': 'Nazwa kategorii jest wymagana.'}, status=400)

            if Category.objects.filter(user=request.user, name__iexact=category_name).exists():
                return JsonResponse({'error': 'Taka kategoria już istnieje.'}, status=400)

            new_category = Category.objects.create(user=request.user, name=category_name)
            
            return JsonResponse({'id': new_category.id, 'name': new_category.name})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Nieprawidłowe żądanie.'}, status=400)

@login_required
def export_expenses_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="wydatki.csv"'
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Tytuł', 'Kwota', 'Kategoria', 'Data', 'Opis'])

    expenses = Expense.objects.filter(user=request.user).select_related('category')

    for expense in expenses:
        category_name = expense.category.name if expense.category else 'Bez kategorii'
        writer.writerow([
            expense.title,
            expense.amount,
            category_name,
            expense.date.strftime('%Y-%m-%d %H:%M'),
            expense.description
        ])

    return response