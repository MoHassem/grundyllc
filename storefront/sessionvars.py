import json
from decimal import Decimal

import attr
from attrs import define, field

@define
class SessionVars:
    shopping_store: str = field(init=True, default='0')
    shopping_cart: list[dict[str:str]] = field(init=True, factory=list)
    shopping_store_total_cents: int = field(init=True, default=0)
    delivery_charge_cents: int = field(init=True, default=0)
    delivery_partner_id: int = field(init=True, default=0)
    delivery_partner_name: str = field(init=True, default=None)
    user_id: str = field(init=True, default='1')
    isCheckout: bool = field(init=True, default=False)

    @property
    def shopping_store_total(self):
        return Decimal(self.shopping_store_total_cents/100).quantize(Decimal('0.00'))

    @property
    def delivery_charge(self):
        return Decimal(self.delivery_charge_cents/100).quantize(Decimal('0.00'))

    @shopping_store_total.setter
    def shopping_store_total(self, value: Decimal):
        self.shopping_store_total_cents = int(value*100)

    @delivery_charge.setter
    def delivery_charge(self, value: Decimal):
        self.delivery_charge_cents = int(value*100)

def get_session_vars(request):
    sv_json = request.session.get('session_vars', None)
    if not sv_json:
        return SessionVars()
    js_dict = json.loads(sv_json)
    return SessionVars(**js_dict)

def save_session_vars(request, session_vars: SessionVars):
    request.session['session_vars'] = json.dumps(attr.asdict(session_vars))

def clear_session_vars():
    return SessionVars()
