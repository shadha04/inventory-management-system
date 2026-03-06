from django.shortcuts import render,redirect
from .models import Profile,Customer,Product, Category,Order
from django.http import HttpResponse
from django.contrib.auth import authenticate,login
import datetime
from django.utils import timezone

from django.contrib.auth import update_session_auth_hash

from django.contrib.auth import get_user_model


User = get_user_model()

def register(request):
    if request.method == 'POST':
        n = request.POST.get('username')
        e = request.POST.get('email')
        p = request.POST.get('password')
        c = request.POST.get('confirm_password')
        a = request.POST.get('address')
        ph = request.POST.get('phno')
        img = request.FILES.get('image')

        # Validate username/email
        if Profile.objects.filter(username=n).exists():
            return HttpResponse("Username already exists")
        if Profile.objects.filter(email=e).exists():
            return HttpResponse("Email already exists")
        # Create user
        x = Profile.objects.create_user(
            username=n,
            password=p,
            email=e,
            is_active=True,
            usertype='customer'
        )

        # Create customer WITHOUT image first
        customer = Customer(
            Customer_id=x,
            confirm_pass=c,
            address=a,
            ph_no=int(ph)  # make sure it’s integer
        )

        # Assign image
        if img:
            customer.image = img

        # Save object
        customer.save()

        return redirect('/log/')

    return render(request, 'app/reg.html')

def log(request):
    if request.method=='POST':
        n = request.POST.get('username', '').strip()
        p = request.POST.get('password', '').strip()
        x=authenticate(username=n,password=p)
        if x is not None and x.is_superuser==1:
            return redirect(admin)
        elif x is not None and x.is_active==1:
            login(request,x)
            request.session['customer']=x.id
            return redirect(customer)
        else:
            return HttpResponse('Invalid')
    return render(request,"app/log.html")


def admin(request):
    x=Product.objects.all()
    return render(request,'app/admin.html',{'data':x})

def customer(request):
    x=Product.objects.all()
    return render(request,'app/customer.html',{'data':x})

def home(request):
    return render(request,'app/home.html')


def add_product(request):
    # --- Merge duplicate categories first ---
    duplicates = Category.objects.values('name').annotate(cat_count=Count('id')).filter(cat_count__gt=1)
    for dup in duplicates:
        # Use case-insensitive matching and strip spaces
        cats = Category.objects.filter(name__iexact=dup['name'].strip())
        main_cat = cats.first()
        for extra_cat in cats[1:]:
            Product.objects.filter(Category=extra_cat).update(Category=main_cat)
            extra_cat.delete()

    # --- Get all categories after cleaning duplicates ---
    categories = Category.objects.all()

    if request.method == 'POST':
        pname = request.POST.get('name')
        quant = request.POST.get('quantity')
        price = request.POST.get('price')
        description = request.POST.get('description')
        expdate = request.POST.get('expdate')
        img = request.FILES.get('image')

        # Get new category if typed, else use selected existing category
        new_cat = request.POST.get('new_category', '').strip()
        existing_cat = request.POST.get('existing_category')

        if new_cat:
            category_name = new_cat
        elif existing_cat:
            category_name = existing_cat
        else:
            return HttpResponse('<script>alert("Please select or enter a category!");window.history.back();</script>')

        # Get or create category (prevents new duplicates)
        category_obj, created = Category.objects.get_or_create(name__iexact=category_name, defaults={'name': category_name})

        # Create the new product
        Product.objects.create(
            name=pname,
            Category=category_obj,
            quantity=quant,
            price=price,
            discription=description,
            exp_date=expdate,
            image=img
        )

        return HttpResponse('<script>alert("Product added successfully");window.location.href="/ad";</script>')

    return render(request, 'app/addproduct.html', {'categories': categories})

# ---------------- Edit Product ----------------
def edit_product(request, id):
    product_qs = Product.objects.filter(id=id)
    if not product_qs.exists():
        return HttpResponse('<script>alert("Product not found.");window.location.href="/ad";</script>')

    product = product_qs.first()
    categories = Category.objects.all()

    if request.method == 'POST':
        pname = request.POST['name']
        quant = request.POST['quantity']
        price = request.POST['price']
        description = request.POST['description']
        expdate = request.POST['expdate']

        # New or existing category
        new_cat = request.POST.get('new_category', '').strip()
        existing_cat = request.POST.get('existing_category')

        category_name = new_cat if new_cat else existing_cat
        category_obj, created = Category.objects.get_or_create(name=category_name)

        # Update product
        product.name = pname
        product.Category = category_obj
        product.quantity = quant
        product.price = price
        product.discription = description
        product.exp_date = expdate
        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        return HttpResponse('<script>alert("Product updated successfully");window.location.href="/ad";</script>')

    # For GET request
    return render(request, 'app/edit_product.html', {
        'data': product,
        'categories': categories,
        'new_category_value': '' if product.Category.name in [c.name for c in categories] else product.Category.name
    })


