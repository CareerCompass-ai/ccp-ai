# ccp-ai

## Required

- Should run on Linux or WSL(windows subsystem for linux)

## How to start

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
pip install -r requirements.txt
```

Start container

```bash
docker-compose -f ./builders/docker-compose.yml up -d
```

Run service

```bash
python3 main.py
```

Remove container

```bash
docker-compose -f ./builders/docker-compose.yml down
```

Exit the virtual environment

```bash
deactivate
```
