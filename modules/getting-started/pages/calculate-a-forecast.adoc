---
title: Einen Forecast berechnen
description: Führe die grundlegenden Schritte aus, um einen Forecast zu erstellen.
product_label:
  - essential
  - advanced
  - enterprise
promote-service: new-planner-training
redirect_from:
  - /de/quickstart-forecasting/
redirect_reason: Updated filename on 29 November 2023
---

Dieser Artikel enthält eine Übersicht der zentralen Schritte auf dem Weg zu deinem ersten {% link_new Forecast | features/forecast/injixo-forecast/what-is-the-injixo-forecast.md %}. Auf Grundlage der historischen Daten berechnet der Forecast die Anzahl der Mitarbeiter, die für die Bearbeitung des eingehenden Volumens zu einer Aktivität in einer Planungseinheit erforderlich sind.
Dieser Artikel enthält eine Übersicht über die Schritte zum Erstellen eines Forecasts. Um mehr zu jedem Schritt zu erfahren, folge den Links in diesem Artikel.

Verwende diesen Artikel als ergänzende Checkliste für dein Onboarding. Besprich dich mit deinem Consultant, falls du Fragen hast.

## Voraussetzung <a name="prerequisite"></a>

Bevor du einen Schichtplan erstellst, stelle sicher, dass du deine {% link_new Grundkonfiguration korrekt eingerichtet | getting-started/set-up-base-configuration.md %} hast.

## 1\. Eine Integration einrichten <a name="1-set-up-an-integration"></a>

Richte unter _Account > Integrationen_{:.breadcrumbs} eine {% link_new Integration | features/acd-integration/cloud/how-integrations-work.md %} mit deinem externen System ein, um historische Daten hochzuladen. Die Integration lädt Daten in injixo hoch und erstellt Queues.

## 2\. Einen Workload einrichten <a name="2-set-up-a-workload"></a>

Erstelle unter _Forecast_{:.breadcrumbs} einen {% link_new Workload | features/forecast/injixo-forecast/create-workloads.md %} aus den Queues, die deine Integration erzeugt hat. Der Forecast wird innerhalb einiger Minuten erzeugt.

Hinweis: Um {% link_new externe Forecasts zu importieren | features/forecast/injixo-forecast/import-forecast.md %}, musst du mindestens eine Queue auswählen. Wenn keine Queue vorhanden ist, musst du über eine {% link_new CSV-Integration | features/acd-integration/cloud/add-csv-integration.md %} mindestens einen Datenpunkt hochladen.

## 3\. Ereignisse erstellen und hinzufügen <a name="3-create-and-add-events"></a>

Erstelle alle {% link_new Ereignisse | features/forecast/injixo-forecast/events-and-holidays.md %}, die die Forecast-Berechnung beeinflussen könnten. Füge die erstellten Ereignisse innerhalb deiner Workloads zum Verlauf und zum Forecast hinzu, um das Berechnungsergebnis zu verbessern.

## 4\. Eine Forecast-Version speichern <a name="4-save-a-forecast-version"></a>

Eine {% link_new Forecast-Version | features/forecast/injixo-forecast/save-forecast-versions.md %} ist eine Momentaufnahme der aktuellen Berechnung. Speichere eine Forecast-Version zur späteren Überprüfung oder zum Vergleich des Forecasts mit dem Volumen am aktuellen Tag, z.&nbsp;B. in {% link_new Dashboards | features/monitoring/dashboards/manage-dashboards.md %}.

## 5\. Mitarbeiterbedarf berechnen <a name="5-calculate-staff-requirements"></a>

Um optimierte Schichtpläne zu erstellen oder die Job-Optimierung auszuführen, musst du zuerst den {% link_new Mitarbeiterbedarf | features/forecast/injixo-forecast/calculate-staff-requirements.md %} für die entsprechenden Aktivitäten innerhalb deiner Workloads berechnen.

## Wie geht’s weiter? <a name="whats-next"></a>

Geschafft! Du kannst jetzt auf Basis des erzeugten Forecasts und Mitarbeiterbedarfs {% link_new deinen ersten Schichtplan erstellen | getting-started/create-a-schedule.md %}.
