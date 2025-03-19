import argparse
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Style

init(autoreset=True)  

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
   parser = argparse.ArgumentParser(description="A script to scan for admin panels and EAR vulnerabilities on the target website.")
   
   parser.add_argument("-t", "--target-url", 
                     help="The target URL to scan (e.g., http://example.com). This argument is required.", 
                     required=True)
   
   parser.add_argument("-p", "--path-prefix", 
                     help="A custom path prefix to append to the target URL for scanning (optional).",
                     default="")
   
   parser.add_argument("-f", "--file-type", 
                     help="The file types to scan (html, php, asp). Default is 'html'.", 
                     choices=["html", "php", "asp"], 
                     default="html")
   
   parser.add_argument("-m", "--multi-threading", 
                     help="Enable multi-threading to speed up the scan (optional).", 
                     action="store_true")
   
   parser.add_argument("-w", "--wordlist", 
                     help="Path to a custom wordlist file for scanning (optional). Default is 'admin_path.txt'.", 
                     default="admin_path.txt")
   
   parser.add_argument("-v", "--verbose", 
                     help="Enable verbose output to display detailed scan progress and results.", 
                     action="store_true")

   return parser.parse_args()

def normalize_target_url(url, prefix=""):
   if url.startswith("https://"):
      url = url.replace("https://", "").rstrip('/')
      protocol = "https://"
   elif url.startswith("http://"):
      url = url.replace("http://", "").rstrip('/')
      protocol = "http://"
   else:
      raise ValueError("The URL must start with 'http://' or 'https://'. Please include the protocol.")
   
   return f'{protocol}{url}{prefix}'

def check_robots(target):
   try:
      response = requests.get(f"{target}/robots.txt")
      if response.status_code == 200:
         print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} Robots.txt found. Check for interesting entries.")
         print(response.text)
      else:
         print(f"  {Fore.RED}[-]{Style.RESET_ALL} Robots.txt not found or inaccessible.")
   except requests.exceptions.RequestException:
      print(f"  {Fore.RED}[-]{Style.RESET_ALL} Failed to fetch robots.txt.")

def read_paths(wordlist_file, file_type):
   file_type_extensions = {
      "html": [".html", ".htm", ".xhtml", ".jsp", ".cgi", ".cfm", ".brf", ".brfbrf"],  
      "php": [".php", ".php3", ".php4", ".phtml", ".phps"],
      "asp": [".asp", ".aspx", ".cer", ".asa"],
      "js": [".js"],  
      "cgi": [".cgi"],
      "cfm": [".cfm"],
      "brf": [".brf"],
      "brfbrf": [".brfbrf"],
   }

   allowed_extensions = file_type_extensions.get(file_type, [])

   paths = set() 

   try:
      with open(wordlist_file, 'r') as file:
         for path in file:
               path = path.strip()
               
               if any(path.endswith(ext) for ext in allowed_extensions):
                  paths.add(path)

   except IOError:
      print(f"{Fore.RED}[-]{Style.RESET_ALL} Wordlist not found!")
      exit(1)

   return list(paths)

def scan_path(target, path):
   url = f"{target}/{path}"
   try:
      response = requests.get(url)
      if response.status_code == 200:
         print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} Admin panel found: {url}")
      elif response.status_code == 404:
         print(f"  {Fore.RED}[-]{Style.RESET_ALL} Not found: {url}")
      elif response.status_code == 302:
         print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} Potential EAR vulnerability found: {url}")
      else:
         print(f"  {Fore.RED}[-]{Style.RESET_ALL} Error {response.status_code}: {url}")
   except requests.exceptions.RequestException:
      print(f"  {Fore.RED}[-]{Style.RESET_ALL} Error with {url}")

def scan_with_threads(target, paths):
   with ThreadPoolExecutor(max_workers=10) as executor:
      executor.map(lambda path: scan_path(target, path), paths)

def scan_without_threads(target, paths):
   for path in paths:
      scan_path(target, path)

def main():
   print_banner()

   args = parse_args()

   # Change 'args.url' to 'args.target_url'
   target = normalize_target_url(args.target_url, args.path_prefix)
   
   check_robots(target)
   
   paths = read_paths(args.wordlist, args.file_type)
   
   if args.multi_threading:
      print(f"{Fore.BLUE}[+]{Style.RESET_ALL} Running in fast mode with multi-threading...")
      scan_with_threads(target, paths)
   else:
      print(f"{Fore.BLUE}[+]{Style.RESET_ALL} Running in normal mode without multi-threading...")
      scan_without_threads(target, paths)

if __name__ == "__main__":
   main()