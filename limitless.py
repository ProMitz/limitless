import random
import argparse
import requests
import time
import subprocess
from colorama import init, Fore, Style

init()

def random_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

def test_ip_headers(session, url, method, data, headers, ip_header):
    fake_ip = random_ip()
    test_headers = headers.copy()
    test_headers[ip_header] = fake_ip
    print(Fore.YELLOW + f"Testing {ip_header} with IP: {fake_ip}..." + Style.RESET_ALL)
    try:
        if method == "GET":
            response = session.get(url, headers=test_headers, timeout=10)
        elif method == "POST":
            response = session.post(url, json=data if isinstance(data, dict) else None,
                                    data=data if not isinstance(data, dict) else None,
                                    headers=test_headers, timeout=10)
        else:
            print(Fore.RED + "[!] Unsupported HTTP method." + Style.RESET_ALL)
            return

        if response.status_code == 429:
            print(Fore.RED + "Not Bypassed! (Rate limited)" + Style.RESET_ALL)
        else:
            print(Fore.GREEN + "Bypassed!" + Style.RESET_ALL)
        print(f"Status Code: {response.status_code}\n")
    except Exception as e:
        print(Fore.RED + f"[!] Request failed: {e}" + Style.RESET_ALL)

def parse_headers(header_list):
    headers = {}
    for header in header_list:
        if ':' in header:
            key, value = header.split(':', 1)
            headers[key.strip()] = value.strip()
        else:
            print(Fore.YELLOW + f"[!] Ignoring invalid header: {header}" + Style.RESET_ALL)
    return headers

def load_proxy_list(filename):
    proxies = []
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    proxies.append(line)
        print(Fore.GREEN + f"[*] Loaded {len(proxies)} proxies from {filename}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"[!] Failed to load proxy list: {e}" + Style.RESET_ALL)
    return proxies

def get_proxy_dict(proxy_str):
    proxy_url = f"http://{proxy_str}"
    return {
        "http": proxy_url,
        "https": proxy_url
    }

def restart_tor():
    print(Fore.YELLOW + "[*] Restarting Tor service for new IP..." + Style.RESET_ALL)
    subprocess.call(["sudo", "systemctl", "restart", "tor"])

def main():
    parser = argparse.ArgumentParser(description="Limitless - Rate-limit bypass tool")
    parser.add_argument("-u", required=True, help="Target URL")
    parser.add_argument("-m", default="GET", help="HTTP method (GET, POST, etc.)")
    parser.add_argument("-d", help="POST data like key=value&foo=bar")
    parser.add_argument("--json", help="JSON string data for POST")
    parser.add_argument("-c", action="store_true", help="Check rate-limit only")
    parser.add_argument("--loop", type=int, default=1, help="Number of requests to send")
    parser.add_argument("--header", action="append", default=[], help="Custom header(s), e.g. 'Key: Value'")
    parser.add_argument("--proxy-list", help="File with list of proxies (ip:port)")
    parser.add_argument("--delay", type=float, default=0, help="Delay seconds between requests")
    parser.add_argument("--tor", action="store_true", help="Use Tor and rotate IP on every request")
    parser.add_argument("--header-fake-ip-test", action="store_true",
                        help="Test IP-related headers for rate-limit bypass")
    parser.add_argument("-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    session = requests.Session()

    if args.tor:
        session.proxies = {
            "http": "socks5h://127.0.0.1:9050",
            "https": "socks5h://127.0.0.1:9050"
        }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    custom_headers = parse_headers(args.header)
    headers.update(custom_headers)

    method = args.m.upper()
    url = args.u

    data = None
    if args.json:
        import json
        try:
            data = json.loads(args.json)
            headers["Content-Type"] = "application/json"
        except Exception as e:
            print(Fore.RED + f"[!] JSON parse error: {e}" + Style.RESET_ALL)
            return
    elif args.d:
        data = {}
        for pair in args.d.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                data[k] = v

    if args.header_fake_ip_test:
        ip_headers_to_test = [
            "X-Forwarded-For",
            "X-Real-IP",
            "Client-IP",
            "X-Client-IP",
            "True-Client-IP"
        ]
        for ip_header in ip_headers_to_test:
            test_ip_headers(session, url, method, data, headers, ip_header)
        return

    loop_count = 10 if args.c else args.loop

    for i in range(loop_count):
        print(Fore.GREEN + f"[*] Sending request {i+1}/{loop_count}..." + Style.RESET_ALL)

        if i == 0 or args.v:
            print(Fore.GREEN + f"[*] URL: {url}" + Style.RESET_ALL)
            print(Fore.GREEN + f"[*] Method: {method}" + Style.RESET_ALL)
            if data:
                print(Fore.GREEN + f"[*] Data: {data}" + Style.RESET_ALL)

        if args.tor:
            restart_tor()
            time.sleep(2)

        try:
            if method == "GET":
                response = session.get(url, headers=headers, timeout=10)
            elif method == "POST":
                if args.json:
                    response = session.post(url, json=data, headers=headers, timeout=10)
                else:
                    response = session.post(url, data=data, headers=headers, timeout=10)
            else:
                print(Fore.RED + f"[!] Unsupported HTTP method: {method}" + Style.RESET_ALL)
                return

            print(Fore.CYAN + f"[+] Status Code: {response.status_code}" + Style.RESET_ALL)

            if args.v:
                print(Fore.GREEN + f"[*] Headers: {headers}" + Style.RESET_ALL)
                print(f"[+] Response headers: {response.headers}")
                print(f"[+] Response body:\n{response.text}")

        except Exception as e:
            print(Fore.RED + f"[!] Request failed: {e}" + Style.RESET_ALL)

        if args.delay > 0:
            time.sleep(args.delay)

if __name__ == "__main__":
    main()
