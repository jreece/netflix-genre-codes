# Netflix Code Explorer — Python desktop app

A native desktop genre browser with search, filters, favorites, code copying, and direct Netflix links.

## Run on Windows (VS Code terminal / PowerShell)

1. Install Python 3.10+ from python.org (check **Add Python to PATH**).
2. Extract this ZIP and open the extracted folder in VS Code.
3. Open **Terminal → New Terminal** and run:

```powershell
py -m pip install -r requirements.txt
py main.py
```

If `py` is unavailable, use `python` instead.

## Optional: build a Windows executable

On Windows, run:

```powershell
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --onefile --windowed --name NetflixCodeExplorer --add-data "netflix_codes.json;." main.py
```

Find the executable in `dist/NetflixCodeExplorer.exe`. Build on Windows for a Windows `.exe`.

## Data and favorites

- `netflix_codes.json` contains the 115 starter categories from the earlier HTML app based on the Cloudwards guide; it is editable.
- Favorites are stored in `%USERPROFILE%\.netflix_code_explorer\favorites.json`.
- No Netflix account details are collected. Clicking Open launches your default browser; availability varies by region.
- Independent project; not affiliated with Netflix or Cloudwards.
