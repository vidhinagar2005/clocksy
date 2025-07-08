from django.shortcuts import get_object_or_404, render, redirect
import razorpay
from .models import Category, Product, Brand, order
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.conf import settings
import pkg_resources
import razorpay

# Create your views here.

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')
        
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
        user.save()
        messages.success(request,'Account created successfully! Please log in.')
        return redirect(login_user)
    
    return render(request,'register.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(username)
        print(password)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  
            return redirect('index') 
        else:
            messages.error(request, "Invalid username or password!")
            return redirect('login_user')

    return render(request, "login.html")



def logout_user(request):
    logout(request)
    return redirect(index)

def account(request):
    return render(request, 'account.html', {'user': request.user})
    
def index(request):
    categories = Category.objects.all()
    products = Product.objects.all()[:8]
    brand = Brand.objects.all()
    return render(request, 'index.html', {'categories': categories, 'products': products, "brands": brand})

def category(request, name):
    categories = Category.objects.all()
    category = Category.objects.get(name=name)
    # print(category)
    products = category.product_set.all()
    # print(products)
    brand = Brand.objects.all()
    return render(request, 'category.html', {'categories': categories,'products': products, 'brands': brand,'name': name})

def singal_product(request, product_id):
    categories = Category.objects.all()
    product = Product.objects.get(id=product_id)
    # releted product
    related_product = Product.objects.filter(category=product.category)[:8]
    brand = Brand.objects.all()
    return render(request, 'singal_product.html', {'categories': categories, 'brands': brand, 'products': product, 'related_products': related_product})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            "name" : product.name,
            "price" : product.price,

            "quantity" : 1,
            "image" : product.image1.url if product.image1 else None, 
        }
    
    request.session['cart'] = cart
    request.session.modified = True
    print(cart)
    return redirect("cart_view")


def cart_view(request):
    categories = Category.objects.all()
    brand = Brand.objects.all()
    cart = request.session.get("cart", {})
    print(cart)
    # total_amount = sum(item['price'] * item['quantity'] for item in request.session.get('cart', {}).values())
    total_amount = sum(item['price'] * item['quantity'] for item in cart.values())
    
    return render(request, 'cart.html', {'categories': categories, 'total_amount': total_amount,'brands': brand, 'cart': cart})    

def update_cart(request, product_id, action):
    cart = request.session.get("cart", {})
    
    if str(product_id) in cart:
        if action == "increase":
            cart[str(product_id)]['quantity'] += 1
        elif action == "decrease":
            if cart[str(product_id)]['quantity'] > 1:
                cart[str(product_id)]['quantity'] -= 1
            else:
                del cart[str(product_id)]
                
    request.session['cart'] = cart
    request.session.modified = True
    return redirect("cart_view")


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        request.session.modified = True
        
    return redirect("cart_view")

def remove_from_wishlist(request, product_id):
    cart = request.session.get("wishcart", {})
    
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['wishcart'] = cart
        request.session.modified = True
        
    return redirect("wishlist_view")


def category_brand(request, name, brand):
    categories = Category.objects.all()
    # categories = Category.objects.all().order_by('price')

    category = Category.objects.get(name=name)
    brand1 = Brand.objects.get(name=brand)
    products = Product.objects.filter(category=category, brand=brand1)
    brand = Brand.objects.all()
    return render(request, 'category.html', {'categories': categories,'products': products, 'brands': brand, 'name': name})


def category_brand_only(request, brand):
    categories = Category.objects.all()
    brand1 = Brand.objects.get(name=brand)
    products = Product.objects.filter(brand=brand1)
    brand = Brand.objects.all()
    return render(request, 'brand_product.html', {'categories': categories,'products': products, 'brands': brand, 'name': brand})


# def register(request):
#     categories = Category.objects.all()
#     brand = Brand.objects.all()
#     return render(request, 'register.html', {'categories': categories, 'brands': brand})



def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishcart = request.session.get('wishcart', {})
    
    # if str(product_id) in cart:
    #     cart[str(product_id)]['quantity'] += 1
    # else:
    wishcart[str(product_id)] = {
        "name" : product.name,
        "price" : product.price,

        "quantity" : 1,
        "image" : product.image1.url if product.image1 else None, 
        }
    
    request.session['wishcart'] = wishcart
    request.session.modified = True
    print(wishcart)
    return redirect("wishlist_view")



def wishlist_view(request):
    categories = Category.objects.all()
    brand = Brand.objects.all()
    wishcart = request.session.get("wishcart", {})
    print(wishcart)
    # total_amount = sum(item['price'] * item['quantity'] for item in request.session.get('cart', {}).values())
    total_amount = sum(witem['price'] * witem['quantity'] for witem in wishcart.values())
    return render(request, 'wishlist.html', {'categories': categories, 'total_amount': total_amount,'brands': brand, 'cart': wishcart})    

@csrf_exempt
def paymentrazor(request):
    cart = request.session.get('cart', {})

    total_amount = sum(item['price'] * item['quantity'] for item in cart.values())
        
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    price = int(total_amount*100)
    
    data = {
        "amount": price,  # Amount in paise (₹500)
        "currency": "INR",
        "payment_capture": 1  # Auto capture
    }
    order = client.order.create(data)

    return render(request, "payment.html", {"order_id": order["id"], "razorpay_key": settings.RAZORPAY_KEY_ID})

@csrf_exempt
def payment_success(request):
    request.session['cart'] = {}  # Clear cart after successful payment

    return redirect("success")

def search_page(request):
    data = request.POST.get('search')
    result = Product.objects.filter(name__icontains = data)
    print(result)
    categories = Category.objects.all()
    brand = Brand.objects.all()

    return render(request,'search_page.html',{'categories':categories,'brands':brand,'results':result})


