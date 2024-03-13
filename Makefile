start:
	@./scripts/bin.sh start
.PHONY: start

up:
	@./scripts/bin.sh up
.PHONY: up

down:
	@./scripts/bin.sh down
.PHONY: down

infras:
	@./scripts/bin.sh infras
.PHONY: infras

	
infras_down:
	@./scripts/bin.sh infras_down
.PHONY: infras_down