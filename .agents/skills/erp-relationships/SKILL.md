---
name: erp-relationships
description: Rules for handling cross-module Foreign Keys and Child Tables in a Modular Monolith.
---

# Skill: ERP Modular Relationships

1. **Cross-Module Links:** When a spec dictates a `Link` to a table in another module (e.g., HR linking to Accounting), DO NOT create a SQLAlchemy `relationship()`. Implement it strictly as a `UUID` foreign key column.
2. **Internal Communication:** Modules must communicate via internal API routing, never via direct database joins.
3. **Child Tables:** When a spec lists "Child Tables" (e.g., Employee Education), these belong to the same parent module. Implement these using standard SQLAlchemy `relationship()` with `cascade="all, delete-orphan"`. Never use JSONB arrays for hierarchical tabular data.