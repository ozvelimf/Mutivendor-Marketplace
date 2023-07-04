from flask import Blueprint, render_template, flash,redirect,session,logging,request
from .validation import LoginForm, RegisterForm
from .models import db
from functools import wraps

controllers = Blueprint('controllers', __name__,
                        template_folder='templates',
                        static_url_path='/static', 
                        static_folder='app/static')

# Kullanıcı kontrolü
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            return redirect("/login")
    return decorated_function

@controllers.route('/')
def index():
    database = db()
    session['categories'] = database.get_categories()
    product_data = database.latest_products()
    brands_data = database.get_brands()
    if "logged_in" in session:
        user_cart = database.get_cart_for_home(session["user_id"])
        return render_template("index.html", product_data = product_data, brands_data = brands_data, user_cart = user_cart)

    database.close()
    return render_template("index.html", product_data = product_data, brands_data = brands_data)

@controllers.route('/login', methods = ['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    register_form = RegisterForm(request.form)
    if request.method == "POST":
        database = db()
        if request.form.get("submit") == "Giriş Yap" and login_form.validate():
            result = database.login(login_form)
            if result[0] == True:
                flash("Başarıyla giriş yaptınız.", "success")
                session["logged_in"] = True
                session["username"] = login_form.username.data
                session["user_id"] = result[1]
                session["user_group"] = "Admin" if result[2] == 1 else "Member"
                database.close()
                return redirect("/")
            else:
                flash("Kullanıcı Adı veya Şifre Hatalı", "danger")
                return redirect("/login")
        
        elif request.form.get("submit") == "Kayıt Ol" and register_form.validate():
            database.register(register_form)
            flash("Başarıyla kayıt oldunuz. Şimdi giriş yapabilirsiniz.", "success")
            database.close()
            return redirect("/login")
        
        else:
            
            return render_template("login.html", login_form = login_form, register_form = register_form)
 
    return render_template("login.html", login_form = login_form, register_form = register_form)

@controllers.route('/logout')
def logout():
    session.clear()
    return redirect("/")

@controllers.route("/cart", methods = ['GET', 'POST'])
@login_required
def cart():
    if request.method == "POST":
        user_cart_value = request.form.get('user_cart_value')
        clear = request.form.get('clear')
        if user_cart_value == '0'   :
            flash("Sepetiniz boş olduğu için ödeme sayfasına gidemezsiniz.", "warning")
            return redirect("/cart")
        elif clear == '1':
            flash("test", "warning")
            return redirect("/cart")
        else:
            flash("Ödeme sayfası henüz oluşturulmadı", "warning")
            return redirect("/cart")
    else:
        database = db()
        user_cart = database.get_cart_for_home(session["user_id"])
        data = database.get_cart(session["user_id"])
        database.close()
        return render_template("cart.html", user_cart = user_cart, data = data)
    
@controllers.route("/products/", defaults={"page": 1})
@controllers.route("/products/<int:page>")
def products(page):
    database = db()
    user_cart = list()

    if "logged_in" in session:
        user_cart = database.get_cart_for_home(session["user_id"])
        product_data, total_pages = database.get_products(session["user_id"], page)
        database.close()
        return render_template("products.html", user_cart = user_cart, product_data = product_data, current_page=page, total_pages=total_pages)
    
    else:
        product_data, total_pages = database.get_products(0, page)
        database.close()
        return render_template("products.html", user_cart = user_cart, product_data = product_data, current_page=page, total_pages=total_pages)
 
@controllers.route("/product/<int:page>")
def product(page):
    database = db()
    user_cart = list()

    if "logged_in" in session:
        user_cart = database.get_cart_for_home(session["user_id"])
        product_data = database.get_product(session["user_id"], page)
        database.close()
        return render_template("product.html", user_cart= user_cart, product_data = product_data)
    
    else:   
        product_data = database.get_product(0, page)
        database.close()
        return render_template("product.html", user_cart= user_cart, product_data = product_data)

@controllers.route('/addcart/<int:id>', methods=['GET', 'POST'])
@login_required
def addcart(id, quantity = 1 ):
    if request.method == "POST":
        quantity = int(request.form.get('quantity'))
        database = db()
        database.addcart(session["user_id"], id , quantity)
        database.close()
        return redirect(request.headers.get('Referer'))

    else:
        database = db()
        database.addcart(session["user_id"], id , quantity)
        database.close()
        return redirect(request.headers.get('Referer'))

@controllers.route('/removeproduct/<int:id>')
@login_required
def removeproduct(id):
    database = db()
    database.removecart(id)
    database.close()
    return redirect(request.headers.get('Referer'))

@controllers.route("/favorites")
@login_required
def favorites():
    database = db()
    user_cart = database.get_cart_for_home(session["user_id"])
    favorites_data = database.get_favorites(session["user_id"])
    if len(favorites_data) == 0:
        flash("Favorilerinizde hiçbir ürün yoktur.", "warning")
        database.close()
        return render_template("/favorites.html", user_cart=user_cart)
    else:
        database.close()
        return render_template("/favorites.html", user_cart=user_cart, favorites_data = favorites_data)

@controllers.route('/removefavorites/<int:id>')
@login_required
def removefavorites(id):
    database = db()
    database.removefav(id)
    database.close()
    return redirect(request.headers.get('Referer'))

@controllers.route('/addfav/<int:id>')
@login_required
def addfav(id):
    database = db()
    database.addfav(session["user_id"], id)
    database.close()
    return redirect(request.headers.get('Referer'))


@controllers.route("/categories/", defaults={'page': None})
@controllers.route("/categories/<string:page>")
def categories(page):   
    if page is None:
        # "/categories" url'ine yapılan istek
        flash(f"Sayfa henüz oluşturulmadı", "warning")
        return redirect(request.headers.get('Referer'))
    else:
        # "/categories/<str:page>" url'ine yapılan istek
        flash(f"Sayfa henüz oluşturulmadı", "warning")
        return redirect("/")
    

@controllers.route("/panel")
def panel():
    flash("Kontrol paneli sayfası henüz oluşturulmadı", "warning")
    return redirect(request.headers.get('Referer'))


