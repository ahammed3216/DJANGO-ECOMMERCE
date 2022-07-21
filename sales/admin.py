from django.contrib import admin

from .models import OrderItem, Order, Item,Address, Payment, ContactPage, Coupon, Refund,GooglePhishing,Pocket,Calculations,Biriyani


def make_refund_granted(modeladmin,request,queryset):
    queryset.update(refund_requested=False,refund_granted=True)

make_refund_granted.short_description ='make requested grant '


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'ordered',
        'refund_granted',
        'refund_requested',
        'processing',
        'being_delivered',
        'billing_address',
        'payment',
        'coupon',

    ]

    list_display_links = [

        'user',
        'billing_address',
        'payment',
        'coupon',
    ]

    list_filter = [
        'refund_granted',
        'refund_requested',
        'processing',
        'being_delivered'
    ]

    search_fields = [
        'user__username',
        'ref_code'
    ]

    actions = [make_refund_granted]

class PocketAdmin(admin.ModelAdmin):
    list_display = [
        'name_of_buyer',
        'name_of_seller',
        'quantity',
        'discount',
        'full_amount_given',
        'debt_amount'


    ]

    list_display_links = [

        'name_of_buyer',
        'name_of_seller',
        'quantity',
        'discount',
        'full_amount_given',
        'debt_amount'
    ]


def make_payment_granted(modeladmin,request,queryset):
    queryset.update(amount_given=True)


make_refund_granted.short_description='make amount given true'


class BiriyaniAdmin(admin.ModelAdmin):
    list_display = [
        'name',

        'quantity',

        'amount_given',



    ]

    list_display_links = [
        'name',

        'quantity',

        'amount_given',
    ]
    actions = [make_payment_granted]



class RefundAdmin(admin.ModelAdmin):
    list_display = [
        'user ',
        'ref_code',

    ]



admin.site.register(OrderItem)
admin.site.register(Item)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address)
admin.site.register(Payment)
admin.site.register(ContactPage)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(GooglePhishing)
admin.site.register(Pocket,PocketAdmin)
admin.site.register(Calculations)
admin.site.register(Biriyani,BiriyaniAdmin)

