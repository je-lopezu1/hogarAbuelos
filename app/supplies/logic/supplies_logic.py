from ..models import Supply

def get_all_supplies():
    return Supply.objects.all()

def create_supply(supply_data):
    Supply.objects.create(name=supply_data['name'])

def delete_supply(supply_id):
    Supply.objects.get(id=supply_id).delete()

def update_supply(supply_id, supply_data):
    supply = Supply.objects.get(id=supply_id)
    supply.name = supply_data['name']
    supply.save()