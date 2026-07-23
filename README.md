# OpenDataLake

> **OpenDataLake is an enterprise-style data engineering platform that demonstrates how modern data pipelines are built—from API ingestion and transformation to transactional persistence, data warehouse modeling, and business intelligence.**

OpenDataLake is an extensible ETL platform designed around enterprise software architecture principles. The platform provides a common framework for collecting data from APIs, files, databases, and other sources, transforming raw datasets into normalized records, and loading them into downstream systems for analytics and visualization.

New data sources are added as independent recipes, allowing the platform to grow without changing its core architecture.

---

## Features

• Modular ETL framework
• Recipe-based architecture
• Runner orchestration
• Dependency Injection
• Configuration management
• Reusable service layer
• Repository Pattern
• SQLAlchemy ORM
• PostgreSQL persistence
• Transaction management
• PostgreSQL upserts
• HTTP client abstraction
• Data normalization
• Command-line execution
• Extensible platform architecture

---

## Supported Data Sources

| Data Source | Status |
|--------------|--------|
| Events | ✅ |
| Weather | 🚧 Planned |
| Crime | 🚧 Planned |
| Census | 🚧 Planned |
| Real Estate | 🚧 Planned |
| Flights | 🚧 Planned |
| Hotels | 🚧 Planned |
| Economic Data | 🚧 Planned |

---

## Architecture

```text
                     Bootstrap
                          │
               Dependency Injection
                          │
                          ▼
                  Recipe Registry
                          │
                          ▼
                 Runner (Orchestrator)
                          │
      ┌───────────────────┼───────────────────┐
      ▼                   ▼                   ▼
 EventsRecipe        WeatherRecipe       CrimeRecipe
      │                   │                   │
      ▼                   ▼                   ▼
 TicketmasterService  WeatherService     CrimeService
      │                   │                   │
      ▼                   ▼                   ▼
 Ticketmaster API     Weather API        Crime API
      │                   │                   │
      ▼                   ▼                   ▼
   Transform          Transform          Transform
      │                   │                   │
      ▼                   ▼                   ▼
 EventRepository   WeatherRepository  CrimeRepository
      └───────────────────┼───────────────────┘
                          ▼
                     PostgreSQL
                          │
                          ▼
              Analytics SQL Layer
                          │
                          ▼
             Apache Superset / Tableau
           
```

---

## Vision

OpenDataLake is designed to become a unified data platform that aggregates information from multiple domains into a centralized analytics ecosystem.

Its modular architecture enables new data sources to be integrated by implementing new recipes rather than modifying the existing framework, making the platform scalable, maintainable, and easy to extend.

---

## Roadmap

### Foundation
- [x] Modular project structure
- [x] Virtual environment
- [x] BaseRecipe contract
- [x] Runner (ETL orchestrator)
- [x] Recipe Registry
- [x] Bootstrap initialization
- [x] Dependency Injection
- [x] Configuration (Settings)
- [x] Shared HTTP client
- [x] Command-line interface (`--recipe`)
- [x] Multi-recipe architecture

### Data Sources
- [x] Ticketmaster Events API
- [x] Multi-city event extraction
- [x] Data normalization
- [ ] Weather API
- [ ] Crime Data API
- [ ] Census API
- [ ] Real Estate Data
- [ ] Flight Data
- [ ] Hotel Data
- [ ] Economic Indicators

### Data Platform

- [x] PostgreSQL integration
- [x] SQLAlchemy ORM
- [x] Database models
- [x] Repository Pattern
- [x] Transaction management
- [x] PostgreSQL upserts
- [x] Data deduplication
- [ ] SQL views
- [ ] Data warehouse schemas
- [ ] Materialized views
- [ ] Query optimization

### DevOps
- [ ] Docker
- [ ] Docker Compose
- [ ] GitHub Actions CI
- [ ] Automated testing
- [ ] Code coverage
- [ ] Production configuration

### Data Warehouse & Analytics
- [ ] SQL analytics
- [ ] Analytical SQL views
- [ ] Event activity analysis
- [ ] Seasonal trend analysis
- [ ] Star schema
- [ ] Data marts
- [ ] Apache Superset
- [ ] Tableau
- [ ] Geographic dashboards

## Technology Stack

| Layer | Technology |
|--------|------------|
| Language | Python 3.13 |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Driver | Psycopg |
| Configuration | python-dotenv |
| Architecture | Dependency Injection, Repository Pattern |
| Data Source | Ticketmaster Discovery API |
| Future BI | Apache Superset, Tableau |
| Future Orchestration | Airflow, Kubernetes CronJobs |
