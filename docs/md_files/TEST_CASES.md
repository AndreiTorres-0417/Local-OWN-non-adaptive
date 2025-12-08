# Test Cases

| Test Case ID | Use Case ID | Test Case Name | Test Case Description |
| :--- | :--- | :--- | :--- |
| TC-01 | UC-01 | Admin Creates Valid Assessment (Basic Flow) | Verify the Admin can successfully create a new assessment by providing all valid parameters and item IDs. |
| TC-02 | UC-01 | Admin Creates New Item During Assessment Creation (Alt Flow) | Verify the Admin can successfully create a new item via the alternative flow, save it to the bank, and use its ID in the new assessment. |
| TC-03 | UC-01 | Admin Cancels Assessment Creation (Alt Flow) | Verify that if the Admin invokes the "Cancel" operation, the assessment data is not saved. |
| TC-04 | UC-01 | Admin Creates Assessment with Missing Data (Exception) | Verify the system outputs a validation error and does not save if the Admin tries to create an assessment with missing required parameters. |
| TC-05 | UC-02 | Admin Assigns Assessment to Single Student (Basic Flow) | Verify the Admin can provide an assessment ID and a single student ID to successfully confirm the assignment. |
| TC-06 | UC-02 | Admin Assigns Assessment to Group (Basic Flow) | Verify the Admin can provide an assessment ID and a student group ID to successfully confirm the assignment to all students in that group. |
| TC-07 | UC-02 | Admin Assigns When No Assessments Exist (Exception) | Verify the system outputs an appropriate error message if the Admin tries to assign an assessment but no active assessments are available. |
| TC-08 | UC-02 | Admin Assigns to Non-Existent Student (Exception) | Verify the system outputs an error if the Admin attempts to assign an assessment to a student ID that does not exist. |
| TC-09 | UC-03 | Student Completes Placement Assessment (Basic Flow) | Verify a Student can request and successfully complete a "Placement" assessment, and the results are stored. |
| TC-10 | UC-03 | Student Completes Writing Assessment (Basic Flow) | Verify a Student can request, complete, and submit the data for a "Writing" assessment, and the results are stored. |
| TC-11 | UC-03 | Student Completes Speaking Assessment (Basic Flow) | Verify a Student can request, provide answer data for, and submit a "Speaking" assessment, and the results are stored. |
| TC-12 | UC-03 | Admin Tests an Assessment (Basic Flow) | Verify an Admin can request and execute any assessment type to test/verify its functionality. |
| TC-13 | UC-03 | Student Exits Assessment Mid-Way (Alt Flow) | Verify that if a Student's session terminates mid-assessment, the system automatically saves their state. |
| TC-14 | UC-03 | Student Resumes Assessment (Alt Flow) | Verify a Student can re-initiate an assessment they exited mid-way and resume or restart it. |
| TC-15 | UC-03 | Student Re-records Speaking Answer (Alt Flow) | Verify a Student can invoke the re-record command during a "Speaking" assessment to replace a previous audio response before submission. |
| TC-16 | UC-03 | No Microphone Detected for Speaking Test (Exception) | Verify the system detects the absence of a working microphone (e.g., failed hardware check) and outputs an error when a Student starts a "Speaking" assessment. |
| TC-17 | UC-03 | Internet Failure During Submission (Exception) | Verify the system outputs an error message if the connection fails during the submission process. |
| TC-18 | UC-03 | Assessment Items Fail to Load (Exception) | Verify the system outputs an error message if the assessment items cannot be retrieved from the database. |
| TC-19 | UC-03 | Speaking/Writing Submission Fails (Exception) | Verify the system outputs an error message if the submission fails due to a file processing error or timeout. |
| TC-20 | UC-04 | Admin Edits Assessment Details (Basic Flow) | Verify an Admin can provide an existing assessment ID and modified parameters (e.g., title), and the changes are saved. |
| TC-21 | UC-04 | Admin Cancels Edit Assessment (Alt Flow) | Verify that if an Admin invokes the "Cancel" operation while editing, no changes are saved to the assessment. |
| TC-22 | UC-04 | Admin Edits Assessment with Invalid Data (Exception) | Verify the system outputs a validation error if the Admin tries to save invalid data in a modified parameter. |
| TC-23 | UC-04 | Admin Edits Assessment in Active Use (Exception) | Verify the system prevents an Admin from saving changes to an assessment that is actively in-progress by a student. |
| TC-24 | UC-04 | Admin Edits Non-Existent Assessment (Exception) | Verify the system outputs an error if the Admin attempts to edit an assessment ID that does not exist. |
| TC-25 | UC-05 | Admin Archives an Assessment (Basic Flow) | Verify an Admin can provide an assessment ID, invoke "Archive," and confirm the action, resulting in the assessment status being "Archived". |
| TC-26 | UC-05 | Admin Archives Assessment in Use (Exception) | Verify the system prevents an Admin from archiving an assessment that is currently assigned or in-use by students. |
| TC-27 | UC-06 | Student Reviews Own Assessment History (Basic Flow) | Verify a Student can request "Assessment History" and receive a list of their own completed assessments. |
| TC-28 | UC-06 | Student Filters Assessment History (Basic Flow) | Verify a Student can use filter and sort parameters in their history request, and the returned results are correct. |
| TC-29 | UC-06 | Admin Reviews Student's History (Alt Flow) | Verify an Admin/Tutor can request the assessment history for a specific student ID and receive that student's data. |
| TC-30 | UC-06 | User Reviews History for New Student (Exception) | Verify the system outputs a "No assessment history is found" message when requesting the history of a student who has none. |
| TC-31 | UC-07 | Student Exports Own Assessment History (Basic Flow) | Verify a Student can use filter parameters and invoke "Export" to generate and receive their own assessment history file. |
| TC-32 | UC-07 | Admin Exports Student's History (Alt Flow) | Verify an Admin/Tutor can request an export of a specific student's history and receive the correct file. |
| TC-33 | UC-07 | User Exports Empty History (Exception) | Verify the system outputs a "No history found" message if the user tries to export an empty history report. |
| TC-34 | UC-07 | Export File Generation Fails (Exception) | Verify the system outputs an error message if the file generation process fails on the server. |
| TC-35 | UC-07 | Export File Download Fails (Exception) | Verify the system outputs an error message if the file transmission fails. |
| TC-36 | UC-08 | Automatic Recommendation Generation (Basic Flow) | Verify that after a Student completes an assessment, the system automatically sends results and stores generated recommendations. |
| TC-37 | UC-08 | Admin Manually Triggers Recommendation (Alt Flow) | Verify an Admin can provide a student's assessment ID and manually trigger the "Generate Recommendations" process. |
| TC-38 | UC-08 | Recommendation Engine Fails (Exception) | Verify the system logs an error if the recommendation engine fails or times out during generation. |
| TC-39 | UC-08 | Recommendation from Corrupted Results (Exception) | Verify the system handles an error if the assessment results are missing or corrupted and cannot be analyzed. |
| TC-40 | UC-09 | Student Reviews Own Recommendations (Basic Flow) | Verify a Student can request the recommendations for a completed assessment and receive the associated data. |
| TC-41 | UC-09 | Admin Reviews Student's Recommendations (Alt Flow) | Verify an Admin/Tutor can request the recommendations for a specific student's assessment and receive the data. |
| TC-42 | UC-09 | User Reviews Non-Existent Recommendations (Exception) | Verify the system outputs a "No recommendations are found" message if the user requests recommendations that haven't been generated. |
| TC-43 | UC-10 | Admin Overrides Recommendation (Basic Flow) | Verify an Admin can provide a student's recommendation ID, invoke "Override," submit new items, and save the replacement. |
| TC-44 | UC-10 | Admin Overrides with Invalid Items (Exception) | Verify the system outputs an error if the Admin tries to save an override with item IDs that are invalid or non-existent. |
| TC-45 | UC-10 | Admin Saves Empty Override (Exception) | Verify the system outputs an error and does not save if the Admin attempts to save an empty recommendation list as an override. |
| TC-46 | UC-11 | Student Reviews Own Progress Report (Basic Flow) | Verify a Student can request "Progress Report" and receive their own analytics and trends. |
| TC-47 | UC-11 | Student Filters Progress Report (Basic Flow) | Verify a Student can use filter parameters in their progress report request, and the returned data is correct. |
| TC-48 | UC-11 | Admin Reviews Student's Progress Report (Alt Flow) | Verify an Admin/Tutor can request the real-time progress report for a specific student ID. |
| TC-49 | UC-11 | Analytics Generation Fails (Exception) | Verify the system outputs an error message if the analytics engine fails or times out. |
| TC-50 | UC-11 | User Reviews Report for New Student (Exception) | Verify the system outputs a "No data is found" message when trying to retrieve a report for a student with no assessment results. |
| TC-51 | UC-12 | Student Exports Own Progress Report (Basic Flow) | Verify a Student can request an export of their progress report, using filters, and successfully receive the file. |
| TC-52 | UC-12 | Admin Exports Student's Progress Report (Alt Flow) | Verify an Admin/Tutor can request an export of a specific student's progress report and receive the correct file. |
| TC-53 | UC-12 | Analytics Fail During Export (Exception) | Verify the system outputs an error if the analytics generation fails during the export process. |
| TC-54 | UC-12 | User Exports Report for New Student (Exception) | Verify the system outputs a "No data is found" error if attempting to export a report for a student with no data. |
| TC-55 | UC-12 | Export File Generation Fails (Exception) | Verify the system outputs an error message if the report file generation fails on the server. |
| TC-56 | UC-12 | Export File Download Fails (Exception) | Verify the system outputs an error message if the report file transmission fails. |