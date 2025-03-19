# **Admin Pabel Scanner (admin_finder)**

> A fast and customizable tool to find **admin panels** and detect potential **EAR (Execution After Redirect)** vulnerabilities on websites using a wordlist-based path scanner. 

> Bonus: Includes C++ utilities for file preparation (`count_extensions.cpp`, `remove_duplicates.cpp`).

---
## **🧠 What This Tool Does**

- Scans a target website for common admin panel paths.
- Supports multiple file types: `.php`, `.asp`, `.html`, etc.
- Can detect suspicious 302 redirects (possible EAR).
- Supports multi-threading for faster scans.
- Optionally uses **fake User-Agent headers** to avoid detection.
- Supports custom wordlists.

---
## **🛠 Usage**

### 📥 Run the tool:

```bash
python3 admin_panel_finder.py -t http://example.com
```
### 💡 With more options:

```Bash
python3 admin_panel_finder.py -t http://target.com \
                              -f php \
                              -w custom_wordlist.txt \
                              -m \
                              -v \
                              --random-agent \
                              -o results.txt
```
### ⚙ Options Explained

|Option|Description|
|---|---|
|`-t`, `--target-url`|**(Required)** The target URL (e.g., `http://example.com`)|
|`-f`, `--file-type`|Choose extension filter: `html`, `php`, or `asp` (default: `html`)|
|`-p`, `--path-prefix`|Optional path prefix to append to the base URL|
|`-w`, `--wordlist`|Custom wordlist file (default: `admin_path.txt`)|
|`-m`, `--multi-threading`|Enable multi-threaded scanning for speed|
|`-v`, `--verbose`|Print full output including 404/other status codes|
|`--random-agent`|Use a **random User-Agent** header per request|
|`-o`, `--output`|Save the found results to a file|

---
## **🔍 Custom Wordlists**

You can use your own wordlist instead of the default one.  
Make sure the paths match the selected file type. For example:

```TXT
admin.php
dashboard.php
login.html
cpanel.asp
```

to use it: 

```Bash
python3 admin_panel_finder.py -t http://yourtarget.com -w my_list.txt -f php
```

---
## **🧩 Bonus Files**

### 📄 `count_extensions.cpp`

A C++ script that **counts occurrences of file extensions** in a wordlist.  
Use this to analyze your wordlist before scanning.

```Bash
g++ count_extensions.cpp -o count_ext
./count_ext admin_path.txt
```

### 📄 `remove_duplicates.cpp`

Removes **duplicate lines** from a given file (e.g., a large wordlist) to make scanning faster and cleaner.

```Bash
g++ remove_duplicates.cpp -o dedup
./dedup admin_path.txt cleaned.txt
```

---
## ⚠️ Disclaimer

This tool is intended for **educational purposes only**. 
The author is **not responsible** for any misuse or illegal activities performed using this script.  
Always have **proper authorization** before scanning any website.

---
## **✨ Credits**

👻 Made by **SieGer**  
Feel free to fork, customize, and contribute!