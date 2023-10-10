from prometheus_client import Counter, make_asgi_app


# based on https://medium.com/python-in-plain-english/adding-prometheus-to-a-fastapi-app-python-e038bccdd502
metrics_app = make_asgi_app()


all_requests = Counter('all_requests', 'A counter of the all requests made')
