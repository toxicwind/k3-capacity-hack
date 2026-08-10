# k3-capacity-hack

Private internal capacity analysis and provider integration toolkit.

## Structure
- `src/` — Core modules
- `providers/` — External service integrations (Shodan, GitHub, SAM, etc.)
- `dashboard/` — Live monitoring dashboard
- `.github/workflows/` — CI/CD automation

## Providers
| Provider | Status | Credits | Strategy |
|----------|--------|---------|----------|
| Shodan | Active | 6/100 | count() validation + facet scraping |
| GitHub API | Active | Free tier | Search + raw code |
| USASpending | Active | Free | POST API |
| SAM.gov | Dead | N/A | API down, CDP fallback |
| Grants.gov | Blocked | N/A | Geo-blocked |
| Exa | Unknown | Unknown | Fallback search |

## Live Endpoints
- Kernel: http://127.0.0.1:8888
- VNC: http://127.0.0.1:6080
- CDP: http://127.0.0.1:9223
- K3 Proxy: http://127.0.0.1:19999
