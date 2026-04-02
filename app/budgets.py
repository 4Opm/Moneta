from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Budget, Category, Transaction
from sqlalchemy import extract
from datetime import date

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route('/budgets')
@login_required
def index():
    today = date.today()
    current_month = today.month
    current_year = today.year

    categories = Category.query.all()
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    budgets = Budget.query.filter_by(
        user_id=current_user.id
    ).order_by(Budget.year.desc(), Budget.month.desc()).all()
    budgets_with_spending = []
    for budget in budgets:
        transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'expense',
            Transaction.category_id == budget.category_id,
            extract('month', Transaction.date) == budget.month,
            extract('year', Transaction.date) == budget.year
        ).all()

        spent = sum(t.amount for t in transactions)
        percentage = (spent / budget.limit_amount * 100) if budget.limit_amount > 0 else 0
        percentage = min(percentage, 100)

        budgets_with_spending.append({
            'budget': budget,
            'spent': spent,
            'remaining': budget.limit_amount - spent,
            'percentage': round(percentage, 1)
        })

    return render_template('budgets/index.html',
        budgets_with_spending=budgets_with_spending,
        categories=categories,
        current_month=current_month,
        current_year=current_year,
        month_names=month_names
    )

@budgets_bp.route('/budgets/add', methods=['GET', 'POST'])
@login_required
def add():
    categories = Category.query.all()
    today = date.today()

    if request.method == 'POST':
        category_id = request.form.get('category_id')
        limit_amount = request.form.get('limit_amount')
        month = request.form.get('month')
        year = request.form.get('year')

        if not limit_amount or not month or not year:
            flash('All fields are required.', 'danger')
            return redirect(url_for('budgets.add'))

        cat_id = int(category_id) if category_id and category_id.strip() else None

        existing = Budget.query.filter_by(
            user_id=current_user.id,
            category_id=cat_id,
            month=int(month),
            year=int(year)
        ).first()

        if existing:
            flash('A budget for this category and month already exists.', 'warning')
            return redirect(url_for('budgets.add'))

        budget = Budget(
            limit_amount=float(limit_amount),
            month=int(month),
            year=int(year),
            user_id=current_user.id,
            category_id=cat_id
        )

        db.session.add(budget)
        db.session.commit()

        flash('Budget added!', 'success')
        return redirect(url_for('budgets.index'))

    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    return render_template('budgets/add.html',
        categories=categories,
        current_month=today.month,
        current_year=today.year,
        month_names=month_names
    )

@budgets_bp.route('/budgets/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    budget = Budget.query.get_or_404(id)

    if budget.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('budgets.index'))

    db.session.delete(budget)
    db.session.commit()

    flash('Budget deleted.', 'info')
    return redirect(url_for('budgets.index'))