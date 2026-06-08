# Database

Banco de dados: **SQLite** (`db.sqlite3` na raiz do projeto).

## Diagrama de entidades

```mermaid
erDiagram
    CustomUser {
        int id PK
        string email UK
        string password
        string first_name
        string last_name
        boolean is_active
        boolean is_staff
        boolean is_superuser
        datetime created_at
        datetime updated_at
    }

    Team {
        int id PK
        string name
        string country_code UK
        string flag_emoji
        datetime created_at
        datetime updated_at
    }

    Stadium {
        int id PK
        string name
        string city
        string country
        datetime created_at
        datetime updated_at
    }

    Round {
        int id PK
        string name
        int order
        string phase
        datetime created_at
        datetime updated_at
    }

    Match {
        int id PK
        int round_id FK
        int stadium_id FK
        int home_team_id FK
        int away_team_id FK
        datetime match_datetime
        int home_score
        int away_score
        string status
        datetime created_at
        datetime updated_at
    }

    Pool {
        int id PK
        string name
        string description
        string invite_token UK
        int created_by_id FK
        datetime created_at
        datetime updated_at
    }

    PoolMember {
        int id PK
        int pool_id FK
        int user_id FK
        datetime joined_at
        datetime created_at
        datetime updated_at
    }

    Prediction {
        int id PK
        int user_id FK
        int match_id FK
        int pool_id FK
        int home_score
        int away_score
        int points
        datetime created_at
        datetime updated_at
    }

    Ranking {
        int id PK
        int user_id FK
        int pool_id FK
        int total_points
        int position
        datetime created_at
        datetime updated_at
    }

    CustomUser ||--o{ Pool : "created_by"
    CustomUser ||--o{ PoolMember : "user"
    CustomUser ||--o{ Prediction : "user"
    CustomUser ||--o{ Ranking : "user"
    Pool ||--o{ PoolMember : "members"
    Pool ||--o{ Prediction : "predictions"
    Pool ||--o{ Ranking : "rankings"
    Team ||--o{ Match : "home_team"
    Team ||--o{ Match : "away_team"
    Stadium ||--o{ Match : "stadium"
    Round ||--o{ Match : "round"
    Match ||--o{ Prediction : "match"
```

## Regras de integridade

- `PoolMember`: `unique_together = ('pool', 'user')` - um usuario so pode ser membro uma vez por bolao.
- `Prediction`: `unique_together = ('user', 'match', 'pool')` - um usuario so pode ter um palpite por jogo por bolao.
- `Ranking`: `unique_together = ('user', 'pool')` - um usuario so tem um ranking por bolao.
- `Match.home_score` e `Match.away_score` sao `null=True, blank=True` - so recebem valor quando o jogo eh finalizado.

## Campo audit em todos os modelos

Todo modelo possui os campos:

```python
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

Nenhuma excecao.

## Migrations

Comando para criar e aplicar migracoes:

```bash
python manage.py makemigrations <app>
python manage.py migrate
```

Sempre rodar `makemigrations` e `migrate` apos criar ou alterar modelos.