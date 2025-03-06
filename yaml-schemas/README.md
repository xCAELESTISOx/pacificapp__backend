# API схемы в формате OpenAPI (YAML)

Эта директория содержит описания API в формате OpenAPI 3.0 (YAML), которые определяют схемы данных и структуру API. Эти файлы предназначены для использования бэкенд-разработчиками при создании API и генерации документации.

## Структура файлов

- `common.yml` - общие типы данных и компоненты
- `user.yml` - схемы для пользователей и аутентификации 
- `stress.yml` - схемы для API стресса
- `sleep.yml` - схемы для API сна
- `work-activity.yml` - схемы для API рабочей активности
- `dashboard.yml` - схемы для API дашборда
- `recommendation.yml` - схемы для API рекомендаций

## Использование

### Для создания документации Swagger/OpenAPI

Вы можете объединить эти файлы в один документ OpenAPI и использовать его для генерации документации API с помощью Swagger UI, Redoc или других инструментов.

```bash
# Установка инструмента для объединения YAML файлов
npm install -g swagger-cli

# Объединение файлов в один документ
swagger-cli bundle -o openapi.yml paths.yml

# Валидация документа
swagger-cli validate openapi.yml
```

### Для генерации кода на бэкенде

Эти схемы можно использовать для автоматической генерации моделей, сериализаторов, валидаторов и контроллеров для различных языков и фреймворков.

#### Для Python (FastAPI)

```python
# Установка генератора кода
pip install datamodel-code-generator

# Генерация моделей Pydantic из YAML схем
datamodel-codegen --input stress.yml --output models/stress.py
```

#### Для Java (Spring)

```bash
# Генерация Java классов из YAML схем с использованием openapi-generator
openapi-generator generate -i stress.yml -g spring -o ./generated-src
```

#### Для TypeScript (Node.js)

```bash
# Установка генератора кода
npm install -g openapi-typescript-codegen

# Генерация TypeScript интерфейсов и API-клиента
openapi -i stress.yml -o ./generated-src
```

## Редактирование и расширение

При изменении API необходимо обновлять соответствующие YAML-файлы. После обновления рекомендуется:

1. Проверить валидность YAML-файлов
2. Убедиться, что ссылки между файлами корректны
3. Проверить совместимость с предыдущими версиями API
4. Обновить версию API, если внесены несовместимые изменения

## Соглашения

1. Все даты и времена передаются в формате ISO 8601
2. Все пути указываются в kebab-case
3. Все параметры и имена свойств в snake_case
4. Все ответы API оборачиваются в стандартные объекты (ApiResponse или PaginatedResponse)

## Создание OpenAPI спецификации

Для создания полноценной спецификации OpenAPI нужно дополнительно определить:

1. Пути (endpoints) - в отдельном файле `paths.yml`
2. Серверы и базовый URL
3. Компоненты безопасности (JWT аутентификация)
4. Теги для группировки API

Пример структуры полного OpenAPI документа:

```yaml
openapi: 3.0.3
info:
  title: API мониторинга стресса
  description: API для мониторинга стресса, сна и рабочей активности
  version: 1.0.0
servers:
  - url: http://127.0.0.1:8000/api
    description: Локальный сервер разработки
security:
  - bearerAuth: []
paths:
  # Пути для API...
components:
  schemas:
    # Импорт схем из текущих файлов
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
``` 