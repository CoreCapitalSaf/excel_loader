# Excel loader

Excel loader is a Django app to import excels to Django databases defined on models.py files


## Quick start

1. Add "excel_loader", to your INSTALLED_APPS settings.py like this:

	Code:
		
		INSTALLED_APPS = [
			...
			'excel_loader',
		]

    
2. Excel structure

    Define an excel file with sheets names related to your model name e.g. sheet name: **Funds**,
    then define the header with fields from the model. 
    The header is there for visual purposes only, perhaps it will be easier for the ones in charge of filling the excel, 
    also to keep in mind that the algorithm will not load the first row

    * File: funds.models.py
	
		Code:
	
			class Country(models.Model):
				name = models.CharField('name', max_length=50)
				code = models.CharField('code', max_length=10, blank=True)
			
			class Fund(models.Model):
				name = models.CharField('name', max_length=50)
				code = models.IntegerField('code', max_length=10, blank=True)
				country = models.ForeignKey(
					'places.Country', verbose_name='country', on_delete=models.CASCADE)

    
	* Excel sheet: Funds where column A, B, C fit Name, Code and Country respectively
	
		Table:
	
			| Name                | Code  | Country (Code)  |
			| ------------------- | ----- | --------------- |
			| Investments fund 1  | 1     | PE              |
    		| Investments fund 2  | 2     | US              |


3. FundExcelSheetParser

    To parse this excel sheet we will have to create a class e.g. **FundExcelSheetParser** 
    that inherits from the class ExcelSheetParser (from excel_loader.loader) on a new file named
    **model_parsers.py** by convention on the app where the data will be imported to
    
    Code:


		from funds.models import Fund, Country
		
		
		class FundExcelSheetParser(ExcelSheetParser):
			model = Fund
			fields = {
				0: 'name',
				1: FieldImporter(field_to_set='code', data_type=int),
				2: ModelImporter(
					model=Country, field_to_set='country', lookup_field_name='code'),
				}

    
    **For more information on**
    
    - FieldImporter and ModelImporter go to [Field parsers](docs/types.md)
    - ExcelSheetParser and its different functionalities go to [Excel sheet parsers](docs/loader.md)
    
4. Create a custom command on the app you will be importing the models to e.g.

    ```    
    app_name/management/commands/custom_command.py
    ```

5. Command structure

	* On the handle function open the excel file previously defined
	
		Code:
	
			wb = xlrd.open_workbook(os.path.join(finders.find(os.path.join(
				'static_files_folder', 'custom_command.xlsx'))))
	
	* Then define the Parsers to be used to load the data on the sheet name as a key e.g.
	
		Code:
	
			sheets_funds = {'Fondos': FundExcelSheetParser}
				
	* Finally to start the data migration, import and call the loading class
	
		Code:
	
			from excel_loader.loader import ExcelCommandLoader
			
			
			ExcelCommandLoader(sheets_funds, wb).load()

	   