from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import loader

import paystack.sub_accounts as psa

from .forms import StorefrontConfigurationForm, DeliveryPartnerForm, StoreForm
from .models import StorefrontConfiguration, DeliveryPartner, Store

# this is the initial view to setup the store front configuration
def config_view(request):
    create_default_config(pk=1)
    storefront_config = get_object_or_404(StorefrontConfiguration, pk=1)
    config_form = StorefrontConfigurationForm(instance=storefront_config)
    context = {
        'config_form': config_form,
    }
    return render(request, 'config/config.html', context)

# update the configuration
def config_update(request, pk):
    msg = ''
    storefront_config = get_object_or_404(StorefrontConfiguration, pk=pk)
    if request.method == 'POST':
        config_form = StorefrontConfigurationForm(request.POST, instance=storefront_config)
        if config_form.is_valid():
            config_form.save()
            msg = 'Storefront configuration updated successfully.'
    else:
        config_form = StorefrontConfigurationForm(instance=storefront_config)
    print(f'{msg=}')
    context = {
        'config_form': config_form,
        'message': msg,
    }
    template = loader.get_template('config/config_form.html')
    return HttpResponse(template.render(context, request))

# this creates a default config if the config does not exist
def create_default_config(pk: int):
    if not StorefrontConfiguration.objects.filter(pk=pk).exists():
        StorefrontConfiguration.objects.create()

# this displays the delivery partners
def delivery_partner_view(request):
    delivery_partner_form = DeliveryPartnerForm()
    delivery_partner_list = DeliveryPartner.objects.all()
    dp_message = ''
    context = {
        'dp_form': delivery_partner_form,
        'dp_list': delivery_partner_list,
        'dp_message': dp_message,
    }
    template = loader.get_template('config/delivery_partner.html')
    return HttpResponse(template.render(context, request))

# this adds a delivery partner and creates a subaccount for the delivery partner and saves the subaccount code
def delivery_partner_add(request):
    dp_message = ''
    form = DeliveryPartnerForm()
    if request.method == 'POST':
        form = DeliveryPartnerForm(request.POST)
        if form.is_valid():
            dp_rec = form.save(commit=False)
            dp_rec.subaccount_code = psa.register_account(
                name=dp_rec.name,
                bank_id=dp_rec.settlement_bank,
                account=dp_rec.account_number,
                percentage=0.00,
            )
            dp_rec.save()
            dp_message = 'Delivery partner added successfully.'
    delivery_partner_list = DeliveryPartner.objects.all()
    context = {
        'dp_form': form,
        'dp_list': delivery_partner_list,
        'dp_message': dp_message,
    }
    template = loader.get_template('config/delivery_form_list.html')
    return HttpResponse(template.render(context, request))

# edit a delivery partner (we can only change the name and description on the subaccount)
def delivery_partner_edit(request, pk):
    dp = DeliveryPartner.objects.get(pk=pk)
    form = DeliveryPartnerForm(instance=dp)
    dp_list = DeliveryPartner.objects.all()
    context = {
        'dp_form': form,
        'dp_list': dp_list,
        'dp_message' : 'Delivery partner deleted successfully.'
    }
    template = loader.get_template('config/delivery_form_list.html')
    return HttpResponse(template.render(context, request))

# delete a delivery partner (subaccount must be deleted on the platform)
def delivery_partner_delete(request, pk):
    dp = DeliveryPartner.objects.get(pk=pk)
    dp.delete()
    dp_list = DeliveryPartner.objects.all()
    form = DeliveryPartnerForm()
    context = {
        'dp_form': form,
        'dp_list': dp_list,
        'dp_message' : 'Delivery partner deleted successfully.'
    }
    template = loader.get_template('config/delivery_form_list.html')
    return HttpResponse(template.render(context, request))

# list all the stores we have on the store front
def store_list(request):
    form = StoreForm()
    stores = Store.objects.all()
    message = ''

    context = {
        'form': form,
        'stores': stores,
        'message': message,
    }

    return render(request, 'config/storemanager.html', context)

# create a new store and associated sub account
def store_create(request):
    message = ''
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store_rec = form.save(commit=False)
            store_rec.subaccount_code = psa.register_account(
                name=store_rec.business_name,
                bank_id=store_rec.settlement_bank,
                account=store_rec.account_number,
                percentage=float(store_rec.percentage_charge),
            )
            store_rec.save()
            message = 'Store added successfully.'
            form = StoreForm()  # Reset the form after saving
    else:
        form = StoreForm()

    stores = Store.objects.all()
    context = {
        'form': form,
        'message': message,
        'stores': stores,
    }

    template = loader.get_template('config/store_form.html')  # Template for rendering the store form
    return HttpResponse(template.render(context, request))

# update a store record
def store_update(request, pk):
    message = ''
    store = get_object_or_404(Store, pk=pk)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            store_rec = form.save(commit=False)
            psa.update_account(
                subaccount_code=store_rec.subaccount_code,
                name=store_rec.business_name,
                description=store_rec.description,
            )
            form.save()
            message = 'Store updated successfully.'
    else:
        form = StoreForm(instance=store)
        message = 'Change the store details below.'

    stores = Store.objects.all()
    context = {
        'form': form,
        'message': message,
        'stores': stores,
    }

    template = loader.get_template('config/store_form.html')
    return HttpResponse(template.render(context, request))

# delete a store record (subaccount to be deleted manually)
def store_delete(request, pk):
    store = Store.objects.get(pk=pk)
    store.delete()
    message = 'Store deleted successfully.'
    form = StoreForm()

    stores = Store.objects.all()
    context = {
        'form': form,
        'message': message,
        'stores': stores,
    }

    template = loader.get_template('config/store_form.html')
    return HttpResponse(template.render(context, request))
