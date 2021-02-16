# ExcelSheetParser

To go into details of how the sheet parser work and its multiple details
we are going start from the same basic example

    Code:

        from funds.models import Fund, Country


		class FundExcelSheetParser(ExcelSheetParser):
			model = Fund
			fields = {
				0: 'name',
				1: FieldImporter(field_to_set='code', data_type=int),
				2: ModelImporter(
					model=Country, field_to_set='country',
					lookup_field_name='code'),
			}


With this example we can observe the ExcelSheetParser which is a
base class for the parser object that every model_parsers on the app should
inherit from to be a model class parser from excels.


## Mandatory class attributes

Its most basic implementation should always contain a **model** and **fields**, where

- model: a models.Model instance e.g. User

- fields: a dict that contains the mapping from the excel sheet 
to the field e.g. fields = {0:'number', 1:'fund_type'} where 0 should match the
alphabetical column 0=A.  

## Optional class attributes

On some cases, there are certain attributes that can be added by default on all 
the instances being imported, for those cases, the algorithm processes a dictionary called
**extra_operations = dict(pre=pre, post=post)** where both pre and post are functions e.g.

    Code:
    
		def pre(self, fields, inverse_relations=[]):
			fields['state'] = User.ACTIVE
			fields['fk_field'] = inverse_relations[0].get_value().fk_field
			return fields
		
		def post(self, instance, nested_fields):
			field = nested_fields[0].field_to_set
			value = nested_fields[0].get_value()
			User.objects.create(self.field_to_set=instance, field=value)


Those functions will work on different ways:

- pre function will receive 2 parameters:
    - fields: a dict containing the kwargs to be saved, add extra fields variables 
    e.g static variables set due to importing exceptions

    - inverse_relations: a list with ModelImporters inverse relations, on the ModelImporter 
    instance can be loaded with a fk model fk field e.g. an instance fk instance we need it 
    to be the same due to importing

- post function will receive 2 parameters
    - instance: a model instance to be added on nested object trying to save
    
    - nested_fields: a list stacked with NestedModelImporter to be added after the main model 
    has already been created e.g. new model instances to be created with the passed instance
    and the data from the NestedModelImporter s
