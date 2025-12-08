import csv
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.persistence.connection import get_session
from app.infrastructure.persistence.models.assessment import (
    AssessmentItem,
    AssessmentConfig,
    AssessmentTemplate,
    AssessmentType,
    TemplateItem,
    AssignedAssessment,
    AssignmentStatus,
    TestTakerType,
)
from app.infrastructure.persistence.models.learning import LearningPathway


async def seed_database():
    """Seed the database with initial data from items.csv and default configurations."""
    print("Starting database seeding...")
    
    async for session in get_session():
        print("Session established...")
        
        await seed_learning_pathways(session)
        await session.flush()
        
        await seed_assessment_items(session)
        await session.flush()
        
        await seed_assessment_templates(session)
        await session.flush()
        
        await seed_template_items(session)
        await session.flush()
        
        await seed_assessment_configs(session)
        await session.flush()
        
        await seed_assigned_assessments(session)
        await session.commit()
        
        print("Database seeding completed successfully!")


async def seed_learning_pathways(session: AsyncSession):
    """Seed default learning pathways."""
    pathways = [
        {"name": "General", "description": "General English Assessment"},
        {"name": "Academic", "description": "Academic English Assessment"},
        {"name": "Career", "description": "Career English Assessment"},
        {"name": "Life & Social", "description": "Life and Social English Assessment"},
    ]
    
    for pathway_data in pathways:
        result = await session.execute(
            select(LearningPathway).where(LearningPathway.name == pathway_data["name"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            pathway = LearningPathway(
                id=str(uuid.uuid4()),
                name=pathway_data["name"],
                description=pathway_data["description"],
                is_active=True
            )
            session.add(pathway)
            print(f"Added learning pathway: {pathway_data['name']}")
        else:
            print(f"Learning pathway already exists: {pathway_data['name']}")


async def seed_assessment_items(session: AsyncSession):
    """Seed assessment items from the items.csv file."""
    print("Starting to seed assessment items from CSV...")
    
    import ast
    
    with open('items.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            result = await session.execute(
                select(AssessmentItem).where(AssessmentItem.id == row['id'])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                options_str = row['options'].strip()
                options = ast.literal_eval(options_str)
                
                content = {
                    'item': row['question'],
                    'options': options,
                    'instruction': '',
                    'correct_answer': row['correct_answer']
                }
                
                item = AssessmentItem(
                    id=row['id'],
                    content=content,
                    item_type="multiple_choice",
                    skill_area=[row['skill_area']],
                    target_proficiency_level=row['cefr_level'],
                    parameters={
                        'difficulty': float(row['difficulty']),
                        'discrimination': float(row['discrimination']),
                        'guessing': float(row['guessing'])
                    },
                    is_active=True
                )
                
                session.add(item)
                print(f"Added assessment item: {row['question'][:50]}...")
            else:
                print(f"Assessment item already exists: {row['id']}")
    
    print("Completed seeding assessment items from CSV")


async def seed_assessment_templates(session: AsyncSession):
    """Seed default assessment templates."""
    pathway_result = await session.execute(
        select(LearningPathway).where(LearningPathway.name == "General")
    )
    general_pathway = pathway_result.scalar_one_or_none()
    
    if not general_pathway:
        print("Warning: General pathway not found, cannot create templates")
        return
    
    templates = [
        {
            "name": "General Placement Test",
            "assessment_type": AssessmentType.PLACEMENT,
            "rubric": {
                "proficiency_levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
                "scoring_method": "IRT",
                "description": "Adaptive placement test using Item Response Theory"
            },
            "meta": {
                "duration_minutes": 30,
                "instructions": "Answer each question to the best of your ability."
            }
        }
    ]
    
    for template_data in templates:
        result = await session.execute(
            select(AssessmentTemplate).where(AssessmentTemplate.name == template_data["name"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            template = AssessmentTemplate(
                id=str(uuid.uuid4()),
                learning_pathway_id=general_pathway.id,
                name=template_data["name"],
                assessment_type=template_data["assessment_type"],
                rubric=template_data["rubric"],
                meta=template_data["meta"],
                version=1,
                is_active=True
            )
            session.add(template)
            print(f"Added assessment template: {template_data['name']}")
        else:
            print(f"Assessment template already exists: {template_data['name']}")


async def seed_template_items(session: AsyncSession):
    """Seed template_item junction table linking templates to items."""
    
    template_result = await session.execute(
        select(AssessmentTemplate).where(AssessmentTemplate.name == "General Placement Test")
    )
    placement_template = template_result.scalar_one_or_none()
    
    if not placement_template:
        print("Warning: Placement template not found, cannot link items")
        return
    
    items_result = await session.execute(select(AssessmentItem))
    all_items = items_result.scalars().all()
    
    if not all_items:
        print("Warning: No assessment items found to link")
        return
    
    existing_result = await session.execute(
        select(TemplateItem).where(TemplateItem.template_id == placement_template.id)
    )
    existing_links = existing_result.scalars().all()
    existing_item_ids = {link.item_id for link in existing_links}
    
    added_count = 0
    for item in all_items:
        if item.id not in existing_item_ids:
            template_item = TemplateItem(
                id=str(uuid.uuid4()),
                template_id=placement_template.id,
                item_id=item.id,
                item_order=None, 
                item_meta=None
            )
            session.add(template_item)
            added_count += 1
    
    if added_count > 0:
        print(f"Linked {added_count} items to placement template")
    else:
        print("Template items already linked")


async def seed_assessment_configs(session: AsyncSession):
    """Seed assessment configurations linked to templates."""
    
    placement_result = await session.execute(
        select(AssessmentTemplate).where(AssessmentTemplate.name == "General Placement Test")
    )
    placement_template = placement_result.scalar_one_or_none()
    
    if not placement_template:
        print("Warning: Placement template not found, cannot create config")
        return
    
    result = await session.execute(
        select(AssessmentConfig).where(AssessmentConfig.template_id == placement_template.id)
    )
    existing = result.scalar_one_or_none()
    
    if not existing:
        config = AssessmentConfig(
            id=str(uuid.uuid4()),
            template_id=placement_template.id,
            parameters={
                "time_limit_minutes": 30
            },
            adaptive_params={
                "starting_ability": 0.0,
                "min_questions": 5,
                "max_questions": 25,
                "stopping_criterion": {"standard_error": 0.3},
                "skill_areas": ["grammar", "vocabulary", "reading"],
                "proficiency_range": {
                    "A1": {"min": -2.0, "max": -1.0},
                    "A2": {"min": -1.0, "max": -0.5},
                    "B1": {"min": -0.5, "max": 0.0},
                    "B2": {"min": 0.0, "max": 1.0},
                    "C1": {"min": 1.0, "max": 1.5},
                    "C2": {"min": 1.5, "max": 2.0}
                }
            },
            speaking_params=None,
            writing_params=None,
            is_active=True
        )
        session.add(config)
        print("Added placement assessment config")
    else:
        print("Placement assessment config already exists")


async def seed_assigned_assessments(session: AsyncSession):
    """Seed sample assigned assessments for testing."""
    
    template_result = await session.execute(
        select(AssessmentTemplate).where(AssessmentTemplate.name == "General Placement Test")
    )
    placement_template = template_result.scalar_one_or_none()
    
    if not placement_template:
        print("Warning: Placement template not found, cannot create assigned assessments")
        return
    
    test_assignments = [
        {"test_taker_id": "student-001", "id": "assign-001"},
        {"test_taker_id": "student-002", "id": "assign-002"},
        {"test_taker_id": "student-003", "id": "assign-003"},
    ]
    
    for assignment_data in test_assignments:
        result = await session.execute(
            select(AssignedAssessment).where(AssignedAssessment.id == assignment_data["id"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            assigned = AssignedAssessment(
                id=assignment_data["id"],
                template_id=placement_template.id,
                test_taker_id=assignment_data["test_taker_id"],
                test_taker_type=TestTakerType.STUDENT,
                status=AssignmentStatus.PENDING,
            )
            session.add(assigned)
            print(f"Added assigned assessment for: {assignment_data['test_taker_id']}")
        else:
            print(f"Assigned assessment already exists: {assignment_data['id']}")


if __name__ == "__main__":
    asyncio.run(seed_database())
