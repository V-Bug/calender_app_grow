const PHASES = [
  {
    key: "seed",
    label: "Saat",
    aliases: ["Saat", "Seed"],
    suffixes: ["saat", "seed"],
    icon: "mdi:seed",
  },
  {
    key: "vegetation",
    label: "Vegetation",
    aliases: ["Vegetation"],
    suffixes: ["vegetation"],
    icon: "mdi:sprout",
  },
  {
    key: "bloom",
    label: "Blüte",
    aliases: ["Blüte", "Blute", "Bluete", "Bloom"],
    suffixes: ["blute", "bluete", "bloom"],
    icon: "mdi:flower",
  },
  {
    key: "harvest",
    label: "Ernte",
    aliases: ["Ernte", "Harvest"],
    suffixes: ["ernte", "harvest"],
    icon: "mdi:basket",
  },
];

class GrowCalendarCard extends HTMLElement {
  setConfig(config) {
    const entityPrefix = config.entity_prefix || config.entityPrefix || "grow";

    this.config = {
      name: "Grow Calendar",
      ...config,
      entity_prefix: entityPrefix,
      phase_sensor: `sensor.${entityPrefix}_aktuelle_phase`,
      calendar_entity: `calendar.${entityPrefix}_kalender`,
    };
  }

  set hass(hass) {
    this._hass = hass;
    this._loadCalendarEvents();
    this.render();
  }

  getCardSize() {
    return 3;
  }

  render() {
    if (!this.config || !this._hass) {
      return;
    }

    const phaseState = this._state(this.config.phase_sensor);
    const currentPhase = this._phaseByLabel(phaseState?.state);

    this.innerHTML = `
      <ha-card>
        <div class="card-content">
          <div class="header">
            <div>
              <div class="title">${this._escape(this.config.name)}</div>
              <div class="subtitle">${this._escape(this._friendlyState(phaseState, "Keine aktive Phase"))}</div>
            </div>
            <ha-icon icon="${currentPhase?.icon || "mdi:calendar-clock"}"></ha-icon>
          </div>

          <div class="phases">
            ${PHASES.map((phase, index) =>
              this._renderPhase(phase, index, currentPhase)
            ).join("")}
          </div>
        </div>
      </ha-card>

      <style>
        ha-card {
          display: block;
          min-width: 1160px;
          overflow: hidden;
        }

        .card-content {
          display: flex;
          flex-direction: column;
          gap: 24px;
          padding: 24px;
        }

        .header {
          align-items: center;
          display: flex;
          justify-content: space-between;
          gap: 16px;
        }

        .title {
          color: var(--primary-text-color);
          font-size: 22px;
          font-weight: 600;
          line-height: 1.2;
        }

        .subtitle {
          color: var(--secondary-text-color);
          font-size: 15px;
          line-height: 1.4;
          margin-top: 4px;
        }

        .header ha-icon {
          --mdc-icon-size: 44px;
          color: var(--primary-color);
          flex: 0 0 auto;
        }

        .phases {
          display: grid;
          gap: 18px;
          grid-template-columns: repeat(4, minmax(250px, 1fr));
        }

        .phase {
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          display: flex;
          flex-direction: column;
          gap: 16px;
          min-width: 0;
          padding: 18px;
        }

        .phase.active {
          border-color: var(--primary-color);
          box-shadow: inset 3px 0 0 var(--primary-color);
        }

        .phase-header {
          align-items: center;
          display: grid;
          gap: 12px;
          grid-template-columns: 32px minmax(0, 1fr);
        }

        .phase-header ha-icon {
          --mdc-icon-size: 26px;
          color: var(--secondary-text-color);
        }

        .phase.active .phase-header ha-icon {
          color: var(--primary-color);
        }

        .phase-name {
          color: var(--primary-text-color);
          font-size: 16px;
          font-weight: 500;
          line-height: 1.25;
        }

        .phase-details {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .phase-detail {
          align-items: flex-start;
          display: flex;
          gap: 8px;
          justify-content: space-between;
          min-width: 0;
        }

        .phase-detail span {
          color: var(--secondary-text-color);
          flex: 0 0 auto;
          font-size: 14px;
          line-height: 1.3;
        }

        .phase-detail strong {
          color: var(--primary-text-color);
          display: inline;
          font-size: 14px;
          font-weight: 600;
          line-height: 1.25;
          overflow-wrap: anywhere;
          text-align: right;
        }

        @media (max-width: 430px) {
          .card-content {
            padding: 18px;
          }

          .phases {
            grid-template-columns: repeat(4, minmax(250px, 1fr));
            overflow-x: auto;
            padding-bottom: 4px;
          }

          .phase-detail {
            justify-content: flex-start;
          }

          .phase-detail strong {
            text-align: left;
          }
        }
      </style>
    `;
  }

