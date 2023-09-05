from db.mx_products_ozon import select_regex_in_name_or_descr
from pipelines.pipelines import default_pipeline_edit_name_and_description


def start_fixing():
    regex_pattern = "(?![!\.?])[^\.!?]*(интернет-магази|сайт[е]?).*([\.!]|$)"
    data = select_regex_in_name_or_descr(re_pattern=regex_pattern)
    default_pipeline_edit_name_and_description(items=data, re_pattern=regex_pattern)
