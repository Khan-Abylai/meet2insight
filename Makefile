build_api_claude:
	docker build -t doc.aivy.kz/api_claude:app api_claude/

build_bot:
	docker build -t doc.aivy.kz/telegram_bot:app telegram/

build_all:
	make build_api_claude
	make build_bot

run:
	docker compose up -d --build

stop:
	docker compose down

restart:
	make stop
	make run

build_and_run:
	make build_all
	make run
