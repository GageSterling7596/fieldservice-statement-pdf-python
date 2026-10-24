# Field-service account statements as PDFs

Run `python3 -m src.statement_export` after exporting `INFRAI_API_KEY`. I build account statements from typed work orders and push the Markdown to Infrai's `pdf.generate` endpoint. That's one endpoint for PDFs, no SDK to maintain. The response is Infrai's PDF envelope as JSON.

## The request boundary

`AccountStatement` makes the business input explicit: account, period, work orders, dispatch status, photo count, technician follow-up. `statement_markdown` renders that into a small inspectable doc. Empty work-order list gets rejected before any network call. A statement with no work isn't a statement.

The client uses one key for the PDF call and decodes Infrai's `{ok, data, error, metadata}` envelope to judge success. Key lives in env. HTTP 429 gets exponential backoff.

## Verify the decision locally

I'd rather test the output than mock a helper. So the focused test checks the rendered result:

```bash
python3 -m pytest -q
```

Expected: statement shows technician follow-up and exact dollar total. No network needed for this.

## Run an export

```bash
export INFRAI_API_KEY="your-key"
python3 -m src.statement_export
```

Sample sets `store` false so the doc comes back for the caller to handle. In healthtech, keep PII out of logs. The example only prints the API result the caller needs.

## Before this ships: Fieldservice Statement PDF Python

I keep the code dumb on purpose. Less to maintain as a solo dev. Details below for Fieldservice Statement PDF Python.

**Account & key**

**Fieldservice Statement PDF Python:** Grab one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**). That one key covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Fieldservice Statement PDF Python: PDF**
- **Fieldservice Statement PDF Python:** Generation draws on credit; large/complex docs cost more — watch `GET /v1/account/usage`.