# MemcachedLite (MCLite)

This repository hosts the code for a simple key-value store service for the 
Fall 2021 Engineering Cloud Computing course at Indiana University Bloomington.

## Design Details

### The Server
The server is implemented using Python's ```socketserver``` library. This 
library uses the select() OS call and therefore can handle client 
disconnections gracefully. The server tries to follow the [memcached protocol](https://github.com/memcached/memcached/blob/master/doc/protocol.txt) 
as closely as possible. The socket server that is being used uses forking to achieve concurrency. 
Because of Python's global interpreter lock, I decided to go a multiprocess 
approach rather than a multithreading approach. This server can be started 
by running the script called ```server.py```. This server can be configured 
using the file ```server_config.py```. The server parses buffered binary 
data using a parser modules ```command_parser.py``` and ```response_parser. py```.

### The clients

```client_sdk.py``` is the module responsible for communicating with the server.
This SDK has two versions of get and set commands. One version treats 
stored values as a binary stream and uses the same parser modules as the 
server to structure the protocol data. The other version simplifies the 
protocol by treating both keys and values as simple strings. This SDK is 
written such that using Python's context managers, the users need not worry 
much about handling the connection to the server. This SDK handles closing 
the socket connection even when the client process recieves a SIGINT or 
SIGTERM interrupt.

A more user-friendly client can be used by running ```client_cli.py``` which 
provides a CLI REPL for the user to interact with the server. This client 
only deals with keys and values as strings using the API provided by the 
client SDK mentioned above. 

Another small test program called ```tests/test_basic_requirements.py``` 
also uses this client SDK to perform some simple tests on the server. 
Similar test scripts can be added to the ```tests/``` directory to test how 
close the server follows the memcached protocol as well as to do some 
benchmarking.

### The storage

The underlying storage system is rather simple. Every key is a file that can 
be found in the storage directory which is configurable using the server 
config file. The contents of a file contain the value stored with a key. All 
of this is implemented in the file ```storage.py```. This file also includes 
an abstract base class which can be used to later on implement an in-memory 
storage.

## Memcached compatibility (bonus)

Unfortunately this repository doesn't implement full memcached compatibility.
Only thing that is lacking is accommodating flags and CAS values. Although 
this too could be easily implemented by tweaking the parser modules. 

## ```startup.sh```

This file can be run to see a demo of what MemcachedLite has implemented yet.
It runs the server in the background, runs a few tests and then starts a 
client REPL for the user to interact with the server.

## Things to note

- Memcached protocol states that keys can contain any characters other than 
  whitespace and control characters. However, MCLite also imposes the 
  restriction that keys can't contain the ```/``` character because of UNIX 
  filename restrictions.
- The memcached protocol mentions that unstructured data is just a byte 
  stream. However, it doesn't specify an encoding for text lines. This 
  repository assumes utf-8 encoding of text lines. Although the pymemcache 
  client only supports the ASCII protocol of memcached, since utf-8 is a 
  superset of ASCII, the MCLite server should not have trouble communicating 
  with this client.
- Client-server handling of unexpected closed sockets could be improved in 
  the client SDK. Probably using selectors library which implements select() and
  epoll() OS calls.
- readline() calls should be replaced by a function that treats <CR><LF> 
  (\r\n) as line separators rather than just <LF> (\n)
- non-printable characters not being checked in regex for keys.
- max key and value length checks are only being done in command parser 
  because that's where clients might send wrong data. Response parsing 
  doesn't handle this check because we are assuming that we are storing 
  sanitized data with our validated storage commands. However, this 
  assumption falls apart if somehow the data is stored in our underlying 
  store not through the server but through compromised filesystem access.
- File handlers can be cached to prevent the overhead of creating them
- A file locking mechanism should be implemented to improve consistency 
  during concurrent access to the same file handler
