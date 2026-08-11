# Sabeelullah Mohammed - Latest Resume

Senior SRE / DevOps Engineer | Kubernetes | Terraform | AWS/GCP/Azure | CI/CD | Observability | Linux | AWS Certified

- [View latest resume](resume.md)
- Location: Somerset, NJ
- Email: mohdsab1525@gmail.com
- LinkedIn: https://www.linkedin.com/in/k-mohammed-646892217

---

# Human-in-the-loop Job Pipeline

Cloud-ready automation for collecting Dice and LinkedIn job leads, deduplicating them, and presenting them for manual approval. It never submits an application automatically.

## What it does

- Runs on a schedule inside a Docker container.
- Collects job links from configured Dice and LinkedIn search pages.
- Stores unique jobs in SQLite and avoids duplicates by normalized URL.
- Shows a password-protected review dashboard.
- Lets you approve, reject, or mark a job as applied.
- Stops and records a blocker when login, CAPTCHA, or security verification appears.
- Includes a GitHub Actions CI/CD workflow for tests, container publishing, and optional SSH deployment.

## Quick start

1. Copy `.env.example` to `.env` and set strong secrets.
2. Put one search URL per line in `config/dice_urls.txt` and `config/linkedin_urls.txt`.
3. Run `docker compose up -d --build`.
4. Open `http://SERVER_IP:8080` and sign in.

Before cloud use, initialize authenticated browser sessions interactively:

```bash
docker compose run --rm app python -m app.auth dice
docker compose run --rm app python -m app.auth linkedin
```

Complete login yourself in the opened browser. Never commit the generated `data/auth/` files. If the provider requests a CAPTCHA or other verification during a scheduled run, the pipeline pauses that source.

## GitHub Actions deployment

The workflow runs tests, builds the image, and publishes it to GHCR. To enable deployment, configure these repository secrets:

- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_SSH_KEY`
- `DEPLOY_PATH` (directory on the server containing `docker-compose.yml` and `.env`)

The server needs Docker and the Compose plugin. The deploy job pulls the new image and restarts the service. Set `IMAGE` in the server `.env` to the GHCR image name printed by the build.

## Important limitations

Use this only in ways permitted by each site's terms and your account rules. LinkedIn and Dice can change markup at any time, so selectors may need maintenance. This project intentionally does not bypass CAPTCHAs, rate limits, login challenges, or site security.