  _renderPhase(phase, index, currentPhase) {
    const calendarPhase = this._calendarPhase(phase);
    const start = calendarPhase?.start || this._dateState(phase)?.state;
    const nextPhase = PHASES[index + 1];
    const end =
      calendarPhase?.end ||
      (nextPhase ? this._dateState(nextPhase)?.state : undefined);
    const days = this._phaseDays(start, end);
    const active = currentPhase?.key === phase.key;

    return `
      <div class="phase ${active ? "active" : ""}">
        <div class="phase-header">
          <ha-icon icon="${phase.icon}"></ha-icon>
          <div class="phase-name">${this._escape(phase.label)}</div>
        </div>
        <div class="phase-details">
          <div class="phase-detail">
            <span>Start:</span>
            <strong>${this._escape(this._formatDate(start) || "-")}</strong>
          </div>
          <div class="phase-detail">
            <span>Ende:</span>
            <strong>${this._escape(this._formatDate(end) || "offen")}</strong>
          </div>
          <div class="phase-detail">
            <span>Tage:</span>
            <strong>${this._escape(this._formatDays(days))}</strong>
          </div>
        </div>
      </div>
    `;
  }

  _state(entityId) {
    return this._hass.states[entityId];
  }

  _phaseByLabel(label) {
    if (!this._isKnown(label)) {
      return undefined;
    }

    const normalized = this._normalize(label);
    return PHASES.find((phase) =>
      phase.aliases.some((alias) => this._normalize(alias) === normalized)
    );
  }

  _dateState(phase) {
    const configuredCandidates = phase.suffixes.map(
      (suffix) => `date.${this.config.entity_prefix}_${suffix}`
    );
    const exactMatch = configuredCandidates
      .map((entityId) => this._state(entityId))
      .find(Boolean);

    if (exactMatch) {
      return exactMatch;
    }

    const normalizedPrefix = this._normalize(this.config.entity_prefix);
    const normalizedAliases = phase.aliases.map((alias) => this._normalize(alias));
    return Object.entries(this._hass.states)
      .filter(([entityId]) => entityId.startsWith("date."))
      .map(([entityId, state]) => ({
        entityId,
        state,
        normalizedEntityId: this._normalize(entityId),
        normalizedName: this._normalize(state.attributes?.friendly_name || ""),
      }))
      .find(({ normalizedEntityId, normalizedName }) => {
        const matchesPrefix =
          normalizedEntityId.includes(normalizedPrefix) ||
          normalizedName.includes(normalizedPrefix);
        const matchesPhase = normalizedAliases.some(
          (alias) =>
            normalizedEntityId.includes(alias) || normalizedName.includes(alias)
        );
        return matchesPrefix && matchesPhase;
      })?.state;
  }

