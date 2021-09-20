# MemcachedLite (MCLite)

This repository hosts the code for a simple key-value store service for the 
Fall 2021 Engineering Cloud Computing course at Indiana University Bloomington.

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
- Client-server handling of unexpected closed sockets should be improved. 
  Probably using selectors library which implements select() and epoll() OS 
  calls.
- readline() calls should be replaced by a function that treats <CR><LF> 
  (\r\n) as line separators rather than just <LF> (\n)
- non-printable characters not being checked in regex for keys.
- max key and value length checks are only being done in command parser 
  because that's where clients might send wrong data. Response parsing 
  doesn't handle this check because we are assuming that we are storing 
  sanitized data with our validated storage commands. However, this 
  assumption falls apart if somehow the data is stored in our underlying 
  store not through the server but through compromised filesystem access.
