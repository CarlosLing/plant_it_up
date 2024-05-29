
.PHONY: test_backend
test_backend:
	cd backend && poetry shell && cd ..
	docker compose start
	bash backend/scripts/test.sh
