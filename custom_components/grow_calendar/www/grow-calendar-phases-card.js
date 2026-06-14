import "./grow-calendar-card.js";

const GrowCalendarCard = customElements.get("grow-calendar-card");

class GrowCalendarPhasesCard extends GrowCalendarCard {
  getCardSize() {
    return 2;
  }

  getGridOptions() {
    return {
      columns: this.config?.grid_columns || 12,
      min_columns: this.config?.min_grid_columns || 6,
      rows: 2,
      min_rows: 2,
    };
  }

  render() {
    if (!this.config || !this._hass) {
      return;
    }

    const phaseState = this._state(this.config.phase_sensor);
    const currentPhase = this._phaseByLabel(phaseState?.state);

    this.innerHTML = `
      <ha-card>
        <div class="phases-only">
          ${GrowCalendarCard.phases.map((phase, index) =>
            this._renderPhase(phase, index, currentPhase)
          ).join("")}
        </div>
      </ha-card>

      <style>
        grow-calendar-phases-card {
          container-type: inline-size;
          display: block;
        }

        grow-calendar-phase-card {
          container-type: inline-size;
          display: block;
        }

        ha-card {
          display: block;
          overflow: hidden;
          width: 100%;
        }

        .phases-only {
          display: grid;
          gap: 12px;
          grid-template-columns: repeat(auto-fit, minmax(${this.config.phase_min_width}, 1fr));
          padding: 12px;
        }

        .phase {
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          display: flex;
          flex-direction: column;
          gap: 10px;
          min-width: 0;
          padding: 12px;
        }

        .phase.active {
          border-color: var(--primary-color);
          box-shadow: inset 3px 0 0 var(--primary-color);
        }

        .phase-header {
          align-items: center;
          display: grid;
          gap: 8px;
          grid-template-columns: 24px minmax(0, 1fr);
        }

        .phase-header ha-icon {
          --mdc-icon-size: 22px;
          color: var(--secondary-text-color);
        }

        .phase.active .phase-header ha-icon {
          color: var(--primary-color);
        }

        .phase-name {
          color: var(--primary-text-color);
          font-size: 14px;
          font-weight: 600;
          line-height: 1.25;
        }

        .phase-details {
          display: flex;
          gap: 8px;
          min-width: 0;
        }

        .phase-detail {
          display: flex;
          flex: 1 0 78px;
          gap: 4px;
          min-width: 0;
        }

        .phase-detail span {
          color: var(--secondary-text-color);
          flex: 0 0 auto;
          font-size: 11px;
          line-height: 1.2;
        }

        .phase-detail strong {
          color: var(--primary-text-color);
          display: inline;
          font-size: 11px;
          font-weight: 600;
          line-height: 1.2;
          overflow-wrap: anywhere;
        }
      </style>
    `;
  }
}

if (!customElements.get("grow-calendar-phases-card")) {
  customElements.define("grow-calendar-phases-card", GrowCalendarPhasesCard);
}

if (!customElements.get("grow-calendar-phase-card")) {
  customElements.define("grow-calendar-phase-card", GrowCalendarPhasesCard);
}

window.customCards = window.customCards || [];
window.customCards.push({
  type: "grow-calendar-phases-card",
  name: "Grow Calendar Phases Card",
  description: "Zeigt nur die vier Grow-Phasen mit Start, Ende und Tagen.",
});
window.customCards.push({
  type: "grow-calendar-phase-card",
  name: "Grow Calendar Phase Card",
  description: "Alias für die Grow Calendar Phases Card.",
});
