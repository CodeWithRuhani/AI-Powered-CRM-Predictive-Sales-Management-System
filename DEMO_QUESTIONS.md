# Demo questions

Use these prompts in the chat after the mandatory profile form. The chat uses Ollama. For actual CRM records, use the documented Swagger endpoints; free-form chat does not silently mutate database records.

## Easy
1. What is a CRM and what problem does this prototype solve?
2. What lead statuses does this application support?
3. Explain lead score versus conversion probability.
4. What information should be recorded after a sales call?
5. How does this application use Ollama?

## Medium
1. A technology company has an 80,000 budget, arrived through a referral and has six interactions. What signals could affect conversion likelihood?
2. Why is OneHotEncoder used for industry and lead source, while StandardScaler is used for numeric values?
3. How does interaction history contribute to lead scoring?
4. A lead is Interested but has not replied for 12 days. Suggest a follow-up action and message.
5. Explain precision, recall, F1-score and ROC-AUC for this classifier.

## Hard
1. The model reports 92% ROC-AUC on synthetic data. Can we claim it will achieve this on real leads? Why?
2. Design a time-based validation strategy and explain target leakage.
3. How would you handle a dataset where only 8% of leads convert?
4. How would you monitor concept drift and recalibrate predicted probabilities?
5. How would you migrate SQLite to PostgreSQL for multiple API workers?
6. What features could be engineered from interactions, and how do you avoid using information recorded after prediction time?

## Recommended demo flow
1. Enter all mandatory profile details; show chat is locked until valid submission.
2. Ask Easy #1 and Medium #5 in the Ollama chat.
3. In `/docs`, create a sales representative using POST `/representatives`.
4. Create a lead using POST `/leads` and assign the representative.
5. Add a Meeting interaction using POST `/interactions`.
6. Generate a prediction using POST `/leads/{id}/score`.
7. Generate follow-up using POST `/followups/recommend?lead_id={id}`.
8. Show GET `/leads/{id}/history`, GET `/analytics`, GET `/ml/metrics`.
9. Answer Hard #1: synthetic evaluation is not proof of real-world performance.
