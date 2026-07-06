#!/usr/bin/env python3
"""
Autonomous Agent Loop Executor for PRD-driven development.

Based on loop engineering research (2025-2026):
- Bounded execution with clear stopping conditions
- State machine orchestration with LLM at decision points
- Observability-first design (logging, metrics, tracing)
- Human-in-the-loop safeguards (approval gates, max iterations)
- Deterministic control flow with AI judgment bounded to specific decisions

Usage:
    python scripts/ralph_loop.py --prd learning/ai-todo-app/prd.json
    python scripts/ralph_loop.py --prd learning/ai-todo-app/prd.json --max-iterations 10 --auto-approve
"""

import argparse
import json
import logging
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional


# ============================================================================
# Configuration & Types
# ============================================================================

class StoryStatus(Enum):
    """User story completion status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    FAILED = "failed"
    BLOCKED = "blocked"


class LoopState(Enum):
    """Agent loop execution state."""
    INIT = "init"
    READ_PRD = "read_prd"
    SELECT_STORY = "select_story"
    EXECUTE_STORY = "execute_story"
    RUN_TESTS = "run_tests"
    COMMIT_CHANGES = "commit_changes"
    UPDATE_PRD = "update_prd"
    LOG_PROGRESS = "log_progress"
    CHECK_COMPLETION = "check_completion"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class UserStory:
    """User story model."""
    id: str
    title: str
    description: str
    priority: str
    passes: bool
    dependencies: List[str]
    acceptance_criteria: List[str]
    technical_notes: List[str]
    files: List[str]


@dataclass
class LoopMetrics:
    """Execution metrics for observability."""
    iterations: int = 0
    stories_completed: int = 0
    stories_failed: int = 0
    total_time_seconds: float = 0.0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


# ============================================================================
# Logging Setup (Observability First)
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/Users/snehamehrin/Desktop/ai_product_intelligence/learning/logs/ralph_loop.log')
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# Core Agent Loop Executor
# ============================================================================

class RalphAgentLoop:
    """
    Autonomous agent loop executor implementing loop engineering patterns.

    Design Principles:
    - Deterministic state machine controls flow
    - LLM (Claude Code) is invoked at bounded decision points
    - Clear stopping conditions prevent infinite loops
    - Human-in-the-loop approval gates for safety
    - Comprehensive logging for observability
    """

    def __init__(
        self,
        prd_path: Path,
        max_iterations: int = 50,
        auto_approve: bool = False,
        require_tests: bool = True
    ):
        self.prd_path = prd_path
        self.max_iterations = max_iterations
        self.auto_approve = auto_approve
        self.require_tests = require_tests

        self.state = LoopState.INIT
        self.metrics = LoopMetrics()
        self.current_story: Optional[UserStory] = None
        self.prd_data: dict = {}

        # Create logs directory if it doesn't exist
        Path('/Users/snehamehrin/Desktop/ai_product_intelligence/learning/logs').mkdir(exist_ok=True)

    def run(self) -> bool:
        """
        Main loop execution with bounded iterations.

        Returns:
            True if all stories completed successfully, False otherwise
        """
        logger.info("=" * 80)
        logger.info("🚀 Starting Ralph Agent Loop")
        logger.info(f"PRD: {self.prd_path}")
        logger.info(f"Max iterations: {self.max_iterations}")
        logger.info(f"Auto-approve: {self.auto_approve}")
        logger.info("=" * 80)

        start_time = datetime.now()

        try:
            while self.metrics.iterations < self.max_iterations:
                self.metrics.iterations += 1
                logger.info(f"\n{'='*80}")
                logger.info(f"🔄 Iteration {self.metrics.iterations}/{self.max_iterations}")
                logger.info(f"State: {self.state.value}")
                logger.info(f"{'='*80}\n")

                # State machine execution
                if self.state == LoopState.INIT:
                    self._state_init()
                elif self.state == LoopState.READ_PRD:
                    self._state_read_prd()
                elif self.state == LoopState.SELECT_STORY:
                    self._state_select_story()
                elif self.state == LoopState.EXECUTE_STORY:
                    self._state_execute_story()
                elif self.state == LoopState.RUN_TESTS:
                    self._state_run_tests()
                elif self.state == LoopState.COMMIT_CHANGES:
                    self._state_commit_changes()
                elif self.state == LoopState.UPDATE_PRD:
                    self._state_update_prd()
                elif self.state == LoopState.LOG_PROGRESS:
                    self._state_log_progress()
                elif self.state == LoopState.CHECK_COMPLETION:
                    if self._state_check_completion():
                        self.state = LoopState.COMPLETE
                        break
                elif self.state == LoopState.COMPLETE:
                    break
                elif self.state == LoopState.ERROR:
                    logger.error("❌ Loop entered ERROR state")
                    break
                else:
                    logger.error(f"Unknown state: {self.state}")
                    self.state = LoopState.ERROR
                    break

            # Check stopping conditions
            if self.metrics.iterations >= self.max_iterations:
                logger.warning(f"⚠️  Reached max iterations ({self.max_iterations}). Stopping.")
                return False

            self.metrics.total_time_seconds = (datetime.now() - start_time).total_seconds()
            self._print_summary()

            return self.state == LoopState.COMPLETE

        except KeyboardInterrupt:
            logger.info("\n⏸️  Loop interrupted by user")
            self._print_summary()
            return False
        except Exception as e:
            logger.exception(f"💥 Unexpected error: {e}")
            self.metrics.errors.append(str(e))
            return False

    # ========================================================================
    # State Machine Handlers
    # ========================================================================

    def _state_init(self):
        """Initialize loop state."""
        logger.info("📋 Initializing...")
        if not self.prd_path.exists():
            logger.error(f"PRD not found: {self.prd_path}")
            self.state = LoopState.ERROR
            return
        self.state = LoopState.READ_PRD

    def _state_read_prd(self):
        """Read and parse PRD."""
        logger.info(f"📖 Reading PRD from {self.prd_path}")
        try:
            with open(self.prd_path, 'r') as f:
                self.prd_data = json.load(f)
            logger.info(f"✅ Loaded PRD: {self.prd_data['projectName']}")
            logger.info(f"   Phase: {self.prd_data['phase']}")
            logger.info(f"   Stories: {len(self.prd_data['userStories'])}")
            self.state = LoopState.SELECT_STORY
        except Exception as e:
            logger.error(f"Failed to read PRD: {e}")
            self.metrics.errors.append(f"PRD read error: {e}")
            self.state = LoopState.ERROR

    def _state_select_story(self):
        """Select highest priority incomplete story."""
        logger.info("🎯 Selecting next user story...")

        # Find incomplete stories
        incomplete_stories = [
            UserStory(
                id=story['id'],
                title=story['title'],
                description=story['description'],
                priority=story['priority'],
                passes=story['passes'],
                dependencies=story.get('dependencies', []),
                acceptance_criteria=story['acceptanceCriteria'],
                technical_notes=story['technicalNotes'],
                files=story['files']
            )
            for story in self.prd_data['userStories']
            if not story['passes']
        ]

        if not incomplete_stories:
            logger.info("✅ No incomplete stories found")
            self.state = LoopState.COMPLETE
            return

        # Sort by priority (P0 > P1 > P2)
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2}
        incomplete_stories.sort(key=lambda s: priority_order.get(s.priority, 99))

        # Check dependencies
        for story in incomplete_stories:
            if self._dependencies_met(story):
                self.current_story = story
                logger.info(f"📌 Selected: {story.id} - {story.title}")
                logger.info(f"   Priority: {story.priority}")
                logger.info(f"   Dependencies: {story.dependencies or 'None'}")
                self.state = LoopState.EXECUTE_STORY
                return

        logger.warning("⚠️  No stories with met dependencies. Blocked.")
        self.state = LoopState.COMPLETE

    def _state_execute_story(self):
        """Execute story using Claude Code CLI."""
        logger.info(f"🔨 Executing story: {self.current_story.id}")

        # Construct prompt for Claude Code
        prompt = self._build_execution_prompt()

        if not self.auto_approve:
            logger.info("\n" + "=" * 80)
            logger.info("STORY TO EXECUTE:")
            logger.info(f"ID: {self.current_story.id}")
            logger.info(f"Title: {self.current_story.title}")
            logger.info(f"Files: {', '.join(self.current_story.files)}")
            logger.info("=" * 80)
            response = input("Continue? [Y/n]: ")
            if response.lower() == 'n':
                logger.info("⏭️  Skipped by user")
                self.state = LoopState.SELECT_STORY
                return

        # Call Claude Code CLI
        logger.info("🤖 Invoking Claude Code...")
        try:
            result = subprocess.run(
                ['claude', 'code', '--prompt', prompt],
                cwd=self.prd_path.parent,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode != 0:
                logger.error(f"Claude Code failed: {result.stderr}")
                self.metrics.errors.append(f"Story {self.current_story.id}: Claude Code error")
                self.metrics.stories_failed += 1
                self.state = LoopState.SELECT_STORY
            else:
                logger.info("✅ Story executed")
                self.state = LoopState.RUN_TESTS if self.require_tests else LoopState.COMMIT_CHANGES

        except subprocess.TimeoutExpired:
            logger.error("⏱️  Claude Code execution timed out")
            self.metrics.errors.append(f"Story {self.current_story.id}: Timeout")
            self.metrics.stories_failed += 1
            self.state = LoopState.SELECT_STORY
        except Exception as e:
            logger.error(f"Execution error: {e}")
            self.metrics.errors.append(f"Story {self.current_story.id}: {e}")
            self.metrics.stories_failed += 1
            self.state = LoopState.SELECT_STORY

    def _state_run_tests(self):
        """Run quality checks."""
        logger.info("🧪 Running tests...")

        # Determine test command based on project structure
        test_commands = [
            ('pytest', 'backend/tests/'),
            ('npm test', 'frontend/'),
        ]

        all_passed = True
        for cmd, path in test_commands:
            if not Path(self.prd_path.parent / path).exists():
                logger.info(f"⏭️  Skipping {cmd} (path not found: {path})")
                continue

            logger.info(f"Running: {cmd}")
            result = subprocess.run(
                cmd.split(),
                cwd=self.prd_path.parent / path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.error(f"❌ Tests failed: {cmd}")
                logger.error(result.stdout)
                all_passed = False

        if all_passed:
            logger.info("✅ All tests passed")
            self.state = LoopState.COMMIT_CHANGES
        else:
            logger.error("❌ Tests failed. Not committing.")
            self.metrics.errors.append(f"Story {self.current_story.id}: Tests failed")
            self.metrics.stories_failed += 1
            self.state = LoopState.SELECT_STORY

    def _state_commit_changes(self):
        """Commit changes to git."""
        logger.info("💾 Committing changes...")

        commit_msg = f"feat: {self.current_story.id} - {self.current_story.title}"

        try:
            # Git add all changes
            subprocess.run(['git', 'add', '.'], cwd=self.prd_path.parent, check=True)

            # Git commit
            result = subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=self.prd_path.parent,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info(f"✅ Committed: {commit_msg}")
                self.metrics.stories_completed += 1
                self.state = LoopState.UPDATE_PRD
            else:
                logger.warning(f"⚠️  No changes to commit (already committed?)")
                self.state = LoopState.UPDATE_PRD

        except Exception as e:
            logger.error(f"Commit failed: {e}")
            self.metrics.errors.append(f"Story {self.current_story.id}: Commit error")
            self.state = LoopState.SELECT_STORY

    def _state_update_prd(self):
        """Update PRD to mark story as complete."""
        logger.info("📝 Updating PRD...")

        try:
            # Update passes flag
            for story in self.prd_data['userStories']:
                if story['id'] == self.current_story.id:
                    story['passes'] = True
                    break

            # Write back to file
            with open(self.prd_path, 'w') as f:
                json.dump(self.prd_data, f, indent=2)

            logger.info(f"✅ Marked {self.current_story.id} as complete in PRD")
            self.state = LoopState.LOG_PROGRESS

        except Exception as e:
            logger.error(f"Failed to update PRD: {e}")
            self.metrics.errors.append(f"PRD update error: {e}")
            self.state = LoopState.LOG_PROGRESS

    def _state_log_progress(self):
        """Log progress to progress.txt."""
        logger.info("📊 Logging progress...")

        progress_file = self.prd_path.parent / 'progress.txt'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        entry = f"""
