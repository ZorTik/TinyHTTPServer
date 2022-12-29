import inspect

from http.server import HTTPServer, BaseHTTPRequestHandler

# Server storage dictionary for accessibility of Server
# instances for the RequestHandler.
server_dict = dict()


class RequestHandler(BaseHTTPRequestHandler):
    """
    An request handler class
    """
    def do_GET(self):
        """
        Handles HTTP GET request from Server class.
        """
        content = server_dict[self.server.server_address].invoke(self.path)
        if content is not None:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(content, encoding="utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


class Server:
    """
    Main server class that stored routes and parses incoming
    requests.
    """
    server: HTTPServer
    routes = {}

    def __init__(self, address="127.0.0.1", port=3000):
        self.address = address
        self.port = port
        server_dict[(address, port)] = self

    def route(self, path: str):
        """
        Route decorator used for implementing route path handler
        functions.

        :param path: Path format.
        :return: The decorator.
        """
        def decorate(func):
            def wrapper(invocation_path: str):
                inv_parts = invocation_path.split("/")
                parts = path.split("/")

                if len(parts) != len(inv_parts):
                    return None

                def is_placeholder(s: str):
                    return s.startswith("{") and s.endswith("}")

                def validate_path() -> bool:
                    for index in range(0, len(inv_parts)):
                        if not is_placeholder(parts[index]) and inv_parts[index] != parts[index]:
                            return False
                    return True

                if not validate_path():
                    return None

                placeholder_values = dict()

                for i in range(0, len(inv_parts)):
                    inv = inv_parts[i]
                    if is_placeholder(parts[i]):
                        placeholder_values[parts[i][1:(len(parts[i]) - 1)]] = inv

                arg_names = inspect.getfullargspec(func)[0]
                arg_values = []
                for arg_name in arg_names:
                    if arg_name in placeholder_values:
                        arg_values.append(placeholder_values[arg_name])
                    else:
                        arg_values.append(None)

                return func(*arg_values)

            self.routes[path] = wrapper
            return wrapper

        return decorate

    def invoke(self, path: str):
        """
        Finds and invokes decorated handlers where first
        successful handler is used as output. Otherwise,
        NoneType is returned.

        :param path: Incoming HTTP request path.
        :return: Content of the page.
        """
        for func in self.routes.values():
            result = func(path)
            if result is not None:
                return result

        return None

    def run_server(self):
        """
        Creates and runs new HTTP server. This method is
        blocking.
        """
        self.server = HTTPServer((self.address, self.port), RequestHandler)

        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            pass

        self.server.server_close()
