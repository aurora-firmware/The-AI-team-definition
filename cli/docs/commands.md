<!-- GENERATED FILE — do not edit by hand.
     Regenerate with: bash cli/scripts/gen_docs.sh -->

# `ai-team`

Manage AI-team artifacts: specs, tasks, bugs, and ADRs.

**Usage**:

```console
$ ai-team [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-V, --version`: Print the ai-team version and exit.
* `--help`: Show this message and exit.

**Commands**:

* `adr`: Create and manage ADR artifacts.
* `archive`: Archive old completed tasks and resolved...
* `bug`: Create and manage bug artifacts.
* `change-request`: Create and manage change-request artifacts.
* `check-layout`: Check the repository layout and report...
* `init`: Scaffold an AI-team repository.
* `list`: List tasks, bugs, specs, ADRs, and change...
* `report`: Write a Gate 5 progress report.
* `show`: Show an artifact by identifier.
* `spec`: Create and manage specification artifacts.
* `status`: Show a Gate 5 status summary.
* `task`: Create and manage task artifacts.
* `validate`: Validate artifact metadata and...

## `ai-team adr`

Create and manage ADR artifacts.

**Usage**:

```console
$ ai-team adr [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `new`: Create a new ADR artifact from the bundled...

### `ai-team adr new`

Create a new ADR artifact from the bundled template.

**Usage**:

```console
$ ai-team adr new [OPTIONS] TITLE
```

**Arguments**:

* `TITLE`: [required]

**Options**:

* `--status [proposed|accepted|superseded]`: [default: proposed]
* `--supersedes TEXT`
* `--json`: Emit JSON output.
* `--help`: Show this message and exit.

## `ai-team archive`

Archive old completed tasks and resolved bugs into project/archive/YYYY-MM/.

**Usage**:

```console
$ ai-team archive [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--older-than TEXT`: [default: 90d]
* `--dry-run`
* `--help`: Show this message and exit.

## `ai-team bug`

Create and manage bug artifacts.

**Usage**:

```console
$ ai-team bug [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `new`: Create a new open bug artifact from the...
* `start`: Move an open bug to in-progress and update...
* `resolve`: Move an in-progress bug to resolved and...

### `ai-team bug new`

Create a new open bug artifact from the bundled template.

**Usage**:

```console
$ ai-team bug new [OPTIONS] TITLE
```

**Arguments**:

* `TITLE`: [required]

**Options**:

* `--severity [critical|high|medium|low]`: [default: medium]
* `--task TEXT`
* `--json`: Emit JSON output.
* `--help`: Show this message and exit.

### `ai-team bug start`

Move an open bug to in-progress and update status.

**Usage**:

```console
$ ai-team bug start [OPTIONS] BUG_ID
```

**Arguments**:

* `BUG_ID`: [required]

**Options**:

* `--help`: Show this message and exit.

### `ai-team bug resolve`

Move an in-progress bug to resolved and update status.

**Usage**:

```console
$ ai-team bug resolve [OPTIONS] BUG_ID
```

**Arguments**:

* `BUG_ID`: [required]

**Options**:

* `--help`: Show this message and exit.

## `ai-team change-request`

Create and manage change-request artifacts.

**Usage**:

```console
$ ai-team change-request [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `new`: Create a new change-request artifact from...

### `ai-team change-request new`

Create a new change-request artifact from the bundled template.

**Usage**:

```console
$ ai-team change-request new [OPTIONS] TITLE
```

**Arguments**:

* `TITLE`: [required]

**Options**:

* `--json`: Emit JSON output.
* `--help`: Show this message and exit.

## `ai-team check-layout`

Check the repository layout and report actionable findings.

**Usage**:

```console
$ ai-team check-layout [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

## `ai-team init`

Scaffold an AI-team repository.

**Usage**:

```console
$ ai-team init [OPTIONS] [PATH] COMMAND [ARGS]...
```

**Arguments**:

* `[PATH]`: [default: .]

**Options**:

* `--tools TEXT`
* `--force`
* `--dry-run`
* `--no-interactive`
* `--create-root-guidance`
* `--help`: Show this message and exit.

## `ai-team list`

List tasks, bugs, specs, ADRs, and change requests.

**Usage**:

```console
$ ai-team list [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `tasks`: List tasks from the project task folders.
* `bugs`: List bugs from the project bug folders.
* `specs`: List specs from the project specs folder.
* `adrs`: List ADRs from the project decisions folder.
* `change-requests`: List change requests from the project...

### `ai-team list tasks`

List tasks from the project task folders.

**Usage**:

```console
$ ai-team list tasks [OPTIONS]
```

**Options**:

* `--state TEXT`: Filter by task state folder.
* `--json`: Emit JSON output.
* `--help`: Show this message and exit.

### `ai-team list bugs`

List bugs from the project bug folders.

**Usage**:

```console
$ ai-team list bugs [OPTIONS]
```

**Options**:

* `--state TEXT`: Filter by bug state folder.
* `--json`: Emit JSON output.
* `--help`: Show this message and exit.

### `ai-team list specs`

List specs from the project specs folder.

**Usage**:

```console
$ ai-team list specs [OPTIONS]
```

**Options**:

* `--state TEXT`: Filter by state where applicable.
* `--json`: Emit JSON output.
* `--help`: Show this message and exit.

### `ai-team list adrs`

List ADRs from the project decisions folder.

**Usage**:

```console
$ ai-team list adrs [OPTIONS]
```

**Options**:

* `--state TEXT`: Filter by state where applicable.
* `--json`: Emit JSON output.
* `--help`: Show this message and exit.

### `ai-team list change-requests`

List change requests from the project change-requests folder.

**Usage**:

```console
$ ai-team list change-requests [OPTIONS]
```

**Options**:

* `--json`: Emit JSON output.
* `--help`: Show this message and exit.

## `ai-team report`

Write a Gate 5 progress report.

**Usage**:

```console
$ ai-team report [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--out PATH`: Override destination path.
* `--help`: Show this message and exit.

## `ai-team show`

Show an artifact by identifier.

**Usage**:

```console
$ ai-team show [OPTIONS] IDENTIFIER COMMAND [ARGS]...
```

**Arguments**:

* `IDENTIFIER`: [required]

**Options**:

* `--json`: Emit JSON output.
* `--help`: Show this message and exit.

## `ai-team spec`

Create and manage specification artifacts.

**Usage**:

```console
$ ai-team spec [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `new`: Create a new specification artifact from...

### `ai-team spec new`

Create a new specification artifact from the bundled template.

**Usage**:

```console
$ ai-team spec new [OPTIONS] TITLE
```

**Arguments**:

* `TITLE`: [required]

**Options**:

* `--author TEXT`: [default: planner]
* `--status [draft|review|approved|superseded]`: [default: draft]
* `--json`: Emit JSON output.
* `--help`: Show this message and exit.

## `ai-team status`

Show a Gate 5 status summary.

**Usage**:

```console
$ ai-team status [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--json`: Emit JSON output.
* `--help`: Show this message and exit.

## `ai-team task`

Create and manage task artifacts.

**Usage**:

```console
$ ai-team task [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `new`: Create a new pending task artifact from...
* `start`: Move a pending task to in-progress and...
* `complete`: Move an in-progress task to completed and...
* `unblock`: Move a blocked task to in-progress and...
* `block`: Move a task to blocked, update status, and...

### `ai-team task new`

Create a new pending task artifact from the bundled template.

**Usage**:

```console
$ ai-team task new [OPTIONS] TITLE
```

**Arguments**:

* `TITLE`: [required]

**Options**:

* `--priority [critical|high|medium|low]`: [default: medium]
* `--assigned-role TEXT`: [default: unassigned]
* `--spec TEXT`
* `--json`: Emit JSON output.
* `--help`: Show this message and exit.

### `ai-team task start`

Move a pending task to in-progress and update status.

**Usage**:

```console
$ ai-team task start [OPTIONS] TASK_ID
```

**Arguments**:

* `TASK_ID`: [required]

**Options**:

* `--help`: Show this message and exit.

### `ai-team task complete`

Move an in-progress task to completed and update status.

**Usage**:

```console
$ ai-team task complete [OPTIONS] TASK_ID
```

**Arguments**:

* `TASK_ID`: [required]

**Options**:

* `--help`: Show this message and exit.

### `ai-team task unblock`

Move a blocked task to in-progress and update status.

**Usage**:

```console
$ ai-team task unblock [OPTIONS] TASK_ID
```

**Arguments**:

* `TASK_ID`: [required]

**Options**:

* `--help`: Show this message and exit.

### `ai-team task block`

Move a task to blocked, update status, and append blocking reason.

**Usage**:

```console
$ ai-team task block [OPTIONS] TASK_ID
```

**Arguments**:

* `TASK_ID`: [required]

**Options**:

* `--reason TEXT`: [required]
* `--help`: Show this message and exit.

## `ai-team validate`

Validate artifact metadata and cross-references.

**Usage**:

```console
$ ai-team validate [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--all`: Validate all artifact types.
* `--tasks`: Validate tasks only.
* `--bugs`: Validate bugs only.
* `--specs`: Validate specs only.
* `--adrs`: Validate ADRs only.
* `--change-requests`: Validate change requests only.
* `--json`: Emit JSON output.
* `--help`: Show this message and exit.

