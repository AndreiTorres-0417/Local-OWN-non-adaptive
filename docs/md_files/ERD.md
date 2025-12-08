# Entity Relationship Diagram

## learning_pathway

| Column      | Type         |
| ----------- | ------------ |
| **PK** id   | CHAR(36)     |
| name        | VARCHAR(50)  |
| description | VARCHAR(100) |
| is_active   | BOOLEAN      |
| created_at  | DATETIME     |
| updated_at  | DATETIME     |

---

## assessment_template

| Column                     | Type                                   |
| -------------------------- | -------------------------------------- |
| **PK** id                  | CHAR(36)                               |
| **FK** learning_pathway_id | CHAR(36)                               |
| name                       | VARCHAR(100)                           |
| assessment_type            | ENUM('PLACEMENT','SPEAKING','WRITING') |
| rubric                     | JSON                                   |
| meta                       | JSON                                   |
| version                    | INT                                    |
| published_at               | DATETIME                               |
| created_by                 | VARCHAR(50)                            |
| created_at                 | DATETIME                               |
| updated_at                 | DATETIME                               |
| is_active                  | BOOLEAN                                |

---

## assessment_config

Stores configuration parameters for different assessment types. Each template can have multiple configs.

| Column             | Type     |
| ------------------ | -------- |
| **PK** id          | CHAR(36) |
| **FK** template_id | CHAR(36) |
| parameters         | JSON     |
| adaptive_params    | JSON     |
| speaking_params    | JSON     |
| writing_params     | JSON     |
| is_active          | BOOLEAN  |
| created_at         | DATETIME |
| updated_at         | DATETIME |

**JSON Field Definitions:**

`adaptive_params` (for PLACEMENT type):

```json
{
  "starting_ability": 0.0,
  "min_questions": 5,
  "max_questions": 25,
  "stopping_criterion": { "standard_error": 0.3 },
  "skill_areas": ["grammar", "vocabulary", "reading"],
  "proficiency_range": {
    "A1": { "min": -2.0, "max": -1.0 },
    "A2": { "min": -1.0, "max": -0.5 },
    "B1": { "min": -0.5, "max": 0.0 },
    "B2": { "min": 0.0, "max": 1.0 },
    "C1": { "min": 1.0, "max": 1.5 },
    "C2": { "min": 1.5, "max": 2.0 }
  }
}
```

`speaking_params` (for SPEAKING type):

```json
{
  "max_recording_seconds": 120,
  "criteria_weights": {
    "fluency": 0.25,
    "pronunciation": 0.25,
    "grammar": 0.2,
    "vocabulary": 0.15,
    "coherence": 0.15
  }
}
```

`writing_params` (for WRITING type):

```json
{
  "min_words": 150,
  "max_words": 500,
  "time_limit_minutes": 30,
  "criteria_weights": {
    "content": 0.3,
    "organization": 0.25,
    "grammar": 0.25,
    "vocabulary": 0.2
  }
}
```

---

## template_item

Junction table linking templates to specific items (used for fixed-mode assessments like Speaking/Writing).

| Column             | Type     |
| ------------------ | -------- |
| **PK** id          | CHAR(36) |
| **FK** template_id | CHAR(36) |
| **FK** item_id     | CHAR(36) |
| item_order         | INT      |
| item_meta          | JSON     |
| created_at         | DATETIME |
| updated_at         | DATETIME |

---

## assessment_item

The item bank containing all assessment questions/prompts.

| Column                   | Type        |
| ------------------------ | ----------- |
| **PK** id                | CHAR(36)    |
| content                  | JSON        |
| item_type                | VARCHAR(50) |
| skill_area               | JSON        |
| target_proficiency_level | VARCHAR(15) |
| parameters               | JSON        |
| is_active                | BOOLEAN     |
| created_at               | DATETIME    |
| updated_at               | DATETIME    |

---

## course

| Column                   | Type         |
| ------------------------ | ------------ |
| **PK** id                | CHAR(36)     |
| **FK** pathway_id        | CHAR(36)     |
| title                    | VARCHAR(50)  |
| description              | VARCHAR(255) |
| course_code              | VARCHAR(50)  |
| target_proficiency_level | VARCHAR(20)  |
| primary_skill            | VARCHAR(50)  |
| secondary_skills         | JSON         |
| skill_scores             | JSON         |
| estimated_duration_hours | DECIMAL      |
| difficulty_order         | INT          |
| prerequisites            | JSON         |
| is_active                | BOOLEAN      |
| created_at               | DATETIME     |
| updated_at               | DATETIME     |

---

## lesson

| Column                     | Type         |
| -------------------------- | ------------ |
| **PK** id                  | CHAR(36)     |
| **FK** course_id           | CHAR(36)     |
| title                      | VARCHAR(100) |
| description                | VARCHAR(255) |
| lesson_order               | INT          |
| target_skills              | JSON         |
| content_type               | VARCHAR(50)  |
| relative_difficulty        | DECIMAL      |
| estimated_duration_minutes | DECIMAL      |
| is_active                  | BOOLEAN      |
| created_at                 | DATETIME     |
| updated_at                 | DATETIME     |

---

## assigned_assessment

Tracks admin assignment of assessments to students.

| Column             | Type                                                |
| ------------------ | --------------------------------------------------- |
| **PK** id          | CHAR(36)                                            |
| **FK** template_id | CHAR(36)                                            |
| test_taker_id      | VARCHAR(50)                                         |
| test_taker_type    | ENUM('STUDENT','TEACHER','ADMIN')                   |
| assigned_by        | VARCHAR(50)                                         |
| assigned_at        | DATETIME                                            |
| due_at             | DATETIME                                            |
| status             | ENUM('PENDING','IN_PROGRESS','COMPLETED','EXPIRED') |
| notes              | VARCHAR(255)                                        |

