# Hunter — OSINT username checker

[English](#english) · [Русский](#русский)

---

## English

A **Sherlock-style** username enumeration tool in **Go**: probe many sites from a single `sites.json` database (merged Sherlock-like entries plus **WhatsMyName** data), optional **web dashboard**, filters by country, and generators for **email** (including Gravatar MD5) and **phone** digits.

### Features

- **Large site list** — one JSON map of probe URLs and rules (`data/sites.json`).
- **CLI** — concurrent checks, progress on stderr, `-sites` for a custom DB, Ctrl+C cancels.
- **Web UI** — search by username, full name, email, phone; **Stop**, table **sort** and **filter**; live progress over WebSocket.
- **Generators** — full-name variants; email local-part variants + **MD5 for `Gravatar_*`** entries; normalized **phone** variants for **`Phone_*`** (e.g. WhatsApp-style URLs in the DB).
- **Country filter** — sites tagged with `countries` (`global`, `uz`, `ru`, etc.).
- **Merge script** — `scripts/merge_whatsmyname.py` pulls [WhatsMyName](https://github.com/WebBreacher/WhatsMyName) `wmn-data.json` (see license below).

### Requirements

- **Go 1.22+**
- **Python 3** (optional, only for regenerating / merging `sites.json`)

### Install from GitHub (`git clone` only)

If you maintain a fork, set `go.mod` to `module github.com/<you>/hunter` and update imports from the placeholder `github.com/user/hunter` to match.

```bash
git clone https://github.com/<you>/hunter.git
cd hunter
go build -o hunter ./cmd/hunter
./hunter -h
```

Keep the repo directory: **`data/sites.json`** is loaded from there (or use `-sites` with another path).  
Optional CI: [`.github/workflows/go.yml`](.github/workflows/go.yml) runs `go build` on push to `main` / `master`.

**Windows** (native binary, not used on Linux/Kali):

```powershell
go build -o hunter.exe ./cmd/hunter
```

### Kali Linux

Same flow: **clone, then build a Linux binary** (`hunter`, not `.exe`). You need **Go 1.22+** — check `go version`; if `apt install golang-go` is too old, use a toolchain from [go.dev/dl](https://go.dev/dl/).

```bash
sudo apt update
sudo apt install -y git python3   # python3 optional (merge_whatsmyname.py)
# install Go 1.22+ if needed (see go.dev/dl)
git clone https://github.com/<you>/hunter.git
cd hunter
go build -o hunter ./cmd/hunter
./hunter -h
```

Install on `PATH` (optional):

```bash
sudo install -m 755 hunter /usr/local/bin/hunter
```

Web UI:

```bash
./hunter -web -port 8080
# http://127.0.0.1:8080
```

### CLI usage

```text
hunter <username>                   Search by username
hunter u1 u2                        Multiple usernames
hunter -u x -e user@mail.com -p 79001234567   Combine nick, email, phone
hunter -n "First Last"             Variants from full name
hunter -e user@mail.com             Email → local part + Gravatar MD5
hunter -p 79991234567               Phone digits (Phone_* sites in DB)
hunter nick -country uz             Country filter (+ global)
hunter -web -port 8080             Web dashboard
```

Useful flags: `-sites path` (custom JSON), `-timeout`, `-workers`, `-v`, `-o out.json`, `-csv`, `-version`.

### Web dashboard

```bash
hunter -web -port 8080
```

Open `http://localhost:8080`. The UI loads site count from `/api/sites`.

### Site database (`data/sites.json`)

- Object keys are site names; values define `url` (use `{}` as username placeholder), `errorType` (`status_code`, `message`, `response_url`), optional `urlProbe`, `errorMsg`, `foundSubstring`, `notFoundHTTP`, `expectedHTTP`, `headers`, `request_payload` / `requestBody`, etc.
- To **refresh WhatsMyName-derived entries**:

  ```bash
  python scripts/merge_whatsmyname.py
  ```

  The script merges into `data/sites.json` with keys prefixed `WMN_`. **WhatsMyName data** is licensed under **CC BY-SA 4.0** — keep attribution as required by that project (see `wmn-data.json` license block).

### Project layout (short)

```text
cmd/hunter/          CLI entrypoint
internal/checker/    HTTP probes + parsers (e.g. Instagram, Telegram)
internal/generator/  Username / email / phone variants
internal/models/     Shared types
internal/scheduler/  Worker pool + cancellable runs
internal/sites/      Load & filter sites.json
internal/web/        HTTP + WebSocket server, embedded static UI
data/sites.json      Site definitions
scripts/             merge_whatsmyname.py, rebuild helpers
```

### Disclaimer

Use only on targets you are allowed to test. This tool automates **public** footprint checks; comply with local laws and site terms.

---

## Русский

**Hunter** — утилита на **Go** в духе **Sherlock**: массовая проверка никнейма по базе сайтов в **`sites.json`** (в том числе после слияния с **WhatsMyName**), опционально **веб-панель**, фильтр по **стране**, генерация вариантов из **email** (в т.ч. MD5 для Gravatar) и **телефона** (цифры).

### Возможности

- **Большая база** — один JSON с шаблонами URL и правилами «найден / не найден».
- **CLI** — параллельные запросы, прогресс в stderr, свой путь к базе **`-sites`**, остановка по **Ctrl+C**.
- **Веб** — поля ник, ФИО, email, телефон; кнопка **Stop**, **сортировка** и **фильтр** таблицы, прогресс по WebSocket.
- **Генераторы** — варианты из ФИО; из email (локальная часть + **MD5 для записей `Gravatar_*`**); нормализация **телефона** для записей **`Phone_*`**.
- **Фильтр страны** — теги `countries` в каждой записи (`global`, `uz`, …).
- **Скрипт слияния** — `scripts/merge_whatsmyname.py` подтягивает актуальный **`wmn-data.json`** из репозитория WhatsMyName.

### Требования

- **Go 1.22+**
- **Python 3** (по желанию — для обновления `sites.json`)

### Установка: только `git clone`

Если свой форк — пропишите в `go.mod` путь `module github.com/<вы>/hunter` и замените импорты с плейсхолдера `github.com/user/hunter`.

```bash
git clone https://github.com/<вы>/hunter.git
cd hunter
go build -o hunter ./cmd/hunter
./hunter -h
```

Работайте из каталога репозитория, чтобы находился **`data/sites.json`** (или укажите **`-sites`**). CI: [`.github/workflows/go.yml`](.github/workflows/go.yml).

**Windows** — отдельно, бинарник `hunter.exe` (на Kali/Linux не нужен):

```powershell
go build -o hunter.exe ./cmd/hunter
```

### Kali Linux

На Kali собирается обычный **`hunter`** (Linux), не `.exe`. Нужен **Go 1.22+** (`go version`); при старом `golang-go` из apt — ставьте Go с [go.dev/dl](https://go.dev/dl/).

```bash
sudo apt update
sudo apt install -y git python3
git clone https://github.com/<вы>/hunter.git
cd hunter
go build -o hunter ./cmd/hunter
./hunter -h
```

В `PATH`, опционально: `sudo install -m 755 hunter /usr/local/bin/hunter`. Веб: `./hunter -web -port 8080` → `http://127.0.0.1:8080`.

### Примеры CLI

```text
hunter nick                         Только ник
hunter u1 u2                        Несколько ников
hunter -u x -e a@b.c -p 79001234567  Нормальное сочетание флагов
hunter -n "Иван Иванов"             Варианты из ФИО
hunter -e user@mail.com             Email + MD5 под Gravatar
hunter -p 79991234567             Телефон (цифры; смотри Phone_* в базе)
hunter nick -country uz            Страна + global
hunter -web -port 8080            Веб-интерфейс
```

Полезные флаги: **`-sites`**, **`-timeout`**, **`-workers`**, **`-v`**, **`-o`**, **`-csv`**, **`-version`**. Короткий алиас телефона: **`-p`** (= **`-phone`**).

### Веб-панель

```bash
hunter -web -port 8080
```

В браузере: `http://localhost:8080`.

### База `data/sites.json`

- В **`url`** плейсхолдер ника — **`{}`**. Типы ошибок: **`status_code`**, **`message`**, **`response_url`**; для стиля WhatsMyName — **`foundSubstring`**, **`notFoundHTTP`**, **`expectedHTTP`**, **`errorMsg`**, POST через **`request_payload`** или **`request_body`**.
- Обновить блоки WMN:

  ```bash
  python scripts/merge_whatsmyname.py
  ```

Ключи WMN имеют префикс **`WMN_`**. Данные WhatsMyName распространяются по **CC BY-SA 4.0** — сохраняйте атрибуцию согласно их лицензии (см. файл `wmn-data.json`).

### Важно

Используйте только в законных и этичных сценариях (свои аккаунты, явное разрешение, рамки политики сайтов и закона).

---

*Для работы через GitHub замените в проекте модуль и импорты с плейсхолдера `github.com/user/hunter` на свой `github.com/<вы>/hunter`.*
#   o s i n t  
 