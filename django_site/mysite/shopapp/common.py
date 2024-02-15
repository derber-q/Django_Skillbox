from csv import DictReader
from io import TextIOWrapper


from .models import Product, Order


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products

def save_csv_orders(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    orders = [
        Order(**row)
        for row in reader
    ]
    Order.objects.bulk_create(orders)
    return orders

def convert_str_to_int_list(string_data):
    bad_chars = ["[", "]", ","]
    filtered_string = filter(lambda i: i not in bad_chars, string_data)
    list_string = "".join(filtered_string).split()
    list_int_data = list(map(int, list_string))
    return list_int_data