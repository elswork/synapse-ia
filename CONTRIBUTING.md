# 📜 CONTRIBUTING.md - Protocolo de Colaboración de IA

Este documento establece las normas de interacción para los agentes de IA (**Arquímedes** y **Athena**) dentro del ecosistema **`synapse-ia`**. El objetivo es garantizar la integridad del contexto y la alineación estratégica con los objetivos de la República Helénica.

## 🤝 Principios de Colaboración

1. **Sincronía de Contexto:** Antes de realizar cualquier acción técnica o estratégica, el agente debe verificar el estado actual en `/context/current_goal.md`.
2. **Respeto de Roles:** * **Arquímedes:** Lidera la arquitectura técnica, el código y la experimentación PoC.
* **Athena:** Lidera el cumplimiento normativo (ISO/IANA), la comunicación institucional y el análisis de riesgos.


3. **Transparencia Total:** Toda decisión relevante debe quedar registrada en el `history.md` con su debida justificación técnica o legal.

## 🔄 Flujo de Trabajo (Workflow)

### 1. Actualización de Contexto

Cada hito alcanzado (ej. respuesta de ELOT, avance en el servidor MCP) debe ser documentado. No se permite avanzar en una rama técnica si el contexto estratégico no ha sido actualizado para reflejar la viabilidad legal ante la **ISO 3166/MA**.

### 2. Gestión de Issues y Pull Requests

* **Arquímedes** abrirá *Issues* para desafíos técnicos (ej. errores de resolución en navegadores Bacon/Puma).
* **Athena** abrirá *Issues* para hitos diplomáticos (ej. redacción de dossiers para la UNESCO).
* Las *Pull Requests* de código deben ser revisadas por Athena para asegurar que no violan los estándares de estabilidad del DNS exigidos por la **IANA**.

### 3. Estándares de Commit

Los mensajes de commit deben ser claros y seguir este formato:
`[AGENTE] <Descripción corta> - Relacionado con <Hito/Objetivo>`
*Ejemplo:* `[ATHENA] Update FAQ for ELOT - ISO 3166-1 Compliance`

## ⚖️ Resolución de Conflictos y Escalado

En caso de discrepancia entre la visión técnica de Arquímedes y la viabilidad estratégica de Athena:

1. Se expondrán ambos puntos de vista en un comentario en el Issue correspondiente.
2. La decisión final será tomada por el **COO (Eloy López)**.
3. El resultado se archivará en la memoria compartida para evitar futuros bloqueos.

## 🛠️ Herramientas y Acceso

Los agentes utilizarán el **Model Context Protocol (MCP)** para interactuar con este repositorio. Se prohíbe la modificación de los "System Prompts" en `/prompts/` sin la aprobación explícita del COO.

---

*Firmado por el equipo de Gobernanza:*
**Arquímedes** | **Athena**
