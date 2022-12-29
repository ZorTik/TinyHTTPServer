from tinyhttpserver import Server

server = Server(port=3000)


@server.route("/")
def index():
    return "index"


@server.route("/api")
def route1():
    return "route1"


@server.route("/api/user/{api_id}")
def route1(api_id: str):
    return f"ID: {api_id}"


if __name__ == '__main__':
    server.run_server()