## {timestamp} - {self.current_story.id}
- **Story:** {self.current_story.title}
- **Status:** {'✅ Complete' if self.current_story.passes else '❌ Failed'}
- **Files changed:** {', '.join(self.current_story.files)}
- **Acceptance criteria:** {len(self.current_story.acceptance_criteria)} items
- **Learnings:** See commit message for details
---
"""

        try:
            with open(progress_file, 'a') as f:
                f.write(entry)
            logger.info("✅ Progress logged")
        except Exception as e:
            logger.error(f"Failed to log progress: {e}")

        self.state = LoopState.CHECK_COMPLETION

    def _state_check_completion(self) -> bool:
        """Check if all stories are complete."""
        logger.info("🏁 Checking completion status...")

        total_stories = len(self.prd_data['userStories'])
        completed_stories = sum(1 for s in self.prd_data['userStories'] if s['passes'])

        logger.info(f"Progress: {completed_stories}/{total_stories} stories complete")

        if completed_stories == total_stories:
            logger.info("🎉 ALL STORIES COMPLETE!")
            return True
        else:
            logger.info(f"📋 {total_stories - completed_stories} stories remaining")
            self.state = LoopState.SELECT_STORY
            return False

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _dependencies_met(self, story: UserStory) -> bool:
        """Check if story dependencies are satisfied."""
        if not story.dependencies:
            return True

        for dep_id in story.dependencies:
            dep_story = next(
                (s for s in self.prd_data['userStories'] if s['id'] == dep_id),
                None
            )
            if not dep_story or not dep_story['passes']:
                return False
        return True

    def _build_execution_prompt(self) -> str:
        """Build prompt for Claude Code."""
        return f"""You are implementing user story {self.current_story.id}.

