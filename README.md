# waka-readme

GitHub Action que atualiza automaticamente o seu README de perfil com estatísticas do [WakaTime](https://wakatime.com) + GitHub.

> Versão própria, mais limpa e sem os bugs do projeto original.

---

## O que aparece no seu README

| Seção | Flag | Padrão |
|---|---|---|
| ⏱ Badge: tempo total de código | `SHOW_TOTAL_CODE_TIME` | `true` |
| 🐤/🦉 Distribuição por hora do dia | `SHOW_COMMIT` | `true` |
| 📅 Distribuição por dia da semana | `SHOW_DAYS_OF_WEEK` | `true` |
| 📊 Linguagens / Editores / Projetos / OS | `SHOW_LANGUAGE`, `SHOW_EDITORS`, etc. | `true` |
| 🗂 Linguagem por repositório | `SHOW_LANGUAGE_PER_REPO` | `true` |
| 🐱 Resumo do perfil GitHub | `SHOW_SHORT_INFO` | `true` |
| 🗓 Data de atualização | `SHOW_UPDATED_DATE` | `true` |

---

## Setup

### 1. Adicione os comentários no seu README.md de perfil

```md
<!--START_SECTION:waka-->
<!--END_SECTION:waka-->
```

### 2. Configure os Secrets no repositório de perfil

Vá em **Settings → Secrets and variables → Actions** e adicione:

| Secret | Valor |
|---|---|
| `WAKATIME_API_KEY` | Sua [WakaTime API Key](https://wakatime.com/settings/account) |
| `GH_TOKEN` | Personal Access Token com scopes `repo` + `user` |

### 3. Crie o workflow

Crie `.github/workflows/waka-readme.yml` no seu repositório de perfil (`<usuario>/<usuario>`):

```yaml
name: Update README Stats

on:
  schedule:
    - cron: '30 0 * * *'
  workflow_dispatch:

jobs:
  update-readme:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: SEU_USUARIO/waka-readme@main
        with:
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
          WAKATIME_API_KEY: ${{ secrets.WAKATIME_API_KEY }}
```

### 4. Rode manualmente

Vá em **Actions → Update README Stats → Run workflow** para testar.

---

## Flags disponíveis

```yaml
- uses: SEU_USUARIO/waka-readme@main
  with:
    GH_TOKEN: ${{ secrets.GH_TOKEN }}
    WAKATIME_API_KEY: ${{ secrets.WAKATIME_API_KEY }}

    SECTION_NAME: 'waka'           # nome da seção no README
    SHOW_COMMIT: 'true'            # commits por hora do dia
    SHOW_DAYS_OF_WEEK: 'true'      # commits por dia da semana
    SHOW_LANGUAGE: 'true'          # linguagens (WakaTime)
    SHOW_EDITORS: 'true'           # editores (WakaTime)
    SHOW_PROJECTS: 'true'          # projetos (WakaTime)
    SHOW_OS: 'true'                # OS (WakaTime)
    SHOW_TIMEZONE: 'true'          # timezone
    SHOW_LANGUAGE_PER_REPO: 'true' # linguagem por repo (GitHub)
    SHOW_TOTAL_CODE_TIME: 'true'   # badge tempo total
    SHOW_LINES_OF_CODE: 'false'    # badge linhas de código
    SHOW_LOC_CHART: 'true'         # gráfico de LOC por ano
    SHOW_SHORT_INFO: 'true'        # info do perfil GitHub
    SHOW_UPDATED_DATE: 'true'      # data de atualização
    SHOW_PROFILE_VIEWS: 'true'     # views do perfil

    SYMBOL_VERSION: '1'            # 1=█░  2=⣿⣀  3=⬛⬜
    BADGE_STYLE: 'flat'            # flat, flat-square, plastic, for-the-badge
    MAX_REPOS: '0'                 # 0 = sem limite
    IGNORED_REPOS: 'repo1,repo2'   # repos a ignorar
    COMMIT_MESSAGE: 'chore: update README metrics'
    DEBUG_RUN: 'false'             # true = só imprime, não commita
```

---

## Exemplo de saída

```text
🐤 Morning person

🌞 Morning    1435 commits   ████████░░░░░░░░░░░░░░░░░  35.2%
🌆 Daytime    1120 commits   ██████░░░░░░░░░░░░░░░░░░░  27.5%
🌃 Evening     980 commits   █████░░░░░░░░░░░░░░░░░░░░  24.0%
🌙 Night       537 commits   ███░░░░░░░░░░░░░░░░░░░░░░  13.2%

📊 This Week I Spent My Time On

💬 Languages:
Python                         8 hrs 22 mins       ████████████░░░░░░░░░░░░░  48.2%
TypeScript                     4 hrs 10 mins       ██████░░░░░░░░░░░░░░░░░░░  24.0%
...
```

---

## Desenvolvimento local

```bash
# Instale as deps
pip install -r requirements.txt

# Configure as variáveis
export GH_TOKEN=ghp_xxx
export WAKATIME_API_KEY=xxx
export INPUT_DEBUG_RUN=true   # não faz commit, só imprime

# Rode
python main.py
```

---

## Licença

MIT