---

## assessment_session

Tracks an individual test attempt.

| Column             | Type                                                  |
| ------------------ | ----------------------------------------------------- |
| **PK** id          | CHAR(36)                                              |
| **FK** assigned_id | CHAR(36)                                              |
| current_ability    | DECIMAL(8,4)                                          |
| standard_error     | DECIMAL(8,4)                                          |
| questions_answered | INT                                                   |
| status             | ENUM('CANCELLED','IN_PROGRESS','COMPLETED','EXPIRED') |
| current_index      | INT                                                   |
| rubric_snapshot    | JSON                                                  |
| template_snapshot  | JSON                                                  |
| started_at         | DATETIME                                              |
| completed_at       | DATETIME                                              |
| expires_at         | DATETIME                                              |

---

## assessment_response

Records a user's answer to an assessment item.

| Column            | Type          |
| ----------------- | ------------- |
| **PK** id         | CHAR(36)      |
| **FK** session_id | CHAR(36)      |
| **FK** item_id    | CHAR(36)      |
| response_data     | JSON          |
| is_correct        | BOOLEAN       |
| raw_score         | DECIMAL(5,2)  |
| presented_at      | DATETIME      |
| submitted_at      | DATETIME      |
| time_taken        | INT           |
| media_key         | VARCHAR(255)  |
| asr_transcript    | VARCHAR(4000) |

---

## result

Base result table for all assessment types.

| Column             | Type              |
| ------------------ | ----------------- |
| **PK** id          | CHAR(36)          |
| **FK** session_id  | CHAR(36)          |
| proficiency_level  | VARCHAR(10)       |
| validated          | BOOLEAN           |
| skill_scores       | JSON              |
| overall_score      | DECIMAL(5,2)      |
| result_type        | ENUM('P','S','W') |
| information_metric | JSON              |
| created_at         | DATETIME          |

---

## placement_result

Extended result data for placement assessments.

| Column                | Type         |
| --------------------- | ------------ |
| **PK** id             | CHAR(36)     |
| **FK** result_id      | CHAR(36)     |
| average_response_time | DECIMAL(8,2) |
| total_items           | INT          |

---

## speaking_result

Extended result data for speaking assessments.

| Column           | Type     |
| ---------------- | -------- |
| **PK** id        | CHAR(36) |
| **FK** result_id | CHAR(36) |
| transcript       | TEXT     |
| criteria_scores  | JSON     |

---

## writing_result

Extended result data for writing assessments.

| Column           | Type        |
| ---------------- | ----------- |
| **PK** id        | CHAR(36)    |
| **FK** result_id | CHAR(36)    |
| essay_text       | TEXT        |
| criteria_scores  | JSON        |
| word_count       | INT         |
| essay_type       | VARCHAR(20) |

---

## recommended_item

Stores learning recommendations generated after assessment.

| Column            | Type                  |
| ----------------- | --------------------- |
| **PK** id         | CHAR(36)              |
| **FK** result_id  | CHAR(36)              |
| **FK** content_id | CHAR(36)              |
| content_type      | VARCHAR(20)           |
| target_skill      | VARCHAR(50)           |
| skill_gap_size    | DECIMAL               |
| rationale         | VARCHAR(500)          |
| priority_order    | INT                   |
| source            | ENUM('AUTO','MANUAL') |
| overridden_by     | VARCHAR(50)           |
| overridden_at     | DATETIME              |
| created_at        | DATETIME              |

---

## audit_log

Tracks all significant actions in the system.

| Column      | Type                                       |
| ----------- | ------------------------------------------ |
| **PK** id   | CHAR(36)                                   |
| actor_id    | VARCHAR(50)                                |
| actor_type  | ENUM('STUDENT','TEACHER','ADMIN','SYSTEM') |
| action      | VARCHAR(50)                                |
| entity_type | VARCHAR(50)                                |
| entity_id   | CHAR(36)                                   |
| details     | JSON                                       |
| created_at  | DATETIME                                   |

---

## Relationships

| From                | Relationship   | To                  |
| ------------------- | -------------- | ------------------- |
| learning_pathway    | Offers         | assessment_template |
| learning_pathway    | Contains       | course              |
| assessment_template | Defines        | assessment_config   |
| assessment_template | Contains       | template_item       |
| template_item       | References     | assessment_item     |
| course              | Contains       | lesson              |
| course              | Is recommended | recommended_item    |
| lesson              | Is recommended | recommended_item    |
| assessment_template | Instantiates   | assigned_assessment |
| assigned_assessment | Is attempted   | assessment_session  |
| assessment_session  | Generates      | assessment_response |
| assessment_response | Answers        | assessment_item     |
| assessment_session  | Produces       | result              |
| result              | Extends to     | placement_result    |
| result              | Extends to     | speaking_result     |
| result              | Extends to     | writing_result      |
| result              | Generates      | recommended_item    |

---

## Indexes

| Table               | Index Name                           | Columns                |
| ------------------- | ------------------------------------ | ---------------------- |
| assigned_assessment | ix_assigned_assessment_test_taker_id | test_taker_id          |
| assigned_assessment | ix_assigned_assessment_status        | status                 |
| audit_log           | ix_audit_log_actor_id                | actor_id               |
| audit_log           | ix_audit_log_entity                  | entity_type, entity_id |
| audit_log           | ix_audit_log_created_at              | created_at             |
