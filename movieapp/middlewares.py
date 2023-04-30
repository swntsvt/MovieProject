class RequestCountMiddleware:
    total_requests = 0

    def __init__(self, get_response):
        self.get_response = get_response

    @classmethod
    def set_total_requests(cls, value):
        cls.total_requests = value
        print("**** reset total requests to : ", cls.total_requests)

    def __call__(self, request):
        RequestCountMiddleware.total_requests += 1
        request.count = RequestCountMiddleware.total_requests

        # Call the next middleware or view function
        response = self.get_response(request)

        return response
