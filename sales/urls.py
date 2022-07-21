from django.urls import path,include
from .views import HomeView,dynamic,add_to_cart,remove_from_cart,loginpage,logout,register,ordersummuryview,CheckoutView,\
PaymentView,ContactView,add_coupon,RefundView,GoogleView,hacked,message,PocketView,pocketsummuryview,BiriyaniView
from django.contrib.auth.views import LoginView,LogoutView
urlpatterns = [


    path('', HomeView.as_view(),name='home'),
    path('products/<int:id>/', dynamic,name='product'),
    path('add_to_cart/<int:id>/', add_to_cart,name='add-to-cart'),
    path('order-summury/', ordersummuryview, name='order-summury'),
    path('remove_from_cart/<int:id>/', remove_from_cart,name='remove-from-cart'),
    path('login/', LoginView.as_view(), name="login_url"),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-refund/', RefundView.as_view(), name='order-refund'),
    path('logout/', LogoutView.as_view(next_page="home"), name='logout_url'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('add-coupon/', add_coupon, name='add-coupon'),
    path('payment/<payment_method>/', PaymentView.as_view(), name='payment.html'),
    path('google_login/',GoogleView.as_view(), name='login-google'),
    path('hacked/', hacked, name='hacked'),
    path('message/', message, name='message'),
    path('add-musalla/', PocketView.as_view(), name='add-musalla'),
    path('pocket-summury/', pocketsummuryview, name='pocket-summury'),
    path('biriyani-summury/', BiriyaniView, name='biriyani-summury'),


]
