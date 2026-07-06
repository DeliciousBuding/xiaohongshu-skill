# n8n Example

Use an Execute Command node for read-only commands, then parse the JSON in a Code node.

## Search Command

```bash
python -m scripts search "北京周末去哪" --limit=5
```

Expected shape:

```json
{
  "count": 5,
  "results": []
}
```

## Safe Workflow

1. Execute Command: run a read-only command such as `search`, `feed`, or `user`.
2. Code: parse JSON and choose the fields your workflow needs.
3. Manual approval: require a person before any write command.
4. Execute Command: run `publish`, `comment`, `reply`, `like`, or `collect` only after approval.

Keep account cookies and local profile data outside exported n8n workflow files.
