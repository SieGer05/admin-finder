import argparse
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Style
import os

init(autoreset=True)

print_lock = threading.Lock()

found_something = []

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

def check_robots(target):
   try:
      response = requests.get(f"{target}/robots.txt")
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

def scan_path(target, path, verbose):
   url = f"{target}/{path}"
   try:
      response = requests.get(url)

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

def scan_with_threads(target, paths, verbose):
   with ThreadPoolExecutor(max_workers=10) as executor:
      executor.map(lambda path: scan_path(target, path, verbose), paths)

def scan_without_threads(target, paths, verbose):
   for path in paths:
      scan_path(target, path, verbose)

def main():
   print_banner()
   args = parse_args()

   target = normalize_target_url(args.target_url, args.path_prefix)
   check_robots(target)

   paths = read_paths(args.wordlist, args.file_type)

   if args.multi_threading:
      safe_print(f"{Fore.BLUE}[+]{Style.RESET_ALL} Running in fast mode with multi-threading...\n")
      scan_with_threads(target, paths, args.verbose)
   else:
      safe_print(f"{Fore.BLUE}[+]{Style.RESET_ALL} Running in normal mode without multi-threading...\n")
      scan_without_threads(target, paths, args.verbose)

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