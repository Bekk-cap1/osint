# Hunter

**OSINT username checker** — Sherlock-style enumeration in **Go**: many sites, one `data/sites.json`, optional **web UI**, country filter, **email** / **phone** helpers.

| | |
|---|---|
| **Language** | English → [below](#english) |
| **Язык** | Русский → [ниже](#русский) |

**Stack:** Go **1.22+** · optional Python **3** (for `scripts/merge_whatsmyname.py`)

---

## English

### What it does

- Checks a username (and generated variants) against **hundreds/thousands** of site probes defined in **`data/sites.json`**.
- **CLI:** concurrent requests, progress on stderr, **Ctrl+C** cancels.
- **Web:** dashboard with search, **Stop**, table sort/filter, WebSocket progress.
- **Extras:** full-name variants; **email** → local part + **MD5** for Gravatar-style entries; **phone** digits for phone-specific probes.

### Requirements

| Tool | Notes |
|------|--------|
| Go | **1.22+** (`go version`) |
| Python | Optional · WMN merge script |

### Installation (from Git)

Fork maintainers: set `go.mod` to `module github.com/<you>/hunter` and replace imports `github.com/user/hunter` → your module path.

**Recommended (Linux / Kali):** use [`install.sh`](install.sh) — builds, installs to `~/.local/bin`, updates `.bashrc` / `.zshrc` for `PATH` when needed.

```bash
git clone https://github.com/<you>/hunter.git
cd hunter
chmod +x install.sh
./install.sh
# Kali default is zsh → use .zshrc (NOT .bashrc in zsh):
source ~/.zshrc
hunter -h
```

**Shell note:** On **Kali**, the default terminal is **zsh**. If you run `source ~/.bashrc` inside zsh, you get errors (`shopt: command not found`, `complete: command not found`). Use **`source ~/.zshrc`**, open a **new terminal**, or run **`export PATH="$HOME/.local/bin:$PATH"`** once.

**Manual build:**

```bash
go build -o hunter ./cmd/hunter
./hunter -h
```

**`data/sites.json`:** run scans from the repo folder or pass **` -sites /absolute/path/to/data/sites.json`**. CI: [`.github/workflows/go.yml`](.github/workflows/go.yml).

**Windows** (optional):

```powershell
go build -o hunter.exe ./cmd/hunter
```

### Kali Linux

| Step | Action |
|------|--------|
| 1 | If `apt install golang-go` is **old**, install Go from [go.dev/dl](https://go.dev/dl/) |
| 2 | `sudo apt update && sudo apt install -y git python3` |
| 3 | Clone repo → `chmod +x install.sh` → `./install.sh` |
| 4 | **`source ~/.zshrc`** on Kali (zsh). On pure bash systems: `source ~/.bashrc`. Or open a **new** terminal. |

**System-wide binary (no shell edits):**

```bash
./install.sh --system
```

**Do not use `sudo go build`.** Build as your user; use `sudo` only to copy the binary (e.g. `install.sh --system` or `sudo install -m 755 hunter /usr/local/bin/hunter`). Root breaks `~/go/pkg` permissions.

**Web UI:**

```bash
cd /path/to/hunter
hunter -web -port 8080
# http://127.0.0.1:8080
```

### CLI examples

| Example | Description |
|---------|-------------|
| `hunter alice` | Single username |
| `hunter u1 u2` | Several usernames |
| `hunter -u x -e a@b.c -p 79001234567` | Nick + email + phone |
| `hunter -n "First Last"` | Full-name variants |
| `hunter -e user@mail.com` | Email + Gravatar MD5 probes |
| `hunter -p 79991234567` | Phone-style probes |
| `hunter nick -country uz` | Country filter + `global` |
| `hunter -web -port 8080` | Web dashboard |

**Flags:** `-sites`, `-timeout`, `-workers`, `-v`, `-o`, `-csv`, `-version`, `-phone` / `-p`.

### Site database

Entries in **`data/sites.json`**: `url` with `{}` placeholder, `errorType`, optional `urlProbe`, `errorMsg`, `foundSubstring`, `notFoundHTTP`, `expectedHTTP`, POST fields, etc.

Refresh WhatsMyName merge:

```bash
python scripts/merge_whatsmyname.py
```

**WhatsMyName** data is **CC BY-SA 4.0** — keep attribution per their license.

### Project layout

```text
cmd/hunter/       main
internal/checker  HTTP checks
internal/generator
internal/models
internal/scheduler
internal/sites
internal/web      + embedded UI
data/sites.json
install.sh
scripts/
```

### Disclaimer

Use only where allowed. Respect laws and site policies.

---

## Русский

### Описание

Проверка ника по большой базе **`data/sites.json`** (Sherlock-подобные правила + слияние с **WhatsMyName**), **веб-интерфейс**, фильтр **страны**, генерация из **email** и **телефона**.

### Требования

| | |
|---|---|
| Go | **1.22+** |
| Python | По желанию (скрипты WMN) |

### Установка

Свой форк: в **`go.mod`** укажите `module github.com/<вы>/hunter`, замените импорты с `github.com/user/hunter`.

```bash
git clone https://github.com/<вы>/hunter.git
cd hunter
chmod +x install.sh
./install.sh
source ~/.zshrc    # Kali: zsh. Если работаете в bash: source ~/.bashrc
hunter -h
```

**Kali / zsh:** не выполняйте **`source ~/.bashrc`** в оболочке zsh — будут ошибки `shopt`, `complete`. Либо **`source ~/.zshrc`**, либо новый терминал, либо разово: **`export PATH="$HOME/.local/bin:$PATH"`**.

Вручную: `go build -o hunter ./cmd/hunter`. Работайте из каталога репозитория или задайте **`-sites`**.

**Windows:** `go build -o hunter.exe ./cmd/hunter`

### Kali Linux

Если Go из `apt` старый — [go.dev/dl](https://go.dev/dl/). Далее то же: **`./install.sh`** или **`./install.sh --system`**.

**Не используйте `sudo go build`** — собирайте от обычного пользователя, в системные каталоги копируйте уже готовый бинарник.

Веб: `cd …/hunter && hunter -web -port 8080`.

По умолчанию в Kali — **zsh**: после `./install.sh` выполняйте **`source ~/.zshrc`**, не **`source ~/.bashrc`** (иначе ошибки `shopt` / `complete`).

### Примеры команд

| Команда | Назначение |
|---------|------------|
| `hunter nick` | Один ник |
| `hunter u1 u2` | Несколько ников |
| `hunter -u x -e a@b -p 7900…` | Ник + email + телефон |
| `hunter -n "Иван Иванов"` | Варианты из ФИО |
| `hunter -e user@mail.com` | Email + MD5 (Gravatar) |
| `hunter -p 79991234567` | Телефон |
| `hunter nick -country uz` | Страна |
| `hunter -web -port 8080` | Веб-панель |

Флаги: **`-sites`**, **`-timeout`**, **`-workers`**, **`-v`**, **`-o`**, **`-csv`**, **`-p`** / **`-phone`**.

### База `data/sites.json`

Плейсхолдер ника — **`{}`**. Обновление WMN: `python scripts/merge_whatsmyname.py`. Лицензия WMN: **CC BY-SA 4.0**.

### Важно

Только законное и этичное использование.

---

*Замените в репозитории `github.com/user/hunter` на свой модуль, если публикуете форк.*
