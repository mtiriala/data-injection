# 📊 Système de Monitoring d'Ingestion de Données

## 🎯 Vue d'ensemble

Ce projet implémente un système complet de monitoring en temps réel pour l'ingestion de données, utilisant une architecture moderne basée sur Kafka, Loki, Promtail et Grafana. Le système surveille automatiquement les pipelines de données, détecte les anomalies et génère des alertes intelligentes.

## 🏗️ Architecture

```
S3 → Producer.py → Kafka → Promtail → Loki → Grafana
                                              ↓
                                         Dashboards + Alertes
```

## 📁 Structure du Projet

### 🔧 **Fichiers de Configuration Principaux**

#### `docker-compose.yml`
**Rôle**: Orchestrateur principal du système
- **Zookeeper**: Coordination des services Kafka
- **Kafka**: Bus de messages pour l'ingestion en temps réel
- **Loki**: Base de données de logs haute performance
- **Promtail**: Agent de collecte et transformation des logs
- **Grafana**: Interface de visualisation et d'alerting

#### `producer.py`
**Rôle**: Générateur de données d'ingestion
- Télécharge les logs depuis S3 (`s3://my12data/logs.json`)
- Transforme et envoie 72 logs vers Kafka
- Simule des succès (71) et échecs (1) réalistes
- Point d'entrée pour tester le système

#### `promtail-config.yml`
**Rôle**: Configuration de l'agent de collecte
- **Source**: Topic Kafka `ingestion-logs`
- **Transformation**: Extraction des champs JSON (`etat`, `source`, `entreprise`, `zone`)
- **Destination**: Loki avec labels structurés
- **Consumer Group**: `promtail-consumer` pour la persistance

#### `loki-config.yml`
**Rôle**: Configuration de la base de données de logs
- Stockage optimisé pour les logs temporels
- Indexation par labels pour requêtes rapides
- Rétention et compression automatiques

### 📊 **Dashboards Grafana** (`grafana-provisioning/dashboards/`)

#### `1-ingestion-health.json`
**Rôle**: Dashboard principal de santé du système
- **8 panels** de monitoring en temps réel:
  - Succès/Échecs (compteurs)
  - Taux d'échec (pourcentage)
  - Performance (p95 durée, mémoire max)
  - Timeline visuelle (SUCCESS vs FAILED)
  - Top sources par performance
  - Table des dernières erreurs

#### `2-errors-slas.json`
**Rôle**: Monitoring des SLAs et erreurs critiques
- **3 panels** spécialisés:
  - Taux d'échec global et par source
  - MTTR (Mean Time To Recovery)
  - SLO fraîcheur (alertes si pipeline silencieux)

#### `3-performance-resource.json`
**Rôle**: Analyse des performances et ressources
- **3 panels** de performance:
  - Percentiles de durée (p50/p95/p99)
  - Débit par source (#exécutions/5min)
  - Consommation CPU et mémoire

#### `4-logs-debugging.json`
**Rôle**: Interface de débogage avancé
- **1 panel** table filtrable:
  - Colonnes: Début, Fin, Durée, CPU, Mémoire, Description
  - Recherche et filtrage en temps réel
  - Export des données pour analyse

### 🚨 **Système d'Alerting** (`grafana-provisioning/alerting/`)

#### `1-echec-detecte.yml`
**Rôle**: Détection d'échecs critiques
- **Condition**: ≥1 log FAILED en 5 minutes
- **Seuil**: Critique (intervention immédiate)
- **Requête**: `{job="kafka-logs"} |= "FAILED"`

#### `2-taux-echec-eleve.yml`
**Rôle**: Surveillance du taux d'erreur global
- **Condition**: Taux d'échec >2% pendant 15 minutes
- **Seuil**: Warning (surveillance renforcée)
- **Calcul**: Ratio échecs/total avec protection division par zéro

#### `3-source-muette.yml`
**Rôle**: Détection de sources silencieuses
- **Condition**: Aucune exécution depuis 75 minutes
- **Seuil**: Critique (pipeline possiblement arrêté)
- **Requête**: `count_over_time({job="kafka-logs"}[75m])`

#### `4-latence-degradee.yml`
**Rôle**: Monitoring des performances
- **Condition**: Latence p95 >10 secondes
- **Seuil**: Warning (dégradation performance)
- **Métrique**: Basée sur le débit (`rate()`)

#### `5-surconsommation-ressources.yml`
**Rôle**: Surveillance des ressources système
- **Conditions**: 
  - Mémoire >150MB
  - CPU >60 secondes
- **Seuil**: Warning (optimisation requise)
- **Proxy**: Utilise le débit comme indicateur

### ⚙️ **Configuration de Provisioning**

#### `datasources/loki.yaml`
**Rôle**: Configuration automatique de la source de données
- **URL**: `http://loki:3100` (réseau Docker)
- **Type**: Loki (logs)
- **UID**: `Loki` (référence dans les dashboards)

#### `dashboards/dashboards.yml`
**Rôle**: Provisioning automatique des dashboards
- **Dossier**: `data-dashboard`
- **Auto-import**: Tous les fichiers JSON
- **Mise à jour**: Automatique au redémarrage

#### `alerting/alerting.yml`
**Rôle**: Configuration du système d'alerting
- **Dossier**: `data-alerts`
- **Règles**: Auto-chargement des fichiers YAML
- **Notifications**: Email (configurable)

## 🚀 **Utilisation**

### Démarrage du Système
```bash
cd /home/ubuntu/data-ingestion
docker-compose up -d
```

### Injection de Données
```bash
python3 producer.py
```

### Accès aux Interfaces
- **Grafana**: http://16.52.119.70:3000 (admin/admin)
- **Loki**: http://16.52.119.70:3100
- **Kafka**: 16.52.119.70:9092

## 📈 **Métriques Surveillées**

### Indicateurs de Santé
- **Succès/Échecs**: Comptage en temps réel
- **Taux d'erreur**: Pourcentage avec seuils
- **Disponibilité**: Détection de sources muettes

### Performance
- **Latence**: Percentiles p50/p95/p99
- **Débit**: Exécutions par minute
- **Ressources**: CPU et mémoire (proxy)

### SLAs
- **MTTR**: Temps moyen de récupération
- **Fraîcheur**: Délai depuis dernière exécution
- **Qualité**: Taux de succès par source

## 🔧 **Maintenance**

### Nettoyage des Données
```bash
docker-compose down
docker volume rm data-ingestion_loki-data data-ingestion_kafka-data
docker-compose up -d
```

### Redémarrage après EC2
```bash
docker-compose up -d
sleep 30
python3 producer.py
```

## 🎯 **Cas d'Usage**

1. **Monitoring Opérationnel**: Surveillance 24/7 des pipelines
2. **Détection d'Anomalies**: Alertes automatiques sur échecs
3. **Analyse de Performance**: Optimisation des sources lentes
4. **Débogage**: Investigation des erreurs avec logs détaillés
5. **Reporting**: Métriques SLA pour management

## 🏆 **Avantages**

- **Temps Réel**: Détection instantanée des problèmes
- **Scalabilité**: Architecture Kafka haute performance
- **Automatisation**: Provisioning complet via code
- **Flexibilité**: Dashboards et alertes configurables
- **Fiabilité**: Persistance des données et états