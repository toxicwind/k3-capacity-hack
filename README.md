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


## Push Workflow

```bash
cd /mnt/agents/output/k3-capacity-hack

# With PAT as argument
python3 push_harness.py <your_<PAT_PLACEHOLDER>>

# With PAT from env
<PAT_ENV>=<pat> python3 push_harness.py

# If upstream has changes (merge without clobber)
python3 merge_resolver.py
```

### Upstream Drift Handling
- `push_harness.py` detects if origin/main has diverged
- If local is ancestor: merges upstream into local, then pushes
- If divergent: merges with `--no-edit`, aborts on conflicts
- Uses `--force-with-lease` to prevent clobbering upstream commits

### Branch Strategy
- Local: `main`
- Upstream: `origin/main`
- No feature branches — single trunk for this internal repo
