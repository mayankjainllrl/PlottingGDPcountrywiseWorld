"""
Visualizing log 10 of GDP year wise of all countries on world map
"""

import csv
import math
import pygal


def read_csv_as_nested_dict(filename, keyfield, separator, quote):
    """
    Inputs:
      filename  - Name of CSV file
      keyfield  - Field to use as key for rows
      separator - Character that separates fields
      quote     - Character used to optionally quote fields

    Output:
      Returns a dictionary of dictionaries where the outer dictionary
      maps the value in the key_field to the corresponding row in the
      CSV file.  The inner dictionaries map the field names to the
      field values for that row.
    """
    with open(filename) as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=separator, quotechar=quote)
        dicty = {}
        for row in csvreader:
            dicty[row[keyfield]] = row
    return dicty


def build_plot_values(gdpinfo, gdpdata):
    """
    Inputs:
      gdpinfo - GDP data information dictionary
      gdpdata - A single country's GDP stored in a dictionary whose
                keys are strings indicating a year and whose values
                are strings indicating the country's corresponding GDP
                for that year.

    Output:
      Returns a list of tuples of the form (year, GDP) for the years
      between "min_year" and "max_year", inclusive, from gdpinfo that
      exist in gdpdata.  The year will be an integer and the GDP will
      be a float.
    """
    listy = []
    for key, value in gdpdata.items():
        if key.isnumeric() and value:
            if int(gdpinfo["min_year"]) <= int(key) <= int(gdpinfo["max_year"]):
                listy.append((int(key), float(value)))
    listy.sort(key=lambda pair: pair[0])
    return listy


def build_plot_dict(gdpinfo, code_list):
    """
    Inputs:
      gdpinfo      - GDP data information dictionary
      country_code_list - List of strings that are country codes

    Output:
      Returns a dictionary whose keys are the country code in
      country_list and whose values are lists of XY plot values
      computed from the CSV file described by gdpinfo.

      Countries from country_list that do not appear in the
      CSV file should still be in the output dictionary, but
      with an empty XY plot value list.
    """
    dictionary_of_data = read_csv_as_nested_dict(gdpinfo["gdpfile"],
                                                 gdpinfo["country_code"],
                                                 gdpinfo["separator"],
                                                 gdpinfo["quote"])
    result_dict = {}
    for code in code_list:
        flag = 0
        for code_gdp in dictionary_of_data:
            if code.casefold() == code_gdp.casefold():
                result_dict[code] = build_plot_values(gdpinfo, dictionary_of_data[code_gdp])
                flag = 1
        if flag == 0:
            result_dict[code] = []
    return result_dict


def build_country_code_converter(codeinfo):
    """
    Inputs:
      codeinfo      - A country code information dictionary

    Output:
      A dictionary whose keys are plot country codes and values
      are world bank country codes, where the code fields in the
      code file are specified in codeinfo.
    """
    dict_of_code = read_csv_as_nested_dict(codeinfo["codefile"],
                                           codeinfo["plot_codes"],
                                           codeinfo["separator"],
                                           codeinfo["quote"])
    result_dicty = {}
    for key, val in dict_of_code.items():
        result_dicty[key] = val[codeinfo["data_codes"]]
    return result_dicty


def reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries):
    """
    Inputs:
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      gdp_countries  - Dictionary whose keys are country codes used in GDP data

    Output:
      A tuple containing a dictionary and a set.  The dictionary maps
      country codes from plot_countries to country codes from
      gdp_countries.  The set contains the country codes from
      plot_countries that did not have a country with a corresponding
      code in gdp_countries.

      Note that all codes should be compared in a case-insensitive
      way.  However, the returned dictionary and set should include
      the codes with the exact same case as they have in
      plot_countries and gdp_countries.
    """
    code_converter = build_country_code_converter(codeinfo)
    plot_code = {}
    result_dicty, result_set = {}, set()
    for code in plot_countries:
        for converter in code_converter:
            if code.casefold() == converter.casefold():
                plot_code[code] = code_converter[converter]

    for code, country_code in plot_code.items():
        flag = 0
        for gdp_code in gdp_countries:
            if gdp_code.casefold() == country_code.casefold():
                result_dicty[code] = country_code
                flag = 1
        if flag == 0:
            result_set.add(code)

    for code in plot_countries:
        if code not in plot_code:
            result_set.add(code)

    return result_dicty, result_set


def build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year for which to create GDP mapping

    Output:
      A tuple containing a dictionary and two sets.  The dictionary
      maps country codes from plot_countries to the log (base 10) of
      the GDP value for that country in the specified year.  The first
      set contains the country codes from plot_countries that were not
      found in the GDP data file.  The second set contains the country
      codes from plot_countries that were found in the GDP data file, but
      have no GDP data for the specified year.
    """
    dictionary_of_country_codes = read_csv_as_nested_dict(gdpinfo["gdpfile"],
                                                          gdpinfo["country_code"],
                                                          gdpinfo["separator"],
                                                          gdpinfo["quote"])

    dict_code_code, first_set = reconcile_countries_by_code(codeinfo,
                                                            plot_countries,
                                                            dictionary_of_country_codes)

    dict_countries_year_gdp = build_plot_dict(gdpinfo, dict_code_code.values())
    result_dicty = {}
    second_set = set()
    for code, country_code in dict_code_code.items():
        flag = 0
        for itr_year_gdp in dict_countries_year_gdp[country_code]:
            if itr_year_gdp[0] == int(year):
                result_dicty[code] = math.log10(itr_year_gdp[1])
                flag = 1
        if flag == 0:
            second_set.add(code)
    return result_dicty, first_set, second_set


def render_world_map(gdpinfo, codeinfo, plot_countries, year, map_file):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year of data
      map_file       - String that is the output map file name

    Output:
      Returns None.

    Action:
      Creates a world map plot of the GDP data in gdp_mapping and outputs
      it to a file named by svg_filename.
    """
    gdp, world_bank_missing, no_data_for_year = build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year)
    worldmap_chart = pygal.maps.world.World()
    worldmap_chart.title = f"GDP by country for {year} (log based), unified by common country names"
    worldmap_chart.add(f'GDP for {year}', gdp)
    worldmap_chart.add('Missing From World Bank Data', world_bank_missing)
    worldmap_chart.add(f'No Data Found For {year}', no_data_for_year)
    worldmap_chart.render_in_browser()  # Renders image to your browser
    worldmap_chart.render_to_png(map_file)  # Creates png image of your project


def test_render_world_map():
    gdpinfo = {
        "gdpfile": "isp_gdp.csv",
        "separator": ",",
        "quote": '"',
        "min_year": 1960,
        "max_year": 2015,
        "country_name": "Country Name",
        "country_code": "Country Code"
    }
    codeinfo = {
        "codefile": "isp_country_codes.csv",
        "separator": ",",
        "quote": '"',
        "plot_codes": "ISO3166-1-Alpha-2",
        "data_codes": "ISO3166-1-Alpha-3"
    }
    pygal_countries = pygal.maps.world.COUNTRIES

    year = int(input(f"Enter any year between {gdpinfo['min_year']} and {gdpinfo['max_year']}"))

    render_world_map(gdpinfo, codeinfo, pygal_countries, year, f"isp_gdp_world_code_{year}.png")


test_render_world_map()