def product_details(request,id):
    x=Product.objects.get(id=id)
    return render(request,'app/product_details.html',{'data':x})

def del_product(request,id):
    x=Product.objects.get(id=id)
    x.delete()
    return HttpResponse('<script>alert("Product deleted successfully");window.location.href="/ad";</script>') 



def dashboard(request):
    total_category = Category.objects.count()
    total_product = Product.objects.count()
    low_stock = Product.objects.filter(quantity__lte=5).count()
    expired = Product.objects.filter(exp_date__lt=datetime.date.today()).count()

    context = {
        'total_category': total_category,
        'total_product': total_product,
        'low_stock': low_stock,
        'expired': expired,
    }
    return render(request, 'app/dashboard.html', context)


def low_stock_products(request):
    products = Product.objects.filter(quantity__lte=5)  # Low stock threshold
    return render(request, 'app/low_stock.html', {'products': products})

def expired_products(request):
    today = timezone.now().date()
    products = Product.objects.filter(exp_date__lt=today)
    return render(request, 'app/expired_products.html', {'products': products})

def view_categories(request):
    categories = Category.objects.all()
    return render(request, 'app/view_category.html', {'categories': categories})

from django.db.models import Count

import datetime

def report(request):
    total_category = Category.objects.count()
    total_product = Product.objects.count()
    low_stock = Product.objects.filter(quantity__lte=5).count()
    expired = Product.objects.filter(exp_date__lt=datetime.date.today()).count()

    # Merge duplicate category names and sum product counts
    category_summary_dict = {}
    for cat in Category.objects.all():
        cat_name = cat.name
        # Add the number of products in this category
        category_summary_dict[cat_name] = category_summary_dict.get(cat_name, 0) + Product.objects.filter(category=cat).count()

    # Convert dict to list of dicts for template
    category_summary = [{'name': name, 'count': count} for name, count in sorted(category_summary_dict.items())]

    context = {
        'total_products': total_product,
        'total_categories': total_category,
        'low_stock_products': low_stock,
        'expired_products': expired,
        'category_summary': category_summary
    }

    return render(request, 'app/report.html', context)



def view_customer(request):
    x=Profile.objects.filter(usertype='customer')
    return render(request,'app/view_customer.html',{'data':x})



def order(request, id):
    product = Product.objects.get(id=id)
    customer = Customer.objects.get(Customer_id=request.user)

    # Check stock
    if product.quantity <= 0:
        return HttpResponse("<script>alert('Out of stock');window.location.href='/cs/';</script>")

    # Check expired
    if product.exp_date < datetime.date.today():
        return HttpResponse("<script>alert('Product expired');window.location.href='/cs/';</script>")

    # Create order
    Order.objects.create(
        customer=customer,
        product=product,
        quantity=1
    )

    # Reduce stock
    product.quantity -= 1
    product.save()

    return HttpResponse("<script>alert('Order placed successfully');window.location.href='/cs/';</script>")

# def my_orders(request):
#     customer = Customer.objects.get(Customer_id=request.user)
#     orders = Order.objects.filter(customer=customer).order_by('-order_date')

#     for order in orders:
#         order.total_price = order.quantity * order.product.price

#     return render(request, 'app/my_order.html', {'orders': orders})


def view_order(request):
    orders = Order.objects.select_related('customer__Customer_id', 'product').all().order_by('-order_date')

    # Handle POST request to update status
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        if order_id and new_status:
            try:
                o = Order.objects.get(id=order_id)
                o.status = new_status
                o.save()
            except Order.DoesNotExist:
                pass
        return redirect('view_order')

    return render(request, 'app/view_order.html', {'data': orders})




