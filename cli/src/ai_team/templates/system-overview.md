---
title: "[Specification Title]"
version: "0.1"
status: draft  # draft | review | approved | superseded
created: YYYY-MM-DD
author: "[Author name or agent role]"
---

# [Specification Title]

<!--
This is the system overview spec (S-000): one plain-language document that
says what the project is, who it serves, and which components make it up.
Write for a reader who has never seen the project. Do not include technology
choices, interface definitions, configuration, implementation order, or
per-component status. Those belong in feature specs, ADRs, and the tracker.
Boundary rule: S-000 owns the decomposition — which components exist and
what each is for. A spec owns the contract of one component or feature.
-->

## Purpose

<!-- Recipe: one short paragraph. What the project is and the outcome it
  exists to deliver. -->

What is this project, and what outcome does it exist to deliver?

## Users

<!-- Recipe: one line per kind of user, naming what each needs from the
  system. -->

- **User kind.** What this user needs from the system.

## Pain points

<!-- Recipe: the concrete problems those users have today that the project
  removes. -->

- The concrete problem a user has today.

## Use cases

<!-- Recipe: the main things a user does with the system, each as one short
  scenario from the user's point of view. -->

- **Use case title.** One short scenario from the user's point of view.

## Solution overview

<!-- Recipe: a few paragraphs on how the system addresses the pain points,
  without naming technologies. -->

How does the system address the pain points above?

## Components

<!-- Recipe: the parts the system is divided into. Each entry gives its name,
  its owned responsibility (what it is for), its boundary (what it is not
  responsible for), and the other components it works with. S-000 owns the
  decomposition; a feature spec owns the contract of one component. -->

### Component name

- **Name:** The component's name.
- **Responsibility:** What the component is for.
- **Boundary:** What the component is not responsible for.
- **Works with:** The other components it works with.

## Project exclusions

<!-- Recipe: what the project deliberately does not do, each with a one-line
  reason. -->

- **Exclusion title.** One-line reason the project does not do this.

## Amendment Log

<!-- Optional. Use when an approved spec is amended after tasks are in flight.
| Date | What changed | Why | Affected tasks |
|------|-------------|-----|----------------|
| YYYY-MM-DD | Description of change | Reason for amendment | T-XXX, T-YYY |
-->
