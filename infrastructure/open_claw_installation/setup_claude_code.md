If nothing else is running, you still **don’t need** root for Claude Code; I’d keep it non‑root but treat the VPS as “disposable” if something breaks.

### What I’d do on an empty VPS

1. **Create a dedicated user** and do everything as that user:

```bash
# as root, once
adduser agent
su - agent
```

2. **Install Claude Code as `agent`** (no sudo):

```bash
curl -fsSL https://claude.ai/install.sh | bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
claude login
```

3. Put all your projects under something like:

```bash
mkdir -p ~/workspaces
```

Then later, mount `~/workspaces` into OpenClaw’s Docker container and call Claude Code via a wrapper, all still as `agent`.

### Why still avoid root even on an empty VPS

- If Claude Code or an agent makes a mistake, it can still wipe the OS or lock SSH if it runs as root.  
- As `agent`, worst case you blow away `/home/agent`, but you can just rebuild the VPS or reinstall tools.  
- You lose almost nothing by avoiding root: compilers, git, Node, Python, etc. all work fine for a normal user if you install them under `$HOME`. [andrey-markin](https://andrey-markin.com/blog/claude-code-vps-setup)

So: use a **single non‑root user + dedicated workspace directories**, and treat the VPS as a sandbox you can recreate, rather than giving Claude Code full root.