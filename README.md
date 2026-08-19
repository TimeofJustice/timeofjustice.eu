![Title of the project](.github/images/title.png)

[![Last Commit](https://badgen.net/github/last-commit/timeofjustice/timeofjustice.eu)](https://timeofjustice.eu)
[![Visit](https://badgen.net/badge/visit%20now/timeofjustice.eu/blue)](https://timeofjustice.eu)

**timeofjustice.eu** began as a portfolio project to showcase my past and current work.
Since then, it has evolved into a playground for experimenting with new technologies and frameworks.
It's not about being perfect, but about having fun and learning new things.
The frontend is built with Vue.js, TypeScript, and Tailwind CSS.
The backend is powered by Django and a PostgreSQL database.

![Features of the project](.github/images/features.png)

- **Portfolio**: A showcase of my work and projects.
- **Games**: A collection of mini-games.
- **r/Place**: A recreation of Reddit’s _r/place_ event.

## Development

### Setup

```bash
npm install                                  # Lefthook + git hooks (via the prepare script)
npm --prefix frontend install
pip install -r backend/requirements.txt      # includes ruff
```

`ruff` has to be on your `PATH`, otherwise the backend hooks will fail.

### Formatting & linting

| Command                | Effect                                        |
| ---------------------- | --------------------------------------------- |
| `npm run format`       | Prettier (frontend) + `ruff format` (backend) |
| `npm run format:check` | the same, check only - this is what CI runs   |
| `npm run lint`         | ESLint (frontend) + `ruff check` (backend)    |
| `npm run lint:fix`     | the same with `--fix`                         |

On commit, Lefthook runs the matching steps automatically, each one only on the
staged files. The configuration lives in `frontend/eslint.config.ts`,
`frontend/.prettierrc` and `backend/ruff.toml`.
