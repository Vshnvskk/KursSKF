import os

from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app

from app.forms import LoginForm, RegistrationForm, AddAdForm, SearchForm
from app.models import User, Ad, TypeObject, House, District, Street, Subway, City


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_login(form.login.data)
        if user is None or not user.check_password(form.password.data):
            flash('Неправильный логин или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Log In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        numb_phone = form.phone.data
        e_mail = form.email.data
        login_dev = form.login.data
        user = User(0,
                    numb_phone,
                    e_mail,
                    login_dev,
                    None)
        user.set_password(form.password.data)
        if not User.add(user):
            abort(500)
        flash('Вы зарегестрированы')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user')
def user():
    return "hi"

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_ad():
    form = AddAdForm()

    cities = City.get_all()
    if cities is None:
        cities = []
    cities.insert(0, (0, '-'))
    form.name_city.choices = cities

    streets = Street.get_all()
    if streets is None:
        streets = []
    streets.insert(0, (0, '-'))
    form.name_street.choices = streets

    subways = Subway.get_all()
    if subways is None:
        subways = []
    subways.insert(0, (0, '-'))
    form.name_subway.choices = subways

    districts = District.get_all()
    if districts is None:
        districts = []
    districts.insert(0, (0, '-'))
    form.name_district.choices = districts

    typeofdeal = TypeObject.get_all()
    if typeofdeal is None:
        typeofdeal = []
    typeofdeal.insert(0, (0, '-'))
    form.type_of_deal.choices = typeofdeal

    if form.validate_on_submit():
        name_object = form.name_object.data
        number = form.number.data
        building = form.building.data
        if building is None:
            building = ''
        amount_rooms = form.amount_rooms.data
        metr = form.metr.data
        price = form.price.data
        floor = form.floor.data
        type_of_deal = form.type_of_deal.data
        description = form.description.data

        path=''
        photo = form.photo.data
        if photo is not None and photo.filename != '':
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path = 'photos/' + filename

        house=House(0,
                    number, building, floorness=form.floorness.data, ID_District=form.name_district.data,
                    ID_Street=form.name_street.data, ID_Subway=form.name_subway.data)
        ID_House=House.add(house)
        if ID_House is None:
            abort(500)

        ad = Ad(0,
            name_object,amount_rooms,metr,
            price,floor,type_of_deal,
            description,path,ID_profile=current_user.id,
            ID_TypeObject=form.type_of_deal.data,ID_House=ID_House)
        print('Объект создан')
        if not Ad.add(ad):
            abort(500)
        flash('Объявление создано успешно')
        return redirect(url_for('index'))
    return render_template('add_ad.html', title='Объявление', form=form)

@app.route('/search', methods = ['GET', 'POST'])
def ad_searching():
    form = SearchForm()

    type_of_deal = TypeObject.get_all()
    if type_of_deal is None:
        type_of_deal = []
    type_of_deal.insert(0, (0, '-'))
    form.type_of_deal.choices = type_of_deal

    if form.validate_on_submit():
        type_of_deal = form.type_of_deal.data
        if type_of_deal == 0:
            type_of_deal = None
        ads = Ad.get_all_with_params(with_params=True, name_object=form.name_object.data,
                                     amount_rooms=form.amount_rooms.data, price=form.price.data,
                                     type_of_deal=type_of_deal)
        if ads is None:
            abort(500)

        return render_template('adsearch.html', title='search', form=form, ads=ads)
    ads = Ad.get_all_with_params()
    return render_template('adsearch.html', title='search', form=form, ads=ads)

@app.route('/ad_page/<adID>', methods = ['GET'])
def ad_page(adID):
    print(adID)
    ad = Ad.get_by_id(adID)
    house = House.get_by_id(ad.ID_House)
    street = Street.get_by_id(house.ID_Street)
    district = District.get_by_id(house.ID_District)
    subway = Subway.get_by_id(house.ID_Subway)
    city = City.get_by_id(street.ID_City)

    return render_template('ad_page.html', title='Объект', ad=ad, house=house,
                           street=street, district=district, subway=subway,
                           city=city)
