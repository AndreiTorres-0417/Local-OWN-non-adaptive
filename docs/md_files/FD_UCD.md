# Functional Description: Use Case Descriptions

## 4.1 Use Case Name: Create Assessment
**Use Case ID:** UC-01  
**Actors:** Admin  
**Description:** Enables admins to create new assessments.  
**Preconditions:** Admin must be logged in and have access to the system with sufficient permissions.

**Basic Flow:**
1. Admin selects “Create Assessment”.
2. Admin enters details such as title, type, skill coverage, CEFR alignment, learning pathway, and other parameters.
3. System retrieves items from the database.
4. Admin selects items.
5. Admin confirms and saves the assessment.
6. System validates and stores assessment data.

**Postconditions:**
* A new assessment is added to the database and ready for assignment to students.
* The action is logged.

**Alternative Flows:**
*   **Step 4a:**
    *   4a. Admin creates new item with its own parameters.
    *   5a. Item saves in the item bank, which can now be selected.
    *   6a. Go back to Step 4 of Basic Flow.
*   **Anytime:**
    *   Admin cancels the creation process.

**Assumptions:**
* The system is online and accessible.
* The item bank is populated.

**Exceptions:**
* Validation fails (e.g. missing or invalid parameters).

---

## 4.2 Use Case Name: Assign Assessment
**Use Case ID:** UC-02  
**Actors:** Admin  
**Description:** Allow an admin to assign a specific assessment to a student or a group of students.  
**Preconditions:** The admin must be logged in and have sufficient permissions.

**Basic Flow:**
1. The admin selects an assessment.
2. The admin selects the "Assign Assessment" option.
3. The admin selects a student or group of students.
4. The admin confirms the assignment.
5. The system assigns the assessment to the student.

**Postconditions:**
* The assessment is assigned to the student(s).
* The action is logged.

**Assumptions:**
* There are active assessments available in the system.
* There are registered students in the system.

**Exceptions:**
* No active assessments are available.
* The selected student does not exist.

---

## 4.3 Use Case Name: Perform Assessment
**Use Case ID:** UC-03  
**Actors:** Student, Admin  
**Description:** Allows the student to take an English assessment that measures proficiency and CEFR level with three different types of assessment: Placement, Speaking, and Writing. Allows the admin to test/verify the assessment.  
**Preconditions:** The user is logged in and has access to the UpsWing! Platform.

**Basic Flow:**
1. User selects “Perform Assessment” option.
2. System retrieves assigned assessments.
3. Student chooses which assessment to perform.  
   *(Note: All three paths are mutually exclusive)*

   **If the assessment type is “Placement”:**
    *   3a. System initializes placement assessment.
    *   4a. System sends an assessment item.
    *   5a. User answers the assessment item.
    *   6a. System processes the answer.
    *   7a. System checks if completion criteria are met (“max items reached” or “ability estimate stable”). System automatically completes the assessment.
    *   8a. Else, system selects the next item and jumps back to 4a.

   **If the assessment type is “Writing”:**
    *   3b. System initializes writing assessment.
    *   4b. System sends all assessment items.
    *   5b. User types written answers.
    *   6b. User submits the answers.
    *   7b. System processes the answers.

   **If the assessment type is “Speaking”:**
    *   4c. System initializes speaking assessment.
    *   5c. System sends all assessment items.
    *   6c. User speaks each answer into the microphone.
    *   7c. User submits the answers.
    *   8c. System processes the answers.

   **All branches merge:**
    *   8. System stores results and sends a completion message.

**Postconditions:**
* Student’s assessment responses and assessment results are saved.
* Results are ready for recommendation generation.
* The action is logged.

**Alternative Flows:**
*   **If the user exits mid-assessment:**
    1. Student exits mid-assessment.
    2. System saves the state automatically.
    3. Student can resume or restart the assessment. (return to Step 3a/3b/3c of Basic Flow).
*   **From Step 5c -> Step 5d:**
    *   User re-records the audio response. (return to Step 5c of Basic Flow).

**Assumptions:**
* The user has a basic understanding of how to answer items online.
* The user has a working microphone for the “Speaking” type of assessment.
* The system is online and accessible.
* The user has a stable internet connection, especially for submitting "Speaking" answers.

**Exceptions:**
* System fails to detect a working microphone for the “Speaking” assessment.
* User’s internet connection fails during submission of the assessment.
* Assessment items fail to load.
* The “Speaking” or “Writing” submission fails (e.g., file upload error, timeout).

---

