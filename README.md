# ccp-ai

## Required

### Install python https://www.python.org/downloads/

- Should run on Linux or WSL(windows subsystem for linux)

## 1. How to start (Linux, macOS)

Initialize the virtual environment

```bash
python3 -m venv venv
```

Access to the virtual environment

```bash
source venv/bin/activate
```

Install initial packages

```bash
pip install -r ./pkg/requirements.txt
```

Pull and start infrastructure images

```bash
make up
```

Run service

```bash
make start
```

Stop all infrastructure images

```bash
make down
```

Exit the virtual environment

```bash
deactivate
```

## 2. How to start (Windows)

Initialize the virtual environment

```bash
python3 -m venv venv
```

Access to the virtual environment

```bash
venv\Scripts\activate.bat
```

Install initial packages

```bash
pip install -r ./pkg/requirements.txt
```

Pull and start infrastructure images

```bash
docker-compose -f ./builders/docker-compose.yml up -d
```

Run service

```bash
python3 main.py
```

Stop all infrastructure images

```bash
docker-compose -f ./builders/docker-compose.yml down
```

Exit the virtual environment

```bash
deactivate
```

## 3. Setup infras (for deploying)

Setup infras

```bash
make infras
```

Stop infras

```bash
make infras_down
```