def change_psss(request):
    if request.method == 'POST':
        pas = request.POST['pass']
        con = request.POST['conpass']

        if pas != con:
            return HttpResponse('<script>alert("Passwords do not match");window.history.back();</script>')

        user = request.user   # This is Profile object
        user.set_password(pas)
        user.save()

        update_session_auth_hash(request, user)

        return HttpResponse("<script>alert('Password changed successfully');window.location.href='/cs/';</script>")

    return render(request, 'app/changepass.html')

def view_profile(request):
    customer = Customer.objects.get(Customer_id=request.user)
    return render(request, 'app/view_profile.html', {'data': customer})

from django.contrib.auth import update_session_auth_hash

def edit_profile(request, id):
    customer = Customer.objects.get(id=id)

    if request.method == "POST":

        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        password = request.POST.get('pass')
        confirm = request.POST.get('con')

        # Update basic details
        customer.Customer_id.username = name
        customer.Customer_id.email = email
        customer.ph_no = phone
        customer.address = address

        # Update image if uploaded
        if request.FILES.get('image'):
            customer.image = request.FILES.get('image')

        # Update password if entered
        if password:
            if password == confirm:
                user = customer.Customer_id
                user.set_password(password)
                user.save()
                update_session_auth_hash(request, user)
            else:
                return HttpResponse("<script>alert('Passwords do not match');window.history.back();</script>")

        customer.Customer_id.save()
        customer.save()

        return HttpResponse("<script>alert('Profile Updated Successfully');window.location.href='/view_profile/';</script>")

    return render(request, 'app/edit_profile.html', {'data': customer})





# Create your views here.

# def register(request):
#     if request.method == 'POST':
#         n = request.POST.get('username', '').strip()
#         e = request.POST.get('email', '').strip()
#         p = request.POST.get('password', '').strip()
#         c = request.POST.get('confirm_password', '').strip()
#         a = request.POST.get('address', '').strip()
#         ph = request.POST.get('phno', '').strip()
        

#         #  Password match
#         if p != c:
#             return HttpResponse('<script>alert("Passwords do not match");window.history.back();</script>')

#         # Check if username exists
#         if Profile.objects.filter(username=n).exists():
#             return HttpResponse('<script>alert("Username already exists");window.history.back();</script>')

#         # Create Profile
#         x = Profile.objects.create_user(username=n, password=p, email=e, is_active=True, usertype='customer')

#         # Create Customer 
#         y = Customer.objects.create(Customer_id=x, confirm_pass=c, address=a, ph_no=ph)
#         y.save()

#         return HttpResponse('<script>alert("Successfully registered");window.location.href="/log";</script>')

#     return render(request, 'app/reg.html')

def log(request):
    if request.method=='POST':
        n = request.POST.get('username', '').strip()
        p = request.POST.get('password', '').strip()
        x=authenticate(username=n,password=p)
        if x is not None and x.is_superuser==1:
            return redirect(admin)
        elif x is not None and x.is_active==1:
            login(request,x)
            request.session['customer']=x.id
            return redirect(customer)
        else:
            return HttpResponse('Invalid')
    return render(request,"app/log.html")


def admin(request):
    x=Product.objects.all()
    return render(request,'app/admin.html',{'data':x})

def customer(request):

    products = Product.objects.all()
    msg = request.GET.get('cart')   # 👈 ADD THIS

    return render(request,'app/customer.html',{
        'data': products,
        'msg': msg   # 👈 ADD THIS
    })
def home(request):
    return render(request,'app/home.html')


def add_product(request):
    categories = Category.objects.all()  # For dropdown

    if request.method == 'POST':
        pname = request.POST['name']
        quant = request.POST['quantity']
        price = request.POST['price']
        description = request.POST['description']
        expdate = request.POST['expdate']
        img = request.FILES['image']

        # Get new category if typed, else use selected existing category
        new_cat = request.POST.get('new_category', '').strip()
        existing_cat = request.POST.get('existing_category')

        # Decide which category to use
        category_name = new_cat if new_cat else existing_cat

        if not category_name:  # Ensure category is provided
            return HttpResponse('<script>alert("Please select or enter a category!");window.history.back();</script>')

        # ⚠ Important: use get_or_create with case-insensitive name check
        category_obj, created = Category.objects.get_or_create(name__iexact=category_name, defaults={'name': category_name})

        # Create product
        Product.objects.create(
            name=pname,
            Category=category_obj,
            quantity=quant,
            price=price,
            discription=description,
            exp_date=expdate,
            image=img
        )

        return HttpResponse('<script>alert("Product added successfully");window.location.href="/ad";</script>')

    return render(request, 'app/addproduct.html', {'categories': categories})

   


