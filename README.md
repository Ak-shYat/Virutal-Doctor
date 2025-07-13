Medical Workflow AI Agent
This project implements a modular AI-powered medical workflow system using Python and LangChain to process patient symptoms, generate diagnoses, recommend medications, and coordinate follow-up care through a chain of specialized agents.

Overview
The Medical Workflow AI Agent is designed to simulate a medical consultation pipeline. It uses multiple AI agents, each handling a specific task in the medical process, from symptom analysis to follow-up recommendations. The system supports both running the full workflow and executing individual agents based on user input.
Features

Interactive CLI: Choose to run the full workflow or individual agents via a command-line interface.
Modular Agents: Four specialized agents handle distinct tasks:
General Doctor: Analyzes symptoms and suggests possible conditions.
Diagnosis: Provides a likely diagnosis and recommends clinic/specialist types.
Medication: Suggests medications based on the diagnosis.
Follow-Up: Coordinates follow-up actions and monitoring tips.


Error Handling: Robust logging and error management for API issues, missing inputs, or safety filter blocks.
Extensible: Easily extendable to add new agents or modify prompts.

Tech Stack

Python: Core programming language.
LangChain: Framework for integrating AI models and prompt templates.
Google Generative AI (Gemini-1.5-Flash): Provides AI-driven responses for medical analysis.
python-dotenv: Manages environment variables for secure API key handling.
Logging: Built-in Python logging for debugging and monitoring.

Installation

Clone the repository:git clone https://github.com/your-repo/medical-workflow-ai-agent.git
cd medical-workflow-ai-agent


Install dependencies:


Create a .env file in the project root and add your Google API key:GOOGLE_API_KEY=your_api_key_here


Ensure Python 3.8+ is installed.

Usage
Run the script to start the interactive CLI:
python interactive_app.py

Options

1. Run full workflow: Input patient symptoms to process through all agents (General Doctor → Diagnosis → Medication → Follow-Up).
2. Run General Doctor Agent: Input symptoms to get possible conditions.
3. Run Diagnosis Agent: Input a preliminary assessment to get a diagnosis and recommendations.
4. Run Medication Agent: Input a diagnosis to get medication suggestions.
5. Run Follow-Up Agent: Input symptoms, preliminary assessment, diagnosis, and medications to get follow-up recommendations.

Example:
=== Medical Workflow Interface ===
Choose an option:
1. Run full workflow
2. Run General Doctor Agent
3. Run Diagnosis Agent
4. Run Medication Agent
5. Run Follow-Up Agent
Enter your choice (1-5): 1
Enter patient symptoms: Patient reports yellowing of hair and nails, fatigue, and mild abdominal discomfort.

Project Structure
medical-workflow-ai-agent/
├── interactive_app.py    # Main script with agent classes and workflow   
└── README.md         

Agents

GeneralDoctorAgent: Analyzes patient symptoms and suggests 2-3 possible conditions with reasons.
DiagnosisAgent: Reviews preliminary assessments to provide a likely diagnosis, clinic type, and specialist recommendation.
MedicationAgent: Recommends 2-3 medications with roles, dosages, and schedules based on the diagnosis.
FollowUpAgent: Suggests follow-up actions and monitoring tips based on symptoms, assessment, diagnosis, and medications.

Contributing
Contributions are welcome! Please follow these steps:

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Commit your changes (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a pull request.

License
This project is licensed under the MIT License. See the LICENSE file for details.
