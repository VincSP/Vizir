def selection_in_options(selection, options):
    if not selection:
        return True

    if not isinstance(selection, (tuple, list)):
        selection = [selection]

    all_option_values = {itm['value'] for itm in options}
    return all(map(lambda item: item in all_option_values, selection))