# ---------------- Edit Product ----------------
def edit_product(request, id):
    product_qs = Product.objects.filter(id=id)
    if not product_qs.exists():
        return HttpResponse('<script>alert("Product not found.");window.location.href="/ad";</script>')

    product = product_qs.first()
    categories = Category.objects.all()

    if request.method == 'POST':
        pname = request.POST['name']
        quant = request.POST['quantity']
        price = request.POST['price']
        description = request.POST['description']
        expdate = request.POST['expdate']

        # New or existing category
        new_cat = request.POST.get('new_category', '').strip()
        existing_cat = request.POST.get('existing_category')

        category_name = new_cat if new_cat else existing_cat
        category_obj, created = Category.objects.get_or_create(name=category_name)

        # Update product
        product.name = pname
        product.Category = category_obj
        product.quantity = quant
        product.price = price
        product.discription = description
        product.exp_date = expdate
        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        return HttpResponse('<script>alert("Product updated successfully");window.location.href="/ad";</script>')

    # For GET request
    return render(request, 'app/edit_product.html', {
        'data': product,
        'categories': categories,
        'new_category_value': '' if product.Category.name in [c.name for c in categories] else product.Category.name
    })


def product_details(request,id):
    x=Product.objects.get(id=id)
    return render(request,'app/product_details.html',{'data':x})

def del_product(request,id):
    x=Product.objects.get(id=id)
    x.delete()
    return HttpResponse('<script>window.location.href="/ad";</script>') 



def dashboard(request):
    total_category = Category.objects.count()
    total_product = Product.objects.count()
    low_stock = Product.objects.filter(quantity__lte=5).count()
    expired = Product.objects.filter(exp_date__lt=datetime.date.today()).count()

    context = {
        'total_category': total_category,
        'total_product': total_product,
        'low_stock': low_stock,
        'expired': expired,
    }
    return render(request, 'app/dashboard.html', context)


def low_stock_products(request):
    products = Product.objects.filter(quantity__lte=5)  # Low stock threshold
    return render(request, 'app/low_stock.html', {'products': products})

def expired_products(request):
    today = timezone.now().date()
    products = Product.objects.filter(exp_date__lt=today)
    return render(request, 'app/expired_products.html', {'products': products})

def view_categories(request):
    categories = Category.objects.all()
    return render(request, 'app/view_category.html', {'categories': categories})

def report(request):
    total_category = Category.objects.count()
    total_product = Product.objects.count()
    low_stock = Product.objects.filter(quantity__lte=5).count()
    expired = Product.objects.filter(exp_date__lt=datetime.date.today()).count()

    # Use ORM annotate to sum products per category
    from django.db.models import Count

    category_summary = (
        Category.objects
        .annotate(count=Count('product'))
        .values('name', 'count')
        .order_by('name')
    )

    context = {
        'total_products': total_product,
        'total_categories': total_category,
        'low_stock_products': low_stock,
        'expired_products': expired,
        'category_summary': category_summary
    }

    return render(request, 'app/report.html', context)



def view_customer(request):
    customers = Customer.objects.select_related('Customer_id').all()
    return render(request, 'app/view_customer.html', {'data': customers})



def order(request, id):
    product = Product.objects.get(id=id)
    customer = Customer.objects.get(Customer_id=request.user)

    # Stock check
    if product.quantity <= 0:
        return HttpResponse("<script>alert('Out of stock');window.location.href='/cs/';</script>")

    # Expiry check
    if product.exp_date < datetime.date.today():
        return HttpResponse("<script>alert('Product expired');window.location.href='/cs/';</script>")

    # Create order with default Cash on delivery
    Order.objects.create(
        customer=customer,
        product=product,
        quantity=1,
        payment_method='COD',      # ✅ Use 'COD' exactly
        payment_status='Unpaid',   
        status='Pending'
    )

    # Reduce stock
    product.quantity -= 1
    product.save()

    return HttpResponse("<script>alert('Order placed successfully');window.location.href='/cs/';</script>")

def my_orders(request):
    customer = Customer.objects.get(Customer_id=request.user)
    orders = Order.objects.filter(
        customer=customer
    ).exclude(status__in=['Pending', 'Cart']).order_by('-order_date')  # latest first
    return render(request, 'app/my_order.html', {'orders': orders})



