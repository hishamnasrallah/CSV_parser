
def generate_csv(column_names, rows):
    yield ','.join(column_names) + '\n'  # Write the header row
    for row in rows:
        yield ','.join([str(cell) for cell in row]) + '\n'
