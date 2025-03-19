import argparse
import requests
import threading
import random
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Style
import os

init(autoreset=True)

print_lock = threading.Lock()
found_something = []

FAKE_USER_AGENTS = [
   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
   "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.80 Mobile Safari/537.36",
   "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
   "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
   "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
   "Mozilla/5.0 (iPhone; CPU iPhone OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Mobile/15E148 Safari/604.1"
]

def clear_screen():
   if os.name == 'nt':  
      os.system('cls')
   else:  
      os.system('clear')

def clear_screen():
   if os.name == 'nt':  
      os.system('cls')
   else:  
      os.system('clear')

def safe_print(message):
   with print_lock:
      print(message)

def print_line(char, times, color):
   print(f'{getattr(Fore, color.upper())}{char * times}{Style.RESET_ALL}')

def print_banner():
   ascii_art = """
      \t███████╗██╗███████╗ ██████╗ ███████╗██████╗ 
      \t██╔════╝██║██╔════╝██╔════╝ ██╔════╝██╔══██╗
      \t███████╗██║█████╗  ██║  ███╗█████╗  ██████╔╝
      \t╚════██║██║██╔══╝  ██║   ██║██╔══╝  ██╔══██╗
      \t███████║██║███████╗╚██████╔╝███████╗██║  ██║
      \t╚══════╝╚═╝╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
   """
   print(Fore.RED + ascii_art)
   print(f"\t\t\t\t{Fore.YELLOW}👻 Made by SieGer{Style.RESET_ALL}")
   print(f"\n\t{Fore.RED}!! I am not responsible for your actions. Use at your own risk.!!{Style.RESET_ALL}\n")
   print_line('-', 74, 'yellow')

def parse_args():
   parser = argparse.ArgumentParser(description="Scan for admin panels and EAR vulnerabilities.")

   parser.add_argument("-t", "--target-url", required=True,
                     help="Target URL to scan (e.g., http://example.com)")
   parser.add_argument("-p", "--path-prefix", default="",
                     help="Path prefix to append to the URL (optional)")
   parser.add_argument("-f", "--file-type", choices=["html", "php", "asp"], default="html",
                     help="File type for filtering paths")
   parser.add_argument("-m", "--multi-threading", action="store_true",
                     help="Enable multi-threaded scanning")
   parser.add_argument("-w", "--wordlist", default="admin_path.txt",
                     help="Custom wordlist file (default: admin_path.txt)")
   parser.add_argument("-v", "--verbose", action="store_true",
                     help="Enable verbose output")
   parser.add_argument("-o", "--output", help="Output file to save found results")
   parser.add_argument("--random-agent", action="store_true",
                     help="Use random User-Agent headers for each request")

   return parser.parse_args()

def save_results_to_file(results, filename):
   try:
      with open(filename, "w") as f:
         for result in results:
               f.write(result + "\n")
      safe_print(f"\n{Fore.CYAN}[✔]{Style.RESET_ALL} Results saved to {filename}")
   except Exception as e:
      safe_print(f"{Fore.RED}[x]{Style.RESET_ALL} Failed to save results: {e}")

def normalize_target_url(url, prefix=""):
   if url.startswith("https://"):
      protocol = "https://"
      url = url.replace("https://", "").rstrip('/')
   elif url.startswith("http://"):
      protocol = "http://"
      url = url.replace("http://", "").rstrip('/')
   else:
      raise ValueError("URL must start with 'http://' or 'https://'")
   return f"{protocol}{url}{prefix}"

def check_robots(target, use_random_agent):
   headers = {
      "User-Agent": random.choice(FAKE_USER_AGENTS) if use_random_agent else "Mozilla/5.0 (AdminScanner)"
   }
   try:
      response = requests.get(f"{target}/robots.txt", headers=headers, timeout=5)
      if response.status_code == 200:
         safe_print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} Robots.txt found. Check for interesting entries.")
         safe_print(response.text)
      else:
         safe_print(f"  {Fore.RED}[-]{Style.RESET_ALL} Robots.txt not found or inaccessible.")
   except requests.exceptions.RequestException:
      safe_print(f"  {Fore.RED}[-]{Style.RESET_ALL} Failed to fetch robots.txt.")

def read_paths(wordlist_file, file_type):
   extensions = {
      "html": [".html", ".htm", ".xhtml", ".jsp", ".cgi", ".cfm", ".brf", ".brfbrf"],
      "php": [".php", ".php3", ".php4", ".phtml", ".phps"],
      "asp": [".asp", ".aspx", ".cer", ".asa"]
   }

   allowed_exts = extensions.get(file_type, [])
   paths = set()

   try:
      with open(wordlist_file, 'r') as file:
         for path in file:
               path = path.strip()
               if any(path.endswith(ext) for ext in allowed_exts):
                  paths.add(path)
   except IOError:
      safe_print(f"{Fore.RED}[-]{Style.RESET_ALL} Wordlist not found!")
      exit(1)

   return list(paths)

def scan_path(target, path, verbose, use_random_agent):
   url = f"{target}/{path}"
   headers = {
      "User-Agent": random.choice(FAKE_USER_AGENTS) if use_random_agent else "Mozilla/5.0 (AdminScanner)"
   }
   try:
      response = requests.get(url, headers=headers, timeout=5)

      if response.status_code == 200:
         safe_print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} Admin panel found: {url}")
         found_something.append(url)
      elif response.status_code == 302:
         safe_print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} Potential EAR vulnerability found: {url}")
         found_something.append(url)
      elif verbose:
         if response.status_code == 404:
               safe_print(f"  {Fore.RED}[-]{Style.RESET_ALL} Not found: {url}")
         else:
               safe_print(f"  {Fore.YELLOW}[!]{Style.RESET_ALL} Status {response.status_code}: {url}")

   except requests.exceptions.RequestException:
      if verbose:
         safe_print(f"  {Fore.RED}[-]{Style.RESET_ALL} Error with {url}")

def scan_with_threads(target, paths, verbose, use_random_agent):
   with ThreadPoolExecutor(max_workers=10) as executor:
      executor.map(lambda path: scan_path(target, path, verbose, use_random_agent), paths)

def scan_without_threads(target, paths, verbose, use_random_agent):
   for path in paths:
      scan_path(target, path, verbose, use_random_agent)

def main():
   clear_screen()
   print_banner()
   args = parse_args()

   target = normalize_target_url(args.target_url, args.path_prefix)
   check_robots(target, args.random_agent)

   paths = read_paths(args.wordlist, args.file_type)

   if args.multi_threading:
      safe_print(f"{Fore.BLUE}[+]{Style.RESET_ALL} Running in fast mode with multi-threading...\n")
      scan_with_threads(target, paths, args.verbose, args.random_agent)
   else:
      safe_print(f"{Fore.BLUE}[+]{Style.RESET_ALL} Running in normal mode without multi-threading...\n")
      scan_without_threads(target, paths, args.verbose, args.random_agent)

   if not args.verbose and not found_something:
      print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} Nothing found.")
   elif found_something and args.output:
      save_results_to_file(found_something, args.output)

if __name__ == "__main__":
   try:
      main()
   except KeyboardInterrupt:
      print(f"\n{Fore.RED}[x] Interrupted by user. Exiting...{Style.RESET_ALL}")
      exit(0)