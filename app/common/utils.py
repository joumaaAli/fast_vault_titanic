import hashlib


def anonymize_data(data, columns):
    for column in columns:
        if column in data.columns:
            data[column] = data[column].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest())
    return data