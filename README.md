### Description

ShortLink is a URL shortening service where you enter a URL and it returns a short URL such as http://short.est/XeUP94.

The service is built using Python and Flask and also using Test Driven Development (TDD)

### Notes

  -   Two endpoints are present
      -   /encode - Encodes a URL to a shortened URL
      -   /decode - Decodes a shortened URL to its original URL.
  -   Both endpoints return JSON
  - Uses base 62 mapping of unqiue number to avoid clashes with hashing and simultaneous requests
  - URLs persisted only in memory
  -   API tests for both endpoints available

