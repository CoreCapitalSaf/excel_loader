#Field parsers
As we have seen before on the ExcelSheetParser classes defined, we have a dictionary
class variable called fields on our basic example it looks like this
```
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
```

##Basic field importers
A basic field importer on our example is this one: *0: 'name',*.
This field will be very useful on strings, floats and fields that are correctly 
specified on the xlsx cell, it may have its drawbacks when fields are imported
incorrectly e.g. date fields
 
##FieldImporter
Class created to parse each field and try to force transform them, to use this parsing just
call the FieldImporter class, pass the instance the field_to_set and the data_type you are 
trying to convert it to e.g. *1: FieldImporter(field_to_set='code', data_type=int),*

### Accepted **data_type**
Pass any of those params on the data_type for parsing (as they are listed, types or str) 

1. bool: accepted cell values are 
    - SI 
    - NO
    - YES
    - Y
    - N 
    - if excepts the default will be **False**

2. int: the accepted cell values are numerical, but it will force them to be integers with 
    no decimal places, if excepts the default will be **0**

3. float: the accepted cell values are numerical, and it will force them to be float decimal,
    if excepts the default value will be **0.0**

4. str: the accepted cell values are any, but it may be used for decimals without points in case
    the value is decimal e.g. 1.000 -> 1000 it will cast them to strings no matter what the 
    cell contains, if excepts the default value will be **''** (empty string)

5. 'datetime': the accepted cell values are 
    - '2008-04-19 11:47:58-05'
    - '2008-04-19'
    - '19/04/2008'
    - if excepts the default value will be None

6. '%': the accepted cell values are numerical values, if the value is lower than 1,
    it will be multiplied by 100 to reach to a number between 1 and 100 %, this was made 
    because the % format on the xlsx cell returns a number below 1 when imported using xlrd 


##ModelImporter
Class created to parse each field into a model instance, it works in multiple ways and multiple 
combinations the 2 basic ones are:
1. simple fields: e.g. *ModelImporter(field_to_set='country', lookup_field_name='code', model=Country),*
    - this will work on this type of field definition: 
    country = models.ForeignKey('places.Country', verbose_name='country', on_delete=models.CASCADE)
2. m2m fields: 
    - e.g. *ModelImporter(field_to_set='accounts', lookup_field_name='ruc', model=Fund, fk_type='m2m')*
        This case works on the following example
        ```
        #models.py
        class Client(models.Model):
            document_number = models.CharField(max_length=50, blank=True)
      
      
        class SecondaryMarket(models.Model):
            seller = models.ManyToManyField(Client, verbose_name='vendedor')
        
        #model_parsers.py
        class SecondaryMarketExcelSheetParser(ExcelSheetParser):
            model = SecondaryMarket
            fields = {0: ModelImporter(
                field_to_set='seller', lookup_field_name='document_number',
                model=Client, fk_type='m2m', data_type=str),}
        ```
        As we can see we can set 1 m2m instance as simple as just defining what field will be assigned to, and what 
        data_type it will be parsed as
      
    - e.g. *ModelImporter(field_to_set='accounts', lookup_field_name='ruc', model=Fund, fk_type='m2m', reverse=True)*
        This case works on the following example
        ```
        # models.py
        class BankAccount(models.Model):
            ...
      
      
        class Fund(models.Model):
            ...
            code = models.IntegerField('code', max_length=10, blank=True)
            accounts = models.ManyToManyField(
                BankAccount, related_name='funds')

      
        # model_parsers.py
        class FundBankAccountExcelSheetParser(ExcelSheetParser):
            model = BankAccount
            fields = {0: ModelImporter(
                model=Fund, field_to_set='accounts', lookup_field_name='code',
                fk_type='m2m', reverse=True, data_type=int),}
        ```
        As we can see the model to be imported is **BankAccount**, but this model
        does not have a field called accounts, but **Fund** does have a m2m to **BankAccount**
        so this is why we add the parameter **reverse=True** because it will be set from the model field
3. special cases
    - multiple lookup_field_name s e.g. : **lookup_field_name=['fund__ruc', 'number']**
        for this to work, the cell only needs the values to be separated with a coma
    
    - complex queries e.g. **lookup_field_name=user__document_number__icontains**
        complex queries as for fk models and orm query syntax such as icontains, in, day, month, 
        year and so many others can be normally used
    
    - data_type: if the query for the fk model is not working, it might be because the cell data
        is not arriving correctly at the moment of the query, try forcing it with the supported 
        data conversion on the **Accepted data_type** block above

##NestedModelImporter
Class created to parse the same as a **FieldImporter**, but this field will be store on 
a list that will not be passed on the moment of the instance creation, but instead it's
passed to post processing function on the **extra_operations = dict(post=post)**

it will be listed on the **nested_fields** param

```
def post(self, instance, nested_fields):
    field = nested_fields[0].field_to_set
    value = nested_fields[0].get_value()
    User.objects.create(self.field_to_set=instance, field=value)
```

         