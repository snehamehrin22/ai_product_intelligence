# Setup Guide - Perplexity → Obsidian → Replit Pipeline

## Step 1: Set Up Bitwarden Credentials (One-Time)

This project uses the global Bitwarden credential system located at `~/.config/ai_credentials/`

### First Time Setup:

```bash
# Run the setup script
~/.config/ai_credentials/setup_bitwarden.sh
```

This will:
1. Install Bitwarden CLI (if needed)
2. Login to your Bitwarden account
3. Unlock your vault

### Add Required Credentials to Bitwarden:

You need to add these items to your Bitwarden vault (via web app at https://vault.bitwarden.com):

#### 1. Perplexity API
- **Name**: `Perplexity API`
- **Type**: Secure Note
- **Custom Fields**:
  - `api_key` = your Perplexity API key

#### 2. OpenAI API (optional, for later phases)
- **Name**: `OpenAI API`
- **Type**: Secure Note
- **Custom Fields**:
  - `api_key` = your OpenAI API key

#### 3. Replit (optional, for programmatic publishing)
- **Name**: `Replit`
- **Type**: Secure Note
- **Custom Fields**:
  - `api_token` = your Replit API token

---

## Step 2: Unlock Bitwarden (Every Terminal Session)

Before running any tests, you need to unlock your Bitwarden vault:

```bash
# Unlock vault
bw unlock

# Copy and run the export command it shows
export BW_SESSION="your-session-key-here"
```

**Pro Tip**: Add this alias to your `~/.zshrc`:
```bash
alias bw-unlock='export BW_SESSION=$(bw unlock --raw)'
```

Then just run `bw-unlock` in each new terminal.

---

## Step 3: Set Up Obsidian Vault

```bash
# Set the path to your Obsidian vault
export OBSIDIAN_VAULT_PATH="/path/to/your/obsidian/vault"

# Or add to your ~/.zshrc:
echo 'export OBSIDIAN_VAULT_PATH="/path/to/your/obsidian/vault"' >> ~/.zshrc
```

---

## Step 4: Test Credential Fetching

```bash
# Test in Python
python3 -c "
import sys
sys.path.append('/Users/snehamehrin/.config/ai_credentials')
from get_credential import get_credential
print(get_credential('Perplexity API', 'api_key'))
"

# Test in Bash
source ~/.config/ai_credentials/get_credential.sh
get_credential "Perplexity API" "api_key"
```

If you see your API key, you're all set!

---

## Step 5: Run Tests

```bash
cd tests/

# Test Perplexity connection
python3 perplexity/test_connection.py

# Test full pipeline with Flo Health
python3 run_pipeline.py --app "Flo Health"
```

---

## Troubleshooting

### "BW_SESSION not set"
Run `bw unlock` and export the session key.

### "Item not found"
Check the item name in Bitwarden:
```bash
bw list items | grep -i "perplexity"
```

### "bw: command not found"
Install Bitwarden CLI:
```bash
brew install bitwarden-cli
```

---

## Security Notes

- ✅ Never commit API keys to git
- ✅ BW_SESSION expires after timeout (secure)
- ✅ All credentials encrypted in Bitwarden
- ✅ Can revoke/rotate keys easily in Bitwarden
