# Grow Calendar für Home Assistant

Grow Calendar ist eine Custom Integration für Home Assistant, mit der du einen Grow in vier Phasen verwalten kannst:

- Saat
- Vegetation
- Blüte
- Ernte

Die Integration legt für jede Phase eine Datum-Entität an. Sobald du ein Startdatum für eine spätere Phase setzt, berechnet Grow Calendar daraus automatisch das Ende der vorherigen Phase. Zusätzlich erstellt die Integration einen Kalender, einen Sensor für die aktuelle Phase, einen Sensor für den aktuellen Phasentag und Sensoren für die Dauer zwischen den Phasen.

Die Daten werden lokal in Home Assistant gespeichert. Es wird kein externer Dienst verwendet.

## Installation

1. Kopiere den Ordner `custom_components/grow_calendar` in deinen Home-Assistant-Config-Ordner.
2. Starte Home Assistant neu.
3. Öffne `Einstellungen > Geräte & Dienste > Integration hinzufügen`.
4. Suche nach `Grow Calendar`.
5. Lege einen Namen an, z. B. `Grow Zelt 1`.

## Nutzung

Nach der Einrichtung entstehen vier Datum-Entitäten. Dort trägst du ein, wann eine Phase beginnt:

- `date.<grow>_saat`
- `date.<grow>_vegetation`
- `date.<grow>_blute`
- `date.<grow>_ernte`

Beispiel: Wenn `Saat` am 01.06. startet und `Vegetation` am 08.06. eingetragen wird, läuft die Saat-Phase vom 01.06. bis zum 08.06. Der Kalender zeigt diese Phase als ganztägigen Eintrag. Die Dauer-Sensoren berechnen die Tage zwischen den gesetzten Phasen automatisch.

## Entitäten

Pro Grow werden diese Entitäten angelegt:

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

Die Entity-IDs können je nach vergebenem Namen abweichen. Du findest sie in Home Assistant unter `Einstellungen > Geräte & Dienste > Entitäten`.

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

Alternativ kannst du eine bestimmte Config Entry ID verwenden:

```yaml
action: grow_calendar.clear_phase_date
data:
  entry_id: 0123456789abcdef
  phase: harvest
```

## Grow Calendar Card

Die Integration stellt zusätzlich eine Custom-Lovelace-Karte bereit. Sie zeigt:

- aktuelle Phase
- Startdatum der aktuellen Phase
- vergangene Tage seit Phasenstart
- Übersicht aller vier Phasen mit Startdatum, Enddatum und Tagen

### Resource eintragen

Nach dem Neustart von Home Assistant muss die gewünschte Karte einmal als Dashboard-Resource eingetragen werden:

1. Öffne `Einstellungen > Dashboards > Ressourcen`.
2. Klicke auf `Ressource hinzufügen`.
3. Trage für die vollständige Karte diese URL ein:

```text
/grow_calendar/grow-calendar-card.js
```

4. Für die reine Phasenkarte trage diese URL ein:

```text
/grow_calendar/grow-calendar-phases-card.js
```

5. Wähle jeweils als Ressourcentyp:

```text
JavaScript-Modul
```

### Vollständige Karte

```yaml
type: custom:grow-calendar-card
name: Grow
entity_prefix: grow
```

Die Karte leitet daraus automatisch diese Entitäten ab:

- `sensor.grow_aktuelle_phase`
- `sensor.grow_tag_der_phase`
- `calendar.grow_kalender`
- `date.grow_saat`
- `date.grow_vegetation`
- `date.grow_blute`
- `date.grow_ernte`

### Nur Phasen-Karten

Wenn du nur die vier kleinen Phasen-Karten ohne Überschrift und Status anzeigen möchtest:

```yaml
type: custom:grow-calendar-phases-card
entity_prefix: grow
```

Dafür muss die Resource `/grow_calendar/grow-calendar-phases-card.js` eingetragen sein.

Die Karte nutzt im Sections-Dashboard standardmäßig die volle Breite und ordnet die Phasen automatisch an. Solange genug Platz vorhanden ist, stehen die Phasen nebeneinander. Wenn eine Phase zu schmal werden würde, bricht sie automatisch in die nächste Zeile um.

Den Umbruchpunkt kannst du optional anpassen:

```yaml
type: custom:grow-calendar-phases-card
entity_prefix: grow
phase_min_width: 140px
```

Kleinere Werte halten die Phasen länger nebeneinander, größere Werte lassen sie früher umbrechen.

## Mehrere Grows

Du kannst die Integration mehrfach einrichten, z. B. für mehrere Zelte oder Pflanzen. Verwende dann pro Dashboard-Karte den passenden Prefix:

```yaml
type: custom:grow-calendar-card
name: Grow Zelt 2
entity_prefix: grow_zelt_2
```

Du musst die Sensoren nicht einzeln in der Karte umbenennen. Der Prefix wird an einer Stelle gesetzt und die Karte leitet Kalender, Phasensensor und Datum-Entitäten daraus ab.

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
