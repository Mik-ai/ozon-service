from business.products import MassProductsEditor


def default_pipeline_edit_name_and_description(
    items: list, re_pattern: str, test_word: str
):
    editor = MassProductsEditor()
    step = 1000
    item_chunks = (items[x : x + step] for x in range(0, len(items), step))

    for i in item_chunks:
        editor.collect_products(i)
        editor.re_edit_name(re_pattern, "", test_word=test_word)
        editor.re_edit_desc(re_pattern, "", test_word=test_word)
        editor.commit_changes()
