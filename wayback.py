import requests
import time
import argparse


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 13_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
]


def crawl_wayback(domain, retries=3):
    base_url = f"https://web.archive.org/web/timemap/json?url={domain}&matchType=prefix&collapse=urlkey&output=json&fl=original%2Cmimetype%2Ctimestamp%2Cendtimestamp%2Cgroupcount%2Cuniqcount&filter=!statuscode%3A%5B45%5D..&limit=10000"
    for attempt in range(retries):
        for user_agent in USER_AGENTS:
            headers = {'User-Agent': user_agent}
            try:
                response = requests.get(base_url, headers=headers)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"[-] Failed to crawl {domain}: Status code {response.status_code} with User-Agent: {user_agent}")
            except requests.exceptions.RequestException as e:
                print(f"[-] Error crawling {domain} with User-Agent {user_agent}: {str(e)}")

        if attempt < retries - 1:
            print(f"[!] Retrying... ({attempt + 1}/{retries})")
            time.sleep(5)  
        else:
            print(f"[-] Skipping {domain} due to repeated errors.")
    return None


def process_url(url):
    url = url.replace('https://', '').replace('http://', '').replace('www.', '')
    return url

def main(input_file, output_file):
    with open(input_file, 'r') as f:
        domains = [line.strip() for line in f.readlines()]

    with open(output_file, 'w') as out:
        for domain in domains:
            if not domain.startswith('http://') and not domain.startswith('https://'):
                domain = 'http://' + domain

            print(f"[+] Crawling {domain} | Processing...")

            data = crawl_wayback(domain)

            if data:
                print(f"[+] Crawling {domain} | Done!!, next domain.")
                for entry in data[1:]:
                    url = process_url(entry[0])
                    out.write(f"{url}\n")
            else:
                print(f"[-] Skipping {domain} due to no crawled data.")
                continue  
            
            time.sleep(15)  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl Wayback Machine for multiple domains.")
    parser.add_argument("-l", "--list", required=True, help="Path to the file containing the list of domains.")
    parser.add_argument("-o", "--output", required=True, help="Path to the output file.")
    
    args = parser.parse_args()

    main(args.list, args.output)