  async _loadCalendarEvents() {
    const calendarState = this.config?.calendar_entity
      ? this._state(this.config.calendar_entity)
      : undefined;
    const eventLoadKey = `${this.config?.calendar_entity}:${calendarState?.last_changed || ""}`;

    if (
      !this._hass ||
      !this.config?.calendar_entity ||
      this._eventsLoadedFor === eventLoadKey ||
      this._loadingEvents
    ) {
      return;
    }

    this._loadingEvents = true;
    const now = new Date();
    const start = new Date(now);
    start.setFullYear(start.getFullYear() - 5);
    const end = new Date(now);
    end.setFullYear(end.getFullYear() + 5);

    try {
      const response = await this._hass.callWS({
        type: "calendar/event/list",
        entity_id: this.config.calendar_entity,
        start: start.toISOString(),
        end: end.toISOString(),
      });
      this._calendarEvents = Array.isArray(response) ? response : response.events || [];
      this._eventsLoadedFor = eventLoadKey;
      this.render();
    } catch (_error) {
      this._calendarEvents = [];
      this._eventsLoadedFor = eventLoadKey;
    } finally {
      this._loadingEvents = false;
    }
  }

  _calendarPhase(phase) {
    const event = (this._calendarEvents || []).find((candidate) =>
      this._isPhaseCalendarEvent(candidate, phase)
    );

    if (!event) {
      return undefined;
    }

    return {
      start: this._eventDate(event.start),
      end: this._eventDate(event.end),
    };
  }

  _isPhaseCalendarEvent(event, phase) {
    const uid = this._normalize(event.uid || "");
    if (uid.startsWith(`${phase.key}-`)) {
      return true;
    }

    const summary = this._normalize(event.summary || "");
    return phase.aliases.some((alias) => summary.startsWith(this._normalize(alias)));
  }

  _eventDate(value) {
    if (!value) {
      return undefined;
    }

    if (typeof value === "string") {
      return value.slice(0, 10);
    }

    if (value.date) {
      return value.date;
    }

    if (value.dateTime) {
      return value.dateTime.slice(0, 10);
    }

    return undefined;
  }

  _friendlyState(stateObj, fallback) {
    if (!stateObj || !this._isKnown(stateObj.state)) {
      return fallback;
    }

    return stateObj.state;
  }

  _formatDate(value) {
    if (!this._isKnown(value)) {
      return undefined;
    }

    const date = new Date(`${value}T00:00:00`);
    if (Number.isNaN(date.getTime())) {
      return value;
    }

    const language = this._hass.locale?.language || navigator.language || "de-DE";
    return new Intl.DateTimeFormat(language, {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }).format(date);
  }

  _formatDays(value) {
    if (!this._isKnown(value)) {
      return "-";
    }

    const days = Number(value);
    if (!Number.isFinite(days)) {
      return String(value);
    }

    return days === 1 ? "1 Tag" : `${days} Tage`;
  }

  _daysSince(value) {
    if (!this._isKnown(value)) {
      return undefined;
    }

    const start = new Date(`${value}T00:00:00`);
    if (Number.isNaN(start.getTime())) {
      return undefined;
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return Math.floor((today.getTime() - start.getTime()) / 86400000) + 1;
  }

  _phaseDays(startValue, endValue) {
    if (!this._isKnown(startValue)) {
      return undefined;
    }

    const start = new Date(`${startValue}T00:00:00`);
    if (Number.isNaN(start.getTime())) {
      return undefined;
    }

    if (this._isKnown(endValue)) {
      const end = new Date(`${endValue}T00:00:00`);
      if (Number.isNaN(end.getTime()) || end < start) {
        return undefined;
      }

      return Math.floor((end.getTime() - start.getTime()) / 86400000);
    }

    return this._daysSince(startValue);
  }

  _isKnown(value) {
    return value !== undefined && value !== null && !["", "unknown", "unavailable"].includes(value);
  }

  _normalize(value) {
    return String(value)
      .trim()
      .toLocaleLowerCase("de-DE")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  _escape(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}

customElements.define("grow-calendar-card", GrowCalendarCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "grow-calendar-card",
  name: "Grow Calendar Card",
  description: "Zeigt die aktuelle Grow-Phase, das Startdatum und vergangene Tage.",
});