def change_psss(request):
    if request.method == 'POST':
        pas = request.POST['pass']
        con = request.POST['conpass']

        if pas != con:
            return HttpResponse('<script>alert("Passwords do not match");window.history.back();</script>')

        user = request.user   # This is Profile object
        user.set_password(pas)
        user.save()

        update_session_auth_hash(request, user)

        return HttpResponse("<script>alert('Password changed successfully');window.location.href='/cs/';</script>")

    return render(request, 'app/changepass.html')

def view_profile(request):

    if not request.user.is_authenticated:
        return redirect('cs')   # or your login page

    try:
        customer = Customer.objects.get(Customer_id=request.user)
    except Customer.DoesNotExist:
        return redirect('cs')   # if no customer record

    return render(request, 'app/view_profile.html', {'data': customer})

def edit_profile(request, id):
    customer = Customer.objects.get(id=id)

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        pas = request.POST.get('pass')
        con = request.POST.get('con')

        # Update basic fields safely
        if name:
            customer.Customer_id.username = name

        if email:
            customer.Customer_id.email = email

        if address:
            customer.address = address
        if phone:
            customer.ph_no = phone

        image = request.FILES.get('image')
        if image:
            customer.image = image

        # Password change (optional)
        if pas and con:
            if pas != con:
                return HttpResponse('<script>alert("Passwords do not match");window.history.back();</script>')

            user = customer.Customer_id
            user.set_password(pas)
            user.save()
            update_session_auth_hash(request, user)

        customer.Customer_id.save()
        customer.save()

        return HttpResponse("<script>alert('Profile Updated Successfully');window.location.href='/view_profile/';</script>")

    return render(request, 'app/edit_profile.html', {'data': customer})


def category_products(request, id):
    category = Category.objects.get(id=id)
    products = Product.objects.filter(Category=category)

    return render(request, 'app/category_products.html', {
        'category': category,
        'products': products
    })

def add_to_cart(request, id):

    if not request.user.is_authenticated:
        return redirect('/')

    try:
        product = Product.objects.get(id=id)
        customer = Customer.objects.get(Customer_id=request.user)
    except:
        return redirect('/cs/')

    # check if already in cart
    existing = Order.objects.filter(
        customer=customer,
        product=product,
        status="Pending"
    ).first()

    if not existing:
        Order.objects.create(
            customer=customer,
            product=product,
            quantity=1,
            status="Pending"
        )

    return redirect('/cs/?cart=added')

def view_cart(request):
    customer = Customer.objects.get(Customer_id=request.user)

    cart_items = Order.objects.filter(
        customer=customer,
        status='Pending'
    )

    return render(request, 'app/cart.html', {'cart_items': cart_items})

def place_order(request, id):
    customer = Customer.objects.get(Customer_id=request.user)

    order = Order.objects.get(
        id=id,
        customer=customer,
        status='Pending'
    )

    order.status = 'Ordered'
    order.payment_method = 'Offline'
    order.payment_status = 'Unpaid'
    order.save()

    return redirect('view_cart')


def update_quantity(request, id, action):
    order = Order.objects.get(id=id)

    if action == "increase":
        order.quantity += 1

    elif action == "decrease":
        if order.quantity > 1:
            order.quantity -= 1

    order.save()
    return redirect('view_cart')

def order_page(request, id):

    customer = Customer.objects.get(Customer_id=request.user)

    order = Order.objects.get(
        id=id,
        customer=customer,
        status='Pending'
    )

    return render(request, 'app/order_page.html', {'order': order})

def confirm_order(request, id):
    customer = Customer.objects.get(Customer_id=request.user)

    try:
        order = Order.objects.get(id=id, customer=customer, status='Pending')
    except Order.DoesNotExist:
        return HttpResponse('<script>alert("Order not found");window.location.href="/cs/";</script>')

    if request.method == "POST":
        payment_method = request.POST.get('payment_method')
        new_address = request.POST.get('address')
                

        # Save address to the order


        if payment_method:
            order.payment_method = payment_method
        order.address = new_address
        order.status = "Ordered"
        order.payment_status = "Unpaid"
        order.order_date = timezone.now()  # save timestamp
        order.save()  # ⚠ must save after editing address

        return redirect('my_orders')

    # If GET, redirect to cart
    return redirect('view_cart')