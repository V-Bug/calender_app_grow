# Grow Calendar für Home Assistant

Custom Integration für einen Grow-Kalender mit vier Phasen:

- Saat
- Vegetation
- Blüte
- Ernte

Die vier Phasen werden als Datum-Entitäten angelegt. Sobald eine neue Phase beginnt, endet die vorherige Phase automatisch. Zusätzlich erzeugt die Integration einen Kalender und Sensoren für die Dauer zwischen den Phasen.

## Installation

1. Kopiere den Ordner `custom_components/grow_calendar` in deinen Home-Assistant-Config-Ordner.
2. Starte Home Assistant neu.
3. Öffne `Einstellungen > Geräte & Dienste > Integration hinzufügen`.
4. Suche nach `Grow Calendar`.
5. Lege einen Namen an, z. B. `Grow Zelt 1`.

## Entitäten

Pro Grow entstehen:

- `date.<grow>_saat`
- `date.<grow>_vegetation`
- `date.<grow>_blute`
- `date.<grow>_ernte`
- `calendar.<grow>_kalender`
- `sensor.<grow>_aktuelle_phase`
- `sensor.<grow>_tag_der_phase`
- `sensor.<grow>_saat_bis_vegetation`
- `sensor.<grow>_vegetation_bis_blute`
- `sensor.<grow>_blute_bis_ernte`

## Dashboard-Beispiel

```yaml
type: sections
sections:
  - type: grid
    cards:
      - type: calendar
        entities:
          - calendar.grow_kalender
      - type: entities
        title: Grow Zelt 1
        entities:
          - date.grow_saat
          - date.grow_vegetation
          - date.grow_blute
          - date.grow_ernte
          - sensor.grow_aktuelle_phase
          - sensor.grow_tag_der_phase
          - sensor.grow_saat_bis_vegetation
          - sensor.grow_vegetation_bis_blute
          - sensor.grow_blute_bis_ernte
```

Die Entity-IDs können je nach Name abweichen. In Home Assistant findest du sie unter `Einstellungen > Geräte & Dienste > Entitäten`.

## Phasendatum löschen

Wenn du ein Datum versehentlich gesetzt hast, kannst du es über den Service `grow_calendar.clear_phase_date` wieder löschen. Dadurch verschwindet auch der entsprechende Kalendereintrag.

Beispiel für `Ernte`:

```yaml
action: grow_calendar.clear_phase_date
data:
  phase: harvest
```

Wenn du mehrere Grows eingerichtet hast, gib zusätzlich den Namen an:

```yaml
action: grow_calendar.clear_phase_date
data:
  grow_name: Grow
  phase: harvest
```

## Grow Calendar Card

Die Integration stellt zusätzlich eine Custom-Lovelace-Karte bereit. Sie zeigt:

- aktuelle Phase
- Datum, an dem die aktuelle Phase gestartet ist
- wie viele Tage seitdem vergangen sind
- Übersicht aller vier Phasen mit Startdatum, Enddatum und Tagen

### Resource eintragen

Nach dem Neustart von Home Assistant muss die Karte einmal als Dashboard-Resource eingetragen werden:

1. Öffne `Einstellungen > Dashboards > Ressourcen`.
2. Klicke auf `Ressource hinzufügen`.
3. Trage diese URL ein:

```text
/grow_calendar/grow-calendar-card.js
```

4. Wähle als Ressourcentyp:

```text
JavaScript-Modul
```

### Karten-Beispiel

```yaml
type: custom:grow-calendar-card
name: Grow
entity_prefix: grow
```

Die Karte leitet daraus automatisch diese Entitäten ab:

- `sensor.grow_aktuelle_phase`
- `date.grow_saat`
- `date.grow_vegetation`
- `date.grow_blute`
- `date.grow_ernte`

Wenn du mehrere Grows angelegt hast, kannst du dieselbe Karte mehrfach verwenden und nur `entity_prefix` austauschen.

### Nur Phasen-Karten

Wenn du nur die vier kleinen Phasen-Karten ohne Überschrift und Status anzeigen möchtest:

```yaml
type: custom:grow-calendar-phases-card
entity_prefix: grow
```

Beispiel für einen zweiten Grow:

```yaml
type: custom:grow-calendar-card
name: Grow Zelt 2
entity_prefix: grow_zelt_2
```

Du musst die Sensoren dafür nicht einzeln in der Karte umbenennen. Der Prefix wird an dieser einen Stelle gesetzt und die Karte leitet Kalender, Phasensensor und Datum-Entitäten daraus ab.

Alternativ kannst du den Kalender direkt setzen. Wenn er dem Muster `calendar.<prefix>_kalender` folgt, erkennt die Karte den Prefix daraus automatisch:

```yaml
type: custom:grow-calendar-card
name: Grow Zelt 2
calendar_entity: calendar.grow_zelt_2_kalender
```

Falls deine Entity-IDs manuell anders heißen, kannst du Kalender und Phasensensor explizit setzen:

```yaml
type: custom:grow-calendar-card
name: Grow Zelt 2
entity_prefix: grow_zelt_2
calendar_entity: calendar.grow_zelt_2_kalender
phase_sensor: sensor.grow_zelt_2_aktuelle_phase
```
