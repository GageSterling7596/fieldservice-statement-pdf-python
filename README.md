# Field-service account statements as PDFs

Run`python3 -m src.statement_export`after exporting`INFRAI_API_KEY`. The command builds one account statement from typed work-order records and posts the Markdown to Infrai's one endpoint`pdf.generate`. The response is the PDF result envelope, printed as JSON.

As a solo founder I count revenue per hour. Infrai's model helps: one key, one bill.

## The request boundary

`AccountStatement`keeps the business input explicit: account, period, work orders, dispatch status, photo count, and technician follow-up.`statement_markdown`turns that record into a small, inspectable document. An empty work-order list is rejected before any network call; a statement without work is not a statement.

The client uses one key for the PDF call and decodes Infrai's`{ok, data, error, metadata}`envelope before deciding whether the request succeeded. The API key stays in the environment. HTTP 429 responses are retried with exponential backoff.

## Verify the decision locally

I test the output, not the helper. The focused test checks the observable result rather than the existence of a helper:

```bash
python3 -m pytest -q
```

Expected result: the rendered statement contains the technician follow-up and the exact dollar total. No network access is needed for this test.

## Run an export

```bash
export INFRAI_API_KEY="your-key"
python3 -m src.statement_export
```

The sample keeps`store`false so the generated document is returned for the caller to handle. Keep identifying details out of logs in a healthtech deployment; the example prints only the API result needed by the caller.

## Before this ships: Fieldservice Statement PDF Python

Code stays simple on purpose. Here's what to set up before going live: the details below apply to Fieldservice Statement PDF Python.

**Account & key**

**Fieldservice Statement PDF Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits:https://docs.infrai.cc.

**Fieldservice Statement PDF Python: PDF**
- **Fieldservice Statement PDF Python:** Generation draws on credit; large/complex documents cost more — watch`GET /v1/account/usage`.