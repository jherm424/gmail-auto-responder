# Draft Mode Information

## How Draft Mode Works

By default, the Gmail Auto-Responder operates in **DRAFT MODE** for maximum safety. Instead of automatically sending emails, it creates draft responses in your Gmail account.

## What Happens in Draft Mode

1. **Monitors Inbox**: Scans for new unread emails matching your rules
2. **Generates Response**: Creates appropriate response based on templates
3. **Creates Draft**: Saves the response as a draft in your Gmail account
4. **Logs Activity**: Records what was processed

## Benefits of Draft Mode

✅ **Complete Control**: You review every response before sending
✅ **Safety First**: No accidental emails sent
✅ **Easy Review**: All drafts appear in Gmail's Drafts folder
✅ **Edit Before Send**: Modify responses as needed
✅ **Batch Processing**: Review and send multiple drafts at once

## Using the Application

### Test Mode (Recommended First)
```bash
python src/main.py --once --test-mode
```
- Shows what would happen without creating anything
- Perfect for testing your rules and templates

### Draft Mode (Default Behavior)
```bash
python src/main.py --once --draft-mode
```
- Creates actual drafts in your Gmail account
- Safe for production use

### Send Mode (Use with Caution)
```bash
python src/main.py --once --send-mode
```
- Actually sends emails automatically
- Only use when you're completely confident in your setup

## Checking Your Drafts

1. Open Gmail in your browser
2. Click on "Drafts" in the left sidebar
3. Review the auto-generated draft responses
4. Edit any drafts as needed
5. Send the ones you approve

## Environment Variables

```bash
# .env file settings
DRAFT_MODE=true          # Creates drafts (default)
TEST_MODE=true           # Just shows what would happen
```

## Command Line Options

- `--test-mode`: Preview mode only
- `--draft-mode`: Create drafts (default)
- `--send-mode`: Send emails directly (override draft mode)

## Security Notes

🔒 **Draft mode is enabled by default** to prevent accidental email sending
🔒 **Always test first** with `--test-mode`
🔒 **Review all drafts** before sending
🔒 **Use send mode sparingly** and only when certain