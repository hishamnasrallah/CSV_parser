from fastapi import Request
from urllib.parse import urlparse, parse_qs, urlunsplit, urlencode


def paginator(request: Request, data, page_num: int = 1, page_size: int = 10):
    parsed_url = urlparse(str(request.url))

    query_params = parse_qs(parsed_url.query)
    try:
        page_num = int(query_params.get('page_num', [1])[0])
    except:
        page_num = page_num

    try:
        page_size = int(query_params.get('page_size', [10])[0])
    except:
        page_size = page_size



    start = (page_num - 1) * page_size
    end = start + page_size
    data_length = len(data)
    response = {
        "data": data[start:end],
        "total": data_length,
        "count": page_size,
        "pagination": {}
                }


    if end >= data_length:
        response["pagination"]["next"] = None
        if page_num > 1:
            query_params['page_num'] = page_num-1
            query_params['page_size'] = page_size
            new_query_string = urlencode(query_params, doseq=True)
            url = urlunsplit(("", "", parsed_url.path, new_query_string, ""))
            response["pagination"]["previous"] = url
        else:
            response["pagination"]["previous"] = None
    else:
        if page_num > 1:
            query_params['page_num'] = page_num-1
            query_params['page_size'] = page_size
            new_query_string = urlencode(query_params, doseq=True)
            url = urlunsplit(("", "", parsed_url.path, new_query_string, ""))
            response["pagination"]["previous"] = url
        else:
            response["pagination"]["previous"] = None

        query_params['page_num'] = page_num + 1
        query_params['page_size'] = page_size
        new_query_string = urlencode(query_params, doseq=True)
        url = urlunsplit(("", "", parsed_url.path, new_query_string, ""))
        response["pagination"]["next"] = url

    return response
