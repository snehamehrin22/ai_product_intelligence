# Execute Phase 2: Event Instrumentation

## Current Status

- **Branch:** phase-2-event-instrumentation
- **PRD:** ai-todo-app/prd-phase-2.json
- **Progress Log:** progress-phase-2.txt
- **Stories:** 13 user stories (US-2.1 through US-2.13)
- **Mode:** Autonomous execution

## To Execute Autonomously

```bash
cd /Users/snehamehrin/Desktop/ai_product_intelligence/learning
./scripts/ralph-phase-2.sh --auto
```

This will:
1. Read prd-phase-2.json
2. Select highest priority incomplete story
3. Implement it using Claude Code
4. Run tests
5. Commit changes
6. Update PRD
7. Log progress
8. Repeat until all 13 stories complete

## Manual Execution (for debugging)

```bash
# Run one story at a time with approval
./scripts/ralph-phase-2.sh

# Or implement stories manually following the PRD
```

## What Gets Built

Phase 2 adds:
- ✅ Azure Event Hubs setup (platform_events + agent_traces topics)
- ✅ Backend event publisher service
- ✅ Platform event schemas (8 events: task_*, agent_*, page_viewed, session_started)
- ✅ Platform event emission from API endpoints
- ✅ Frontend event emitter service
- ✅ Frontend event instrumentation
- ✅ POST /events API endpoint
- ✅ OpenTelemetry agent instrumentation
- ✅ Agent trace publishing to Event Hubs
- ✅ session_id propagation (frontend → backend → events → traces)
- ✅ Langfuse integration for real-time trace visualization
- ✅ End-to-end event flow validation
- ✅ Documentation and monitoring setup

## Architecture

```
Frontend (React)
  ├─ EventEmitter (generates session_id)
  ├─ Emits: task_created, agent_message_sent, etc.
  └─ Sends to: POST /events

Backend (FastAPI)
  ├─ POST /events → validates → publishes to Event Hubs
  ├─ EventPublisher service → Azure Event Hubs
  ├─ OpenTelemetry → LangGraph agent → Langfuse
  └─ Custom OTel exporter → Event Hubs (agent_traces)

Azure Event Hubs
  ├─ Topic: platform_events (8 event types)
  └─ Topic: agent_traces (OTel spans)

Langfuse
  └─ Real-time agent trace visualization
```

## Success Criteria

Before marking Phase 2 complete:
- [ ] All 13 user stories have `passes: true` in PRD
- [ ] Events flow from frontend → Event Hubs within 5 seconds
- [ ] Agent traces visible in Langfuse UI
- [ ] session_id joins platform events and agent traces (>95% match)
- [ ] All tests pass
- [ ] Documentation complete

## Next Phase

After Phase 2 completion → Phase 3: Streaming Ingestion + Bronze Layer
- Auto Loader ingestion from Event Hubs
- Databricks Bronze tables (medallion architecture)
- Schema evolution handling

---

**Ready to execute:** Run `./scripts/ralph-phase-2.sh --auto` to start autonomous execution.
