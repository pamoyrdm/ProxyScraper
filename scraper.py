import requests
import concurrent.futures
import re
import sys
import time
import os

# Limpiar la consola
os.system('cls' if os.name == 'nt' else 'clear')

# Colores
red = "\033[1;31m"
green = "\033[1;32m"
yellow = "\033[1;33m"
blue = "\033[1;34m"
defcol = "\033[0m"

def error(msg):
    print(red + "[" + yellow + "!" + red + "] - " + defcol + msg)

def alert(msg):
    print(red + "[" + blue + "#" + red + "] - " + defcol + msg)

def action(msg):
    print(red + "[" + green + "+" + red + "] - " + defcol + msg)

def errorExit(msg):
    sys.exit(red + "[" + yellow + "!" + red + "] - " + defcol + "Fatal - " + msg)

def get_orders():
    if len(sys.argv) < 2:
        print("\033[1;33m╔═╗╦═╗╔═╗═╗ ╦╦ ╦  ╔═╗╔═╗╦═╗╔═╗╔═╗╔═╗╦═╗")
        print("\033[1;33m╠═╝╠╦╝║ ║╔╩╦╝╚╦╝  ╚═╗║  ╠╦╝╠═╣╠═╝║╣ ╠╦╝")
        print("\033[1;33m╩  ╩╚═╚═╝╩ ╚═ ╩   ╚═╝╚═╝╩╚═╩ ╩╩  ╚═╝╩╚═")
        errorExit("Usage: python scraper.py <output.txt> [-t threads] [-l yourlist] [-s sort]\nExamples:\n🌟Socks4\n- python2 scraper.py proxies_socks4.txt -t 50 -l socks4.txt\n🌟Socks5\n- python2 scraper.py proxies_socks5.txt -t 50 -l socks5.txt\n🌟HTTP\n- python2 scraper.py proxies_http.txt -t 50 -l http.txt")
    
    name = sys.argv[1]
    try:
        max_threads = int(sys.argv[sys.argv.index("-t") + 1])
    except (ValueError, IndexError):
        max_threads = 40
    try:
        leech_list = sys.argv[sys.argv.index("-l") + 1]
    except (ValueError, IndexError):
        leech_list = "sites.txt"
    b_sort = "-s" in sys.argv

    return [name, max_threads, leech_list, b_sort]

def scan_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        valid_proxies = re.findall(r'(?:[\d]{1,3}\.){3}[\d]{1,3}:[\d]{2,5}', response.text)
        action("%s proxies found on %s" % (len(valid_proxies), url))
        return valid_proxies, url
    except (requests.RequestException, IOError):
        return [], None

if __name__ == "__main__":
    sys.dont_write_bytecode = True  # Don't create .pyc

    orders = get_orders()
    try:
        proxy_list = open(orders[0], "a")
        sites = open(orders[2], "r")
        good_sites = open("good_sites.txt", "w")
    except IOError as e:
        errorExit("Error: %s" % e)

    with concurrent.futures.ThreadPoolExecutor(max_workers=orders[1]) as executor:
        futures = [executor.submit(scan_url, url.strip()) for url in sites]
        for future in concurrent.futures.as_completed(futures):
            valid_proxies, url = future.result()
            for proxy in valid_proxies:
                proxy_list.write(proxy + "\n")
            if url:
                good_sites.write(url + "\n")

    proxy_list.close()
    good_sites.close()

    try:
        with open(orders[0]) as f:
            total_proxies = sum(1 for _ in f)
            action("Scraped %s proxies." % total_proxies)
    except IOError:
        pass

    action("Done leeching.")
