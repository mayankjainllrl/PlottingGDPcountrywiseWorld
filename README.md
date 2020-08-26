### Contact Author :- 
mayankjainllrl@gmail.com

### LinkedIn :- 
https://www.linkedin.com/in/mayank-jain-731325148/

#### Instructions
I have provided with a requirements.txt File so you can create a new venv on your system so that the program runs smoothly without any errors.(Recommended)

Moreover 
If you dont want to set a new venv then the important modules are :-
1. pygal (Data visualization library used in this code)
2. pygal.maps.world (Required for country codes)
3. cairosvg (For creating png image)
4. lxml (For rendering in browser)

I have provided with two csv files in this module :-
1. isp_country_codes.csv (World Bank country codes)
2. isp_gdp.csv (Contains year wise gdp info for all countries)

##### For using your own data 
For using your data you just have to change few parameters in :-
1. gdpinfo dictionary
2. codeinfo dictionary 
Present in test_render_world_map() function.

###### gdpinfo dictionary 
It contains 
1. "gdpfile": the name of the CSV file that contains GDP data.
2. "separator": the delimiter character used in the CSV file.
3. "quote": the quote character used in the CSV file.
4. "min_year": the oldest year for which there is data in the CSV file.
5. "max_year": the most recent year for which there is data in the CSV file.
6. "country_name": the name of the column header for the country names.
7. "country_code": the name of the column header for the country codes.

###### codeinfo dictionary 
It contains
1. "codefile": the name of the CSV file that contains country codes.
2. "separator": the delimiter character used in the CSV file.
3. "quote": the quote character used in the CSV file.
4. "plot_codes": the name of the column header that holds the country codes used by the plot library.
5. "data_codes": the name of the column header that holds the country codes used by the GDP data.
    
