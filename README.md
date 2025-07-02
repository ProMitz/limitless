# Limitless - Rate-limit Bypass Tool

**Limitless** is a Python tool designed to bypass server rate-limits using techniques like:

- IP spoofing headers (`X-Forwarded-For`, etc.)
- TOR IP rotation
- Delay between requests
- Proxy list support
- Verbose
 
## Features

- `--tor` for automatic TOR IP change on every request
- `--header-fake-ip-test` to test spoofed IP headers
- `--loop` to send multiple requests
- `--delay` to slow down requests
- `--proxy-list` for rotating HTTP proxies
- `--json` to send json data
- `header` too add custom headers
- `--header-fake-ip-test` to try various headers to evade rate-limit
- `-c` to send requests 10 times to check if rate-limit is present
- `-d` to send data
- `-u` to specify an URL
- `-m` to define a method

- (You may need tor installed and running if using --tor)

## Usages 
`python3 limitless.py -u "https://example.com" -m POST -d "username=admin&password=admin" --loop 10 --delay 1 --tor`
Or test spoofed headers:
`python3 limitless.py -u "https://example.com" --header-fake-ip-test`

## Legal Disclaimer
This tool is intended for educational and authorized testing only. Use it on systems you own or are permitted to test.

## Author
Taiki - ethical hacking student and developer 
