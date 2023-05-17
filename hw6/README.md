## Overview
Design and implement a pair of web client program and web server program that support the HTTP 1.0, HTTP 1.1, HTTP 2.0 protocols and HTTP 3.0 protocols, respectively.

## HTTP/1.0
- Request and response are in plain text.
- Each request needs to create a new connection.

## HTTP/1.1
- Request and response are in plain text.
- The connection between the client the and server will be kept for a while and multiple requests/responses can be transferred over the same connection.

#### HTTP/1.X Request Format
```
<Request>::= <method> <resource> <HTTP-version>\r\n<headers>\r\n<body>
    <method>::= "GET" | "POST"
    <resource>::= <path>[<query>]
    <HTTP-version>::= “HTTP/1.0” | “HTTP/1.1”
    <headers>::= <header>*
        <header>::= <key>": "<value>"\r\n"
            <key>::= case insensitive string
            <value>::= string
    <body>: string
```

#### HTTP/1.X Response Format
```
<response>::= <HTTP-version> <status>\r\n<headers>\r\n<body>
    <HTTP-version>::= “HTTP/1.0” | “HTTP/1.1”
    <status>::= “200 OK” | “404 Not Found” | “400 Bad Request”
    <headers>::= <header>*
        <header>::= <key>": "<value>"\r\n"
            <key>::= case insensitive string
            <value>::= string
    <body>::= string
```

#### HTTP/1.X End of Request or Response
- When sending a request or response, the request or response should contain the header Content-Length: <body_size> to inform the receiver where the end of request or response is located.
- In HTTP/1.0, the server can indicate the end of a response to the client by closing the connection.

------

## HTTP/2
- Each connection will be kept alive for a while.
- A connection can have multiple streams to handle multiple requests and responses simultaneously. Each stream is used to transfer a pair of request and response.
- Request and response are splitted into headers frame and data frames.
- The stream id of requests should be odd.
    - E.g., stream id = 1,3,5,7,9…

#### HTTP/2 Frame Format
![image](https://github.com/lon5948/Network-Systems-Capstone/blob/main/hw6/HTTP2_format.jpg)

#### HTTP/2 Frame Header
- Length is the payload size in bytes.
- Type:
    - 0: data frame
    - 1: headers frame
- Flags:
    - 0: default
    - 1: end of stream
- R is not used. Just set it to 0.

#### HTTP/2 Frame Payload
- HTTP headers and body are strings. In the payload, they are encoded in utf-8.
- Headers:
    - `<headers>::= <header>*`
    - `<header>::= <key>": "<value>"\r\n"`
    - `<key>::= case insensitive string`
    - `<value>::= string`
    - The key of header is case insensitive.
- Body may be divided into multiple data frames. At the receiver, you need a buffer to append the payload you received from the data frames of a stream.

#### Request and Response Pseudo Header
- Request pesudo header
```
:method: GET
:path: /
:scheme: http
:authority: 127.0.0.1:8080
```
- Response pesudo header
```
:status: 200
```

-------
## HTTP/3
- HTTP/3 uses QUIC as the transport-layer protocol instead of TCP.
- Unlike TCP, when a packet is lost in a stream of QUIC, it does not affect the reception of data in other streams.

#### HTTP/3 Frame Format
![image](https://github.com/lon5948/Network-Systems-Capstone/blob/main/hw6/HTTP3_format.jpg)

#### HTTP/3 Frame Header
- Length is the payload size in bytes.
- Type:
    - 0x00: data frame
    - 0x01: headers frame

#### HTTP/3 Frame Payload
- Headers and body are strings. In the payload, they are encoded in utf-8.
- Headers:
    - `<headers>::= <header>*`
    - `<header>::= <key>": "<value>"\r\n"`
    - `<key>::= case insensitive string`
    - `<value>::= string`
    - The key of header is case insensitive.
- Body may be divided into multiple data frames. At the receiver, you need a buffer to append the payload you received from the data frames of a stream.

#### Request and Response Pesudo Header
- Request pesudo header
```
:method: GET
:path: /
:authority: 127.0.0.1:8080
:scheme: http
```
- Response pesudo header
```
:status: 200
```