## 4.4 Use Case Name: Update Assessment
**Use Case ID:** UC-04  
**Actors:** Admin  
**Description:** Allows the admin to modify assessment details or replace test items.  
**Preconditions:** Admin must be logged in and have access to the system with sufficient permissions.

**Basic Flow:**
1. Admin selects an existing assessment.
2. System retrieves assessment data.
3. Admin clicks the Edit button.
4. Admin modifies fields (title, difficulty, item set, other parameters).
5. Admin saves the changes.
6. System validates and updates assessment data.

**Postconditions:**
* Assessment record updated.
* The action is logged.

**Alternative Flows:**
*   **Step 5a:**
    *   Admin selects “Cancel” and discard any changes.

**Assumptions:**
* The system is online and accessible.
* The assessment being updated is not currently in-progress by any students.

**Exceptions:**
* Validation fails on modified fields.
* Admin attempts to edit an assessment that is actively in-use.
* The selected assessment does not exist.

---

## 4.5 Use Case Name: Archive Assessment
**Use Case ID:** UC-05  
**Actors:** Admin  
**Description:** Enables admins to remove outdated assessments from active use without deletion.  
**Preconditions:** Admin must be logged in and have access to the system with sufficient permissions.

**Basic Flow:**
1. Admin selects an existing assessment.
2. Admin clicks the Archive button.
3. System prompts confirmation.
4. Admin confirms action.
5. System validates assessment.
6. System archives and updates the status as Archived.

**Postconditions:**
* Assessment is marked as Archived and hidden from active lists.
* The action is logged.

**Assumptions:**
* The assessment is outdated, not in use.
* The system is online and accessible.

**Exceptions:**
* Admin attempts to archive an assessment that is assigned or currently in-use.

---

## 4.6 Use Case Name: Review Assessment History
**Use Case ID:** UC-06  
**Actors:** All users  
**Description:** Allows students, admins, and tutors to review a record of assessments of a specific student.  
**Preconditions:** The user is logged in and has access to the UpsWing! platform.

**Basic Flow (Student):**
1. Student selects “Assessment History”.
2. System retrieves records.
3. Student applies filters and sorts.
4. Student reviews History and clicks on a specific Assessment.
5. System sends details about the Assessment.

**Postconditions:**
* Assessment history file was reviewed.
* The action is logged.

**Alternative Flow (Admin or Tutor):**
*   1a. The user selects a Student.
*   2a. Go to Basic Flow Step 1.

**Assumptions:**
* The student has existing history to review.

**Exceptions:**
* No assessment history is found for the student.

---

## 4.7 Use Case Name: Export Assessment History
**Use Case ID:** UC-07  
**Actors:** All users  
**Description:** Allows students, admins, and tutors to export a record of assessments of a specific student.  
**Preconditions:** The user is logged in and has access to the UpsWing! platform.

**Basic Flow (Student):**
1. Student selects “Assessment History”.
2. System retrieves records.
3. Student applies filters.
4. Student clicks Export.
5. System generates file and downloads to local storage.

**Postconditions:**
* Assessment history file is downloaded (CSV or PDF).
* The action is logged.

**Alternative Flow (Admin or Tutor):**
*   1a. The user selects a Student.
*   2a. Go to Basic Flow Step 1.

**Assumptions:**
* The student has existing history to download.
* The user’s device has software capable of reading the file.

**Exceptions:**
* No history found.
* File generation fails.
* File download fails.

---

## 4.8 Use Case Name: Generate Recommendation
**Use Case ID:** UC-08  
**Actors:** Student, Admin  
**Description:** Generates tailored recommendations for students based on the results of their assessment. Allows admin to manually trigger the process.  
**Preconditions:**
* The user is logged in and has access to the UpsWing! platform.
* The student completes an assessment.

**Basic Flow (Student):**
1. System automatically sends results to the recommendation engine.
2. System analyzes results and generates recommendations.
3. System stores recommendations for reviewing.

**Postconditions:**
* Recommendations are generated and stored.
* The action is logged.

**Alternative Flow (Admin):**
1. Admin selects a Student.
2. Admin selects “Assessment History”.
3. Admin selects a specific assessment.
4. Admin clicks “Generate Recommendations” based on configs.
5. System generates recommendations.

**Assumptions:**
* The recommendation engine has appropriate configs.
* The assessment results are valid and sufficient for analysis.

**Exceptions:**
* The recommendation engine fails or times out.
* The results provided are missing or corrupted.

---

## 4.9 Use Case Name: Review Recommendation
**Use Case ID:** UC-09  
**Actors:** All users  
**Description:** Allows students, admins, and tutors to review recommendations for a specific student.  
**Preconditions:** The user is logged in and has access to the UpsWing! platform.

