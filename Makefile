.PHONY: help run migrate makemigrations createsuperuser shell test lint install 

createsuperuser:
	uv run manage.py createsuperuser

help:
	@echo "Команды make:"
	@echo "  make createsuperuser    - Создать суперпользователя"
	@echo "  make install            - Установить зависимости"
	@echo "  make lint               - Запустить линтер (flake8)"
	@echo "  make makemigrations     - Создать миграции"
	@echo "  make migrate            - Применить миграции"
	@echo "  make run                - Запустить Django сервер"
	@echo "  make shell              - Открыть Django shell"
	@echo "  make test               - Запустить тесты"

install:
	uv sync

lint:
	uv run flake8

makemigrations:
	uv run manage.py makemigrations

migrate:
	uv run manage.py migrate

run:
	uv run manage.py runserver

shell:
	uv run manage.py shell

test:
	uv run manage.py test






