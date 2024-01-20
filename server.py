"""
 HTTP Server Shell
 Author: Barak Gonen ,Nir Dweck and Ido Shema
 Purpose: Provide a basis for Ex. 4
 Note: The code is written in a simple way, without classes, log files or
 other utilities, for educational purpose
 Usage: Fill the missing functions and constants
"""
import socket
import os
import mimetypes

DEFAULT_URL = "/index.html"
ROOT_WEB = "C:/Users/User/PycharmProjects/targil4/ROOT-WEB"
REDIRECTION_DICTIONARY = {'/moved': '/'}
QUEUE_SIZE = 10
ERROR404 = "C:/Users/User/PycharmProjects/targil4/ROOT-WEB/imgs/404_not_found.jpg"
ERROR500 = "C:/Users/User/PycharmProjects/targil4/ROOT-WEB/imgs/500_internal_error.png"
ERROR400 = "C:/Users/User/PycharmProjects/targil4/ROOT-WEB/imgs/400_bad_request.png"
ERROR403 = "C:/Users/User/PycharmProjects/targil4/ROOT-WEB/imgs/403_forbidden.png"
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 2


def get_file_data(file_name):
    """
        Get data from file
        :param file_name: the name of the file
        :return: the file data in a string
    """
    try:
        with open(file_name, 'rb') as file:
            return file.read()
    except FileNotFoundError:
        return b''


def validate_http_request(request):
    """
        Check if request is a valid HTTP request and returns TRUE / FALSE and
        the requested URL
        :param request: the request which was received from the client
        :return: a tuple of (True/False - depending if the request is valid,
        the requested resource )
    """
    request_lines = request.split(b'\r\n')
    if len(request_lines) > 0 and request_lines[0].startswith(b'GET'):
        parts = request_lines[0].split(b' ')
        if len(parts) == 3 and parts[2].endswith(b'HTTP/1.1'):
            return True, parts[1].decode('utf-8')
    return False, ''


def bad_request(client_socket):
    """
        return the handle for 400 bad_request
        :param client_socket: a socket for the communication with the client
        :return: None
        """
    data = get_file_data(ERROR400)
    http_response = ('HTTP/1.1 400 BAD REQUEST\r\nContent-Type: image/jpeg\r\n' +
                     f'Content-Length: {len(data)}\r\n\r\n').encode() + data
    client_socket.send(http_response)
    return


def handle_client_request(resource, client_socket):
    """
        Check the required resource, generate proper HTTP response and send
        to client
        :param resource: the required resource
        :param client_socket: a socket for the communication with the client
        :return: None
    """
    if resource == '/':
        resource = DEFAULT_URL

    if resource.startswith('/forbidden'):
        data = get_file_data(ERROR403)
        http_response = ('HTTP/1.1 403 FORBIDDEN\r\nContent-Type: image/jpeg\r\n' +
                         f'Content-Length: {len(data)}\r\n\r\n').encode() + data
        client_socket.send(http_response)
        return

    if resource.startswith('/moved'):
        http_response = 'HTTP/1.1 302 TEMPORARY REDIRECT\r\nLocation: /\r\n\r\n'.encode()
        client_socket.send(http_response)
        return

    if resource.startswith('/error'):
        data = get_file_data(ERROR500)
        print(data)
        http_response = ('HTTP/1.1 500 ERROR SERVER INTERNAL\r\nContent-Type: image/jpeg\r\n' +
                         f'Content-Length: {len(data)}\r\n\r\n').encode() + data
        client_socket.send(http_response)
        return
    file_path = os.path.join(ROOT_WEB, resource[1:])
    file_type, encoding = mimetypes.guess_type(file_path)
    if file_type:
        http_header = f'HTTP/1.1 200 OK\r\nContent-Type: {file_type}; charset=utf-8\r\n'
        data = get_file_data(file_path)
        http_response = (http_header + f'Content-Length: {len(data)}\r\n\r\n').encode() + data
        client_socket.send(http_response)
        return
    else:
        data = get_file_data(ERROR404)
        http_response = ('HTTP/1.1 404 NOT FOUND\r\nContent-Type: image/jpeg\r\n' +
                         f'Content-Length: {len(data)}\r\n\r\n').encode() + data
        client_socket.send(http_response)
        return


def handle_client(client_socket):
    """
        Handles client requests: verifies client's requests are legal HTTP, calls
        function to handle the requests
        :param client_socket: the socket for the communication with the client
        :return: None
    """
    print('Client connected')
    while True:
        client_request = client_socket.recv(1024)
        if not client_request:
            break

        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print('Got a valid HTTP request')
            handle_client_request(resource, client_socket)
        else:
            print('Error: Not a valid HTTP request')
            bad_request(client_socket)
            break

    print('Closing connection')
    client_socket.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print("Listening for connections on port %d" % PORT)

        while True:
            client_socket, client_address = server_socket.accept()
            try:
                print('New connection received')
                client_socket.settimeout(SOCKET_TIMEOUT)
                handle_client(client_socket)
            except socket.error as err:
                print('Received socket exception - ' + str(err))
            finally:
                client_socket.close()
    except socket.error as err:
        print('Received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
