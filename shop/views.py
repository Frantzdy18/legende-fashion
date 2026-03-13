from decimal import Decimal
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db import transaction 
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Product, Profile, Purchase
from .forms import ProductForm
from .forms import SignupWithEmailForm
from django.db.models import Sum, Q


from .forms import ProfileForm

@login_required
def profile_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès !")
            return redirect('profile')
        else:
            messages.error(request, "Erreur lors de la mise à jour du profil.")
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'shop/profile.html', {'form': form, 'profile': profile})



def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)



@login_required
@admin_required
def admin_user_profile(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    # Ou ka ajoute commandes si ou gen modèl Order
    orders = getattr(user_obj, 'order_set', None)
    return render(request, 'shop/admin_user_profile.html', {
        'user_obj': user_obj,
        'orders': orders.all() if orders else [],
    })





@login_required
@admin_required
def admin_users(request):
    users = User.objects.all().order_by('id')
    return render(request, 'shop/admin_users.html', {'users': users})


@login_required
def profile(request):
    profile = request.user.profile

    # AJOUTE pati sa
    if request.method == "POST":
        if request.FILES.get('profile_pic'):
            profile.profile_pic = request.FILES['profile_pic']
            profile.save()

    return render(request, "shop/profile.html")


def is_staff(user):
    return user.is_staff

@login_required
def product_search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(nom__icontains=query)
    ) if query else Product.objects.none()  # si pa gen rechèch, montre anyen

    return render(request, 'shop/product_search_results.html', {
        'products': products,
        'query': query
    })



@login_required
@user_passes_test(is_staff)
def update_purchase_status(request, purchase_id, status):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    if status in ['expedie', 'livre']:
        purchase.statut = status
        purchase.save()
    return redirect('orders')


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity', 1))
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity

    request.session['cart'] = cart
    messages.success(request, "Produit ajouté au panier !")
    return redirect('product_list')


def cart_view(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        subtotal = product.prix * quantity
        total += subtotal

        products.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, "shop/cart.html", {
        'products': products,
        'total': total
    })


@login_required
def checkout(request):
    cart = request.session.get("cart", {})

    if not cart:
        return redirect("cart")

    user_profile = request.user.profile
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        messages.error(request, "Aucun administrateur trouvé.")
        return redirect("cart")
    admin_profile = admin_user.profile

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)

        if product.quantite < quantity:
            messages.error(request, f"Stock insuffisant pour {product.nom}")
            return redirect("cart")

        total_price = product.prix * quantity

        if user_profile.balance < total_price:
            messages.error(request, "Solde insuffisant.")
            return redirect("cart")

        user_profile.balance -= total_price
        admin_profile.balance += total_price

        user_profile.save()
        admin_profile.save()

        product.quantite -= quantity
        product.save()

        Purchase.objects.create(
            user=request.user,
            product=product,
            prix=total_price
        )

    request.session["cart"] = {}
    messages.success(request, "Commande passée avec succès !")
    return redirect("orders")


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart
    return redirect('cart')


def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Vous n'avez pas la permission d'accéder à cette page !")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
def orders(request):
    if request.user.is_staff:
        orders = Purchase.objects.all().order_by('-date')
        total_sales = Purchase.objects.aggregate(Sum('prix'))['prix__sum'] or 0
    else:
        orders = Purchase.objects.filter(user=request.user).order_by('-date')
        total_sales = None

    return render(request, 'shop/orders.html', {
        'orders': orders,
        'total_sales': total_sales
    })


@login_required
def demo_withdraw(request):
    profile = request.user.profile
    if request.method == 'POST':
        montant_str = request.POST.get('montant', '0')
        try:
            montant = Decimal(montant_str)
            if montant <= 0:
                messages.error(request, "Montant doit être supérieur à 0 !")
            elif montant > profile.balance:
                messages.error(request, "Solde insuffisant !")
            else:
                profile.balance -= montant
                profile.save()
                messages.success(request, f"{montant} $ retiré avec succès !")
        except:
            messages.error(request, "Montant invalide !")
        return redirect('demo_withdraw')

    # 👇 Mwen ajoute balance san retire profile
    return render(request, 'shop/demo_withdraw.html', {
        'profile': profile,
        'balance': profile.balance
    })


@login_required
def demo_topup(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    message = ""

    if request.method == "POST":
        montant_str = request.POST.get("montant", "0")
        try:
            montant = Decimal(montant_str)
            if montant <= 0:
                message = "❌ Montant invalide"
            elif montant > 5000:
                message = "❌ Montant maximum 5000$"
            else:
                profile.balance += montant
                profile.save()
                message = f"✅ {montant}$ ajouté avec succès !"
        except:
            message = "❌ Montant invalide"

    return render(request, "shop/demo_topup.html", {
        "balance": profile.balance,
        "message": message
    })


@login_required
def mark_as_delivered(request, order_id):
    order = get_object_or_404(Purchase, id=order_id)

    if request.user.is_staff:
        order.statut = "livre"
        order.save()

    return redirect('orders')


@login_required
def buy_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    profile = request.user.profile
    prix = Decimal(product.prix)

    if product.quantite <= 0:
        messages.error(request, "Produit en rupture de stock !")
        return redirect('dashboard')

    if profile.balance < prix:
        messages.error(request, "Solde insuffisant !")
        return redirect('dashboard')

    with transaction.atomic():
        profile.balance -= prix
        profile.save()

        product.quantite = max(product.quantite - 1, 0)
        product.save()

        Purchase.objects.create(user=request.user, product=product, prix=prix)

    messages.success(request, f"Vous avez acheté {product.nom} avec succès !")
    return redirect('dashboard')


@login_required
def product_list(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(nom__icontains=query)
    else:
        products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})


@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, f"Produit {product.nom} ajouté !")
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'shop/product_form.html', {'form': form, 'title': 'Ajouter un produit'})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Produit {product.nom} mis à jour !")
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/product_form.html', {'form': form, 'title': 'Modifier le produit'})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, f"Produit {product.nom} supprimé !")
        return redirect('product_list')
    return render(request, 'shop/product_confirm_delete.html', {'product': product})


def signup_view(request):
    if request.method == 'POST':
        form = SignupWithEmailForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Compte créé avec succès !")
            return redirect('login')
    else:
        form = SignupWithEmailForm()
    return render(request, 'shop/signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} !")
            return redirect('dashboard')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect !")
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Vous êtes déconnecté !")
    return redirect('login')


@login_required
def dashboard(request):
    profile = request.user.profile
    products = Product.objects.all()

    # Si admin, ajoute stats
    if request.user.is_staff:
        total_sales = Purchase.objects.aggregate(Sum('prix'))['prix__sum'] or 0
        total_orders = Purchase.objects.count()
        total_clients = User.objects.filter(is_staff=False).count()
        total_products = Product.objects.count()
    else:
        total_sales = total_orders = total_clients = total_products = None

    return render(request, 'shop/dashboard.html', {
        'profile': profile,
        'products': products,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'total_clients': total_clients,
        'total_products': total_products
    })