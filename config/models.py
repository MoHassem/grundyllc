from django.db import models

class StorefrontConfiguration(models.Model):
    CHARGE_TYPE_CHOICES = [
        ('flat', 'Flat Fee'),
        ('percentage', 'Percentage'),
    ]
    basket_charge_type = models.CharField(
        max_length=10,
        choices=CHARGE_TYPE_CHOICES,
        default='flat',
        help_text="Type of charge per basket (flat fee or percentage)"
    )
    basket_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="The charge per basket, based on the charge type"
    )
    delivery_charge_per_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Delivery charge per kilometer"
    )
    threshold_distance_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Threshold distance for additional delivery charges (in km)"
    )
    additional_charge_per_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Additional charge per km beyond the threshold distance"
    )
    maximum_distance_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Maximum distance for delivery (in km)"
    )
    def __str__(self):
        return (f"basket charge {self.basket_charge_type} {self.basket_charge_type}, "
                f"delivery charge p/km: {self.delivery_charge_per_km}, threhold: {self.threshold_distance_km} km, "
                f"threhold charge: {self.additional_charge_per_km}, Max Distance: {self.maximum_distance_km} km)")


class DeliveryPartner(models.Model):
    BANK_CHOICES = [
        ('140', 'ABSA'),
        ('151', 'FNB'),
        ('157', 'Nedbank'),
        ('163', 'Standard'),
    ]
    name = models.CharField(
        max_length=50,
        help_text="Name of the delivery partner"
    )
    settlement_bank = models.CharField(
        max_length=10,
        choices=BANK_CHOICES,
        default='140',
        help_text="Bank code for payment"
    )
    account_number = models.CharField(
        max_length=15,
        help_text="Bank account number for payments",
        default=None
    )
    subaccount_code = models.CharField(
        max_length=100,
        help_text="Subaccount code for transactions",
        default=None,
        null=True
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Delivery partner active?"
    )

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"


class Store(models.Model):
    BANK_CHOICES = [
        ('140', 'ABSA'),
        ('151', 'FNB'),
        ('157', 'Nedbank'),
        ('163', 'Standard'),
    ]

    business_name = models.CharField(
        max_length=100,
        help_text="Name of the business managing the store"
    )
    settlement_bank = models.CharField(
        max_length=10,
        choices=BANK_CHOICES,
        default='140',
        help_text="Bank code for settlement"
    )
    account_number = models.CharField(
        max_length=15,
        help_text="Bank account number for settlements"
    )
    percentage_charge = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percentage charge applied to transactions"
    )
    description = models.TextField(
        help_text="Description of the store",
        default=None,
        null=True
    )
    subaccount_code = models.CharField(
        max_length=100,
        help_text="Subaccount code for transactions",
        default=None,
        null=True
    )

    def __str__(self):
        return f"{self.business_name} - {self.settlement_bank} | {self.account_number}"

