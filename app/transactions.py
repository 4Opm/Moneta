from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Transaction, Category
from datetime import datetime

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transactions')
@login_required
def index():
    transactions = Transaction.query.filter_by(
        user_id=current_user.id
    ).order_by(Transaction.date.desc()).all()

    categories = Category.query.all()

    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_income - total_expense

    return render_template(
        'transactions/index.html',
        transactions=transactions,
        categories=categories,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance
    )

@transactions_bp.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add():
    categories = Category.query.all()

    if request.method == 'POST':
        amount = request.form.get('amount')
        description = request.form.get('description')
        date_str = request.form.get('date')
        type_ = request.form.get('type')
        category_id = request.form.get('category_id')

        if not amount or not type_:
            flash('Amount and transaction type are required.', 'danger')
            return redirect(url_for('transactions.add'))
        try:
            amount = float(amount)
            date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
        except ValueError:
            flash('Invalid amount or date.', 'danger')
            return redirect(url_for('transactions.add'))
        
        transaction = Transaction(
            amount=amount,
            description=description,
            date=date,
            type=type_,
            user_id=current_user.id,
            category_id=int(category_id) if category_id else None
        )

        db.session.add(transaction)
        db.session.commit()

        flash('Transaction added!', 'success')
        return redirect(url_for('transactions.index'))

    return render_template('transactions/add.html', categories=categories)

@transactions_bp.route('/transactions/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    transaction = Transaction.query.get_or_404(id)

    if transaction.user_id != current_user.id:
        flash('Nie masz dostępu do tej transakcji.', 'danger')
        return redirect(url_for('transactions.index'))
    
    categories = Category.query.all()

    if request.method == 'POST':
        transaction.amount = float(request.form.get('amount'))
        transaction.description = request.form.get('description')
        transaction.type = request.form.get('type')
        category_id = request.form.get('category_id')
        transaction.category_id = int(category_id) if category_id else None

        date_str = request.form.get('date')
        if date_str:
            transaction.date = datetime.strptime(date_str, '%Y-%m-%d')

        db.session.commit()
        flash('Transaction updated!', 'success')
        return redirect(url_for('transactions.index'))

    return render_template('transactions/edit.html', transaction=transaction, categories=categories)

@transactions_bp.route('/transactions/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    transaction = Transaction.query.get_or_404(id)

    if transaction.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('transactions.index'))

    db.session.delete(transaction)
    db.session.commit()

    flash('Transaction deleted.', 'info')
    return redirect(url_for('transactions.index'))