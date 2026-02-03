from django.db import models
from ..Company import Company
from ..fuel_type import FuelType
from .fuel_cost import FuelCost

class FuelCostCheck(models.Model):
  
    fuel_cost_check_id=models.AutoField(primary_key=True)
    
    company=models.ForeignKey(Company,on_delete=models.PROTECT)
    
    TYPE="type"
    VOLUME_UNITS="volume_units"
    VOLUME_RATIO="volume_ratio"
    COST_RATIO="cost_ratio"
    
    type_choices=[
        (TYPE,"Validate that fuel types of cost record and asset are equal."),
        (VOLUME_UNITS,"Validate that fuel volume units of cost record and asset are equal."),
        (VOLUME_RATIO,"Validate that fuel volume of cost record relative to fuel tank capacity of asset is below a configurable ratio."),
        (COST_RATIO,"Validate that cost per unit of fuel is below a configurable threshold.")
    ]
    type=models.CharField(choices=type_choices,max_length=20)
    
    def get_human_readable_type(self):
        return FuelCostCheck.get_all_types().get(self.type)
    
    @staticmethod
    def get_all_types():
        dict={}
        for (key,value) in FuelCostCheck.type_choices:
            dict[key]=value
        return dict
    
    @staticmethod
    def get_unique_per_company_key(object):
        if object.type==FuelCostCheck.COST_RATIO:
            return "%s-%s-%s"%(object.type,object.cost_ratio_type.name,object.cost_ratio_units)
        return object.type
    
    volume_ratio_threshold=models.FloatField(default=0)

    cost_ratio_type=models.ForeignKey(FuelType,null=True,on_delete=models.SET_NULL)
    cost_ratio_units=models.CharField(choices=FuelCost.volume_unit_choices,max_length=50,null=True)
    cost_ratio_threshold=models.FloatField(default=0)