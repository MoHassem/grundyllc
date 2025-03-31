
from django.urls import path

import config.views as cv

urlpatterns = [
    path('view/', cv.config_view, name='config-view'),
    path('update/<int:pk>', cv.config_update, name='config-update'),
    path('delivery-view/', cv.delivery_partner_view, name='delivery-view'),
    path('delivery-add/', cv.delivery_partner_add, name='delivery-add'),
    path('delivery-edit/<int:pk>', cv.delivery_partner_edit, name='delivery-edit'),
    path('delivery-delete/<int:pk>', cv.delivery_partner_delete, name='delivery-delete'),
    path('store-list/', cv.store_list, name='store-view'),
    path('store-create/', cv.store_create, name='store-create'),
    path('store-update/<int:pk>', cv.store_update, name='store-update'),
    path( 'store-delete/<int:pk>', cv.store_delete, name='store-delete'),
]
