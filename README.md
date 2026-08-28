# AEGIS — AI Decision & Planning Engine

A futuristic Streamlit demo for a CCP individual project.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload:
   - `app.py`
   - `requirements.txt`
   - `README.md`
3. On Streamlit Community Cloud, choose the repository and set the main file to `app.py`.
4. Deploy.

No API key is required for the current demo. It uses realistic mock planning data so the complete UI/UX can be demonstrated immediately.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Demo flow

Launch → Login → Personalize → AI Introduction → Command Center → Create Plan → AI Processing → Plan Workspace → What-If Optimizer.

## Later AI integrations

The cleanest next step is to replace the demo processing/data layer with:
- an LLM API for natural-language parsing and reasoning,
- web search for current options,
- maps/routing,
- weather,
- database/authentication.

Keep API keys in Streamlit Secrets rather than hard-coding them.
