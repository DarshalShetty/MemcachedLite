# MemcachedLite (MCLite)

This repository hosts the code for a simple key-value store service for the 
Fall 2021 Engineering Cloud Computing course at Indiana University Bloomington.

## Things to note

- Memcached protocol states that keys can contain any characters other than 
  whitespace and control characters. However, MCLite also imposes the 
  restriction that keys can't contain the ```/``` character because of UNIX 
  filename restrictions.