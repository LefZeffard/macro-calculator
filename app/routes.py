from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request, abort, session
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, ServingForm, WeightForm, QuickAddForm, ActionForm, EditInfo
from app.models import User, Meal


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    action = ActionForm()
    user = current_user
    if action.validate_on_submit(): 
        if action.remove.data:
            meal_id = request.form.get("meal_id", type=int)
            meal_delete = db.session.get(Meal, meal_id)
            if meal_delete and meal_delete.user_id == current_user.id:
                db.session.delete(meal_delete)
                db.session.commit()
        elif action.new_day.data:
            
            db.session.execute(
                sa.delete(Meal).where(Meal.user_id == current_user.id)
                )
            db.session.commit()
            session["ingredients"] = []
        return redirect(url_for('index'))
    meals = user.meals
    total_calories = sum(i.calories for i in meals)
    total_protein = sum(i.protein for i in meals)
    total_fat = sum(i.fat for i in meals)
    tz_name = session.get('timezone', 'UTC')
    return render_template('index.html', title='summary', user=user, meals=meals, tz_name=tz_name,
                           total_calories=total_calories, total_protein=total_protein, total_fat=total_fat, action=action)

@app.route('/set_timezone', methods=['POST'])
def set_timezone():
    data = request.get_json() or {}
    tz_name = data.get('timezone')
    try:
        ZoneInfo(tz_name)
        session['timezone'] = tz_name
    except (ZoneInfoNotFoundError, TypeError):
        session['timezone'] = 'UTC'
    return '', 204

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        r_cals = round(form.target_calories.data, 1)
        r_pro = round(form.target_protein.data, 1)
        r_fat = round(form.target_fat.data, 1)
        user = User(username=form.username.data, target_calories=r_cals, 
                    target_protein=r_pro, target_fat=r_fat)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("User has been registered.")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/log_meal/<mode>', methods=['GET', 'POST'])
@login_required
def log_meal(mode):
    action = ActionForm()
    ingredients = session.get('ingredients', [])
    if mode == 'base':
        return render_template('log_meal.html', mode=mode)
    elif mode == 'servings':
        form = ServingForm()
    elif mode == 'weight':
        form = WeightForm()
    elif mode == 'quick':
        form = QuickAddForm()
    else:
        abort(404)
    if form.add.data and form.validate():
        if mode == 'servings':
            servings = form.servings.data
        elif mode == 'weight':
            servings = form.weight.data / form.weight_servings.data
        elif mode == 'quick':
            servings = 1
        calories, protein, fat = form.calories.data*servings, form.protein.data*servings, form.fat.data*servings
        ingredient = {'calories': round(calories, 1), 'protein': round(protein, 1), 'fat': round(fat, 1)}
        ingredients.append(ingredient)
        session['ingredients'] = ingredients
        return redirect(url_for('log_meal', mode=mode))
    elif action.validate() and action.submit.data:
        meal = Meal(user_id=current_user.id, 
                    calories=session['total_cal'], protein=session['total_pro'], fat=session['total_fat'])
        db.session.add(meal)
        db.session.commit()
        flash("Meal has been logged.")
        session['ingredients'] = []
        session['total_cal'], session['total_pro'], session['total_fat'] = 0, 0, 0
        return redirect(url_for('log_meal', mode='base'))
    elif action.validate() and action.remove.data:
        index = int(request.form.get("index"))    
        if 0 <= index < len(ingredients):
            ingredients.pop(index)
        session["ingredients"] = ingredients
        return redirect(url_for('log_meal', mode=mode))
    if ingredients:
        total_cal = sum([i['calories'] for i in ingredients])
        total_pro = sum([i['protein'] for i in ingredients])
        total_fat = sum([i['fat'] for i in ingredients])
        session['total_cal'], session['total_pro'], session['total_fat'] = total_cal, total_pro, total_fat
        return render_template('log_meal.html', mode=mode, form=form, ingredients=ingredients, action=action,
                            total_cal=total_cal, total_pro=total_pro, total_fat=total_fat)
    return render_template('log_meal.html', mode=mode, form=form, ingredients=ingredients, action=action)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = EditInfo()
    if form.validate_on_submit():
        current_user.target_calories = round(form.target_calories.data, 1)
        current_user.target_protein = round(form.target_protein.data, 1)
        current_user.target_fat = round(form.target_fat.data, 1)
        db.session.commit()
        flash("Targets have been updated.")
        return redirect(url_for('settings'))
    elif request.method == 'GET':
        form.target_calories.data = current_user.target_calories
        form.target_protein.data = current_user.target_protein
        form.target_fat.data = current_user.target_fat
    return render_template('settings.html', form=form)
    


