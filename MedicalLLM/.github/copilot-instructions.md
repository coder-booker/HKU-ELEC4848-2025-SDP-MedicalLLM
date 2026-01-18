# Copilot instructions for MedicalLLM

## Project map (what to read first)
- Core package lives under [medical_llm_workflow/](medical_llm_workflow/); it follows a simple layered split: Domain (tasks/prompts), Infrastructure (Poe API client), Service (workflow engine/context).
- The current “happy path” example is in [medical_llm_workflow/main.py](medical_llm_workflow/main.py) and wires `WorkflowConfig` → `Workflow.fire()` → `Task.execute()`.
- Older experiments live under [old/](old/) and deprecated workflow code is under [medical_llm_workflow/Service/workflow/(Depre)engine/](medical_llm_workflow/Service/workflow/(Depre)engine/); avoid changing these unless explicitly requested.

## Architecture & data flow
- Models/configs are dataclasses and enums in [medical_llm_workflow/models/models.py](medical_llm_workflow/models/models.py) (e.g., `TaskConfig`, `WorkflowConfig`, `TaskType`, `LanguageType`, `PoeChatbotModel`). Use these types when adding new workflow behavior.
- `Task` is intentionally “thin”: it renders a prompt and calls the Poe API, leaving orchestration to the workflow layer (see [medical_llm_workflow/Domain/tasks/task.py](medical_llm_workflow/Domain/tasks/task.py)).
- Prompt construction is centralized in [medical_llm_workflow/Domain/prompts/prompt_generator.py](medical_llm_workflow/Domain/prompts/prompt_generator.py): `prompt_factory()` returns a list of `PromptTemplate`s based on `PromptType`, with a 3-step self‑refine flow (initial → critique → refine). Placeholders like `{{CASE}}`, `{{INITIAL_ANSWER}}`, `{{CRITIQUE}}` are expected.
- Poe integration uses the SDK in [medical_llm_workflow/Infrastructure/api/poe_client.py](medical_llm_workflow/Infrastructure/api/poe_client.py) via `fastapi_poe.stream_request` and `PoeChatbotModel` enum values.

## Workflows, examples, and integration points
- API key is expected via the `POE_API_KEY` environment variable (see [medical_llm_workflow/main.py](medical_llm_workflow/main.py)).
- Alternative Poe examples exist under [test/Chatbot.py](test/Chatbot.py) (OpenAI‑compatible client against Poe base URL) and [test/PoeBotExample.py](test/PoeBotExample.py) (multi‑agent Poe server bot).
- `test/config.yaml` contains example API config; treat it as local‑only and avoid committing real keys.

## Project‑specific conventions
- Comments and prompts are bilingual (EN/ZH); keep prompt templates and language selection consistent with `LanguageType` and existing dictionaries in `prompt_generator.py`.
- `Task` does not manage conversation history; context management is intended to live in `ContextManager` (see [medical_llm_workflow/Service/workflow/workflow_context/workflow_context.py](medical_llm_workflow/Service/workflow/workflow_context/workflow_context.py)).
- When adding new prompt types or task modes, extend the enums and templates in [medical_llm_workflow/models/models.py](medical_llm_workflow/models/models.py) and [medical_llm_workflow/Domain/prompts/prompt_generator.py](medical_llm_workflow/Domain/prompts/prompt_generator.py) together.

## Dependencies & setup notes
- Base dependency list is in [requirements.txt](requirements.txt) (currently `fastapi-poe`). Example scripts under [test/](test/) also use `openai`, `pydantic`, and `pyyaml`.