**Title:** {self.current_story.title}

**Description:** {self.current_story.description}

**Acceptance Criteria:**
{chr(10).join(f'- {c}' for c in self.current_story.acceptance_criteria)}

**Technical Notes:**
{chr(10).join(f'- {n}' for n in self.current_story.technical_notes)}

**Files to modify:**
{chr(10).join(f'- {f}' for f in self.current_story.files)}

**Instructions:**
1. Implement this story according to the acceptance criteria
2. Follow patterns in CLAUDE.md and progress.txt
3. Run tests and ensure they pass
4. Commit with message: "feat: {self.current_story.id} - {self.current_story.title}"
5. Update any relevant CLAUDE.md files with learnings

Work autonomously and complete this story fully.
"""

    def _print_summary(self):
        """Print execution summary."""
        logger.info("\n" + "=" * 80)
        logger.info("📊 EXECUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total iterations: {self.metrics.iterations}")
        logger.info(f"Stories completed: {self.metrics.stories_completed}")
        logger.info(f"Stories failed: {self.metrics.stories_failed}")
        logger.info(f"Total time: {self.metrics.total_time_seconds:.2f}s")

        if self.metrics.errors:
            logger.info(f"\n⚠️  Errors encountered: {len(self.metrics.errors)}")
            for error in self.metrics.errors[:5]:  # Show first 5
                logger.info(f"  - {error}")

        logger.info("=" * 80 + "\n")


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Autonomous agent loop executor for PRD-driven development'
    )
    parser.add_argument(
        '--prd',
        type=Path,
        required=True,
        help='Path to prd.json file'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=50,
        help='Maximum loop iterations (safety bound)'
    )
    parser.add_argument(
        '--auto-approve',
        action='store_true',
        help='Auto-approve all actions (no human-in-the-loop)'
    )
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip running tests before commit'
    )

    args = parser.parse_args()

    loop = RalphAgentLoop(
        prd_path=args.prd,
        max_iterations=args.max_iterations,
        auto_approve=args.auto_approve,
        require_tests=not args.skip_tests
    )

    success = loop.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