**Basic Flow (Student):**
1. Student selects “Assessment History”.
2. Student selects a specific assessment.
3. System retrieves assessment details.
4. Student selects “Recommendations”.
5. System retrieves recommendations.
6. Students may review details.

**Postconditions:**
* Recommendations have been retrieved.
* The action is logged.

**Alternative Flow (Admin or Tutor):**
*   1a. The user selects a Student.
*   2a. Go to Basic Flow Step 1.

**Assumptions:**
* Recommendations have been generated for the student.

**Exceptions:**
* No recommendations are found for the student.

---

## 4.10 Use Case Name: Override Recommendation
**Use Case ID:** UC-10  
**Actors:** Admin  
**Description:** Allows admins to adjust or manually override automatically generated recommendations.  
**Preconditions:**
* The admin is logged in and has access to the UpsWing! Platform.
* The courses and lessons list is populated.

**Basic Flow:**
1. Admin selects a Student.
2. Admin selects “Assessment History”.
3. Admin selects a specific assessment.
4. System retrieves assessment details.
5. Admin selects “Recommendations”.
6. Admin clicks “Override Recommendations”.
7. System sends a list of course/lessons.
8. Admin manually inputs recommended items or edits items.
9. System replaces the old recommendations with the manual override.

**Postconditions:**
* Manual recommendations replace the automatic recommendations and are stored.
* The action is logged.

**Assumptions:**
* The admin has the pedagogical knowledge to make an appropriate manual recommendation.

**Exceptions:**
* The manual items selected by the admin are invalid, non-existent, or incompatible.
* The admin attempts to save an empty recommendation list.

---

## 4.11 Use Case Name: Review Real-Time Progress Report
**Use Case ID:** UC-11  
**Actors:** All users  
**Description:** Allows students, admins, and tutors to view real-time progress report of a specific student.  
**Preconditions:** The user is logged in and has access to the UpsWing! platform.

**Basic Flow (Student):**
1. Student selects “Progress Report”.
2. System retrieves data and generates analytics.
3. System sends the analytics and trends.
4. Student can view their progress report.
5. Student may apply filters to the report.

**Postconditions:**
* The Progress Report page can be viewed and analytics have been generated.
* The action is logged.

**Alternative Flow (Admin or Tutor):**
*   1a. The user selects a Student.
*   2a. Go to Basic Flow Step 1.

**Assumptions:**
* The student has completed at least one assessment and has gotten a result.
* The analytics engine is configured and running.

**Exceptions:**
* Analytics generation fails or times out.
* No data is found for the student.

---

## 4.12 Use Case Name: Export Progress Report
**Use Case ID:** UC-12  
**Actors:** All users  
**Description:** Allows students, admins, and tutors to export a real-time progress report of a specific student.  
**Preconditions:** The user is logged in and has access to the UpsWing! platform.

**Basic Flow (Student):**
1. Student selects “Progress Report”.
2. System retrieves data and generates analytics.
3. System sends the analytics and trends.
4. Student may apply filters to the report.
5. Student clicks Export.
6. System generates file and downloads to local storage.

**Postconditions:**
* Progress Report file is downloaded (CSV or PDF).
* The action is logged.

**Alternative Flow (Admin or Tutor):**
*   1a. The user selects a Student.
*   2a. Go to Basic Flow Step 1.

**Assumptions:**
* The student has completed at least one assessment and has gotten a result.
* The analytics engine is configured and running.



   **Exceptions:**

* Analytics generation fails or times out.

* No data is found for the student.

* File generation fails.

* File download fails.



---



## 4.13 Use Case Name: Manage Learning Content

**Use Case ID:** UC-13  

**Actors:** Admin  

**Description:** Enables admins to create and modify the courses and lessons used for recommendations.  

**Preconditions:** Admin must be logged in and have access to the system with sufficient permissions.



**Basic Flow:**

1. Admin selects "Manage Learning Content".

2. Admin selects "Create New" or selects an existing item to edit.

3. Admin enters or modifies details such as title, type (Course/Lesson), CEFR level, and skill focus.

4. Admin saves the content.

5. System validates and stores the learning content.



**Postconditions:**

* Learning content is added or updated in the library.

* Content is available for recommendations.

* The action is logged.



**Alternative Flows:**

*   **Step 4a:**

    *   Admin cancels the operation and discards changes.



**Assumptions:**

* The system is online and accessible.



**Exceptions:**

* Validation fails (e.g. missing required fields).
