import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from typing import Dict, Optional
import logging
import traceback
from google.api_core.exceptions import ResourceExhausted, Forbidden

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    logger.error("GOOGLE_API_KEY not found in .env file")
    raise ValueError("GOOGLE_API_KEY is required")
logger.info(f"API Key loaded: {API_KEY[:4]}...{API_KEY[-4:]}")

class Agent:
    def __init__(self, role: str, input_data: Optional[Dict] = None):
        self.role = role
        self.input_data = input_data or {}
        self.prompt_template = self.create_prompt_template()
        # Initialize Gemini model via LangChain
        try:
            self.model = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=API_KEY,
                temperature=0.1,
                max_tokens=512,
                top_p=0.9
            )
            logger.info(f"{self.role} model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize {self.role} model: {str(e)}\n{traceback.format_exc()}")
            self.model = None

    def create_prompt_template(self) -> PromptTemplate:
        # Simplified prompts to avoid safety filters
        templates = {
            "GeneralDoctor": PromptTemplate.from_template("""
                You are a medical assistant analyzing patient-reported symptoms. Provide 2-3 possible conditions with brief reasons, using this exact format:
                - Condition 1: [Name] - [Reason]
                - Condition 2: [Name] - [Reason]
                - Condition 3: [Name] - [Reason]
                Input: {symptoms}
            """),
            "Diagnosis": PromptTemplate.from_template("""
                You are a medical assistant reviewing a preliminary assessment. Suggest a likely condition, clinic type, and specialist type, using this exact format:
                - Diagnosis: [Condition] - [Explanation]
                - Recommended Clinic: [Clinic type]
                - Recommended Doctor Type: [Specialist type]
                Input: {preliminary_assessment}
            """),
            "Medication": PromptTemplate.from_template("""
                You are a medical assistant providing treatment options based on a diagnosis. Suggest 2-3 medications with their role, dosage, and schedule, using this exact format:
                - Medication 1: [Name] - Role: [Role] - Dosage: [Dosage] - Schedule: [Schedule]
                - Medication 2: [Name] - Role: [Role] - Dosage: [Dosage] - Schedule: [Schedule]
                - Medication 3: [Name] - Role: [Role] - Dosage: [Dosage] - Schedule: [Schedule]
                Input: {diagnosis}
            """),
            "FollowUp": PromptTemplate.from_template("""
                You are a medical assistant coordinating follow-up care. Suggest 2 follow-up actions and monitoring tips, using this exact format:
                - Follow-Up Action 1: [Action] - [Timeline]
                - Follow-Up Action 2: [Action] - [Timeline]
                - Monitoring for New Issues: [Suggestions]
                Input:
                - Symptoms: {symptoms}
                - Preliminary Assessment: {preliminary_assessment}
                - Diagnosis: {diagnosis}
                - Medications: {medications}
            """)
        }
        return templates[self.role]

    def run(self) -> Optional[str]:
        if not self.model:
            logger.error(f"{self.role} Agent model not initialized")
            return None
        logger.info(f"{self.role} Agent is processing")
        try:
            # Format prompt based on role
            if self.role == "GeneralDoctor":
                if not self.input_data.get("symptoms"):
                    logger.error(f"{self.role} Agent: Missing symptoms")
                    return None
                prompt = self.prompt_template.format(symptoms=self.input_data["symptoms"])
            elif self.role == "Diagnosis":
                if not self.input_data.get("preliminary_assessment"):
                    logger.error(f"{self.role} Agent: Missing preliminary assessment")
                    return None
                prompt = self.prompt_template.format(preliminary_assessment=self.input_data["preliminary_assessment"])
            elif self.role == "Medication":
                if not self.input_data.get("diagnosis"):
                    logger.error(f"{self.role} Agent: Missing diagnosis")
                    return None
                prompt = self.prompt_template.format(diagnosis=self.input_data["diagnosis"])
            elif self.role == "FollowUp":
                required_keys = ["symptoms", "preliminary_assessment", "diagnosis", "medications"]
                if not all(self.input_data.get(key) for key in required_keys):
                    logger.error(f"{self.role} Agent: Missing required inputs")
                    return None
                prompt = self.prompt_template.format(**self.input_data)

            # Debug: Log the prompt
            # logger.debug(f"{self.role} Prompt:\n{prompt}")
            # Invoke model
            response = self.model.invoke(prompt)
            # Extract text from response
            response_text = response.content if hasattr(response, "content") else str(response)
            # Debug: Log raw response
            # logger.debug(f"{self.role} Raw Response:\n{response_text}")
            # Check for safety block
            if not response_text.strip():
                logger.warning(f"{self.role} Agent: Empty response, possibly blocked by safety filters")
                return "Blocked: Response filtered due to content restrictions"
            return response_text
        except ResourceExhausted:
            logger.error(f"{self.role} Agent: Rate limit exceeded\n{traceback.format_exc()}")
            return "Error: Rate limit exceeded, please try again later"
        except Forbidden:
            logger.error(f"{self.role} Agent: API key permission error\n{traceback.format_exc()}")
            return "Error: Invalid API key or insufficient permissions"
        except Exception as e:
            logger.error(f"Error in {self.role} Agent: {str(e)}\n{traceback.format_exc()}")
            return None

class GeneralDoctorAgent(Agent):
    def __init__(self, symptoms: str):
        super().__init__(role="GeneralDoctor", input_data={"symptoms": symptoms})

class DiagnosisAgent(Agent):
    def __init__(self, preliminary_assessment: str):
        super().__init__(role="Diagnosis", input_data={"preliminary_assessment": preliminary_assessment})

class MedicationAgent(Agent):
    def __init__(self, diagnosis: str):
        super().__init__(role="Medication", input_data={"diagnosis": diagnosis})

class FollowUpAgent(Agent):
    def __init__(self, symptoms: str, preliminary_assessment: str, diagnosis: str, medications: str):
        super().__init__(role="FollowUp", input_data={
            "symptoms": symptoms,
            "preliminary_assessment": preliminary_assessment,
            "diagnosis": diagnosis,
            "medications": medications
        })

def run_workflow(symptoms: str) -> Dict[str, str]:
    results = {}
    logger.info("Starting workflow")
    
    # Step 1: General Doctor
    general_doctor = GeneralDoctorAgent(symptoms)
    results["general_doctor"] = general_doctor.run()
    if not results["general_doctor"] or "Error" in results["general_doctor"] or "Blocked" in results["general_doctor"]:
        logger.warning("General Doctor Agent failed. Stopping workflow.")
        return results
    
    # Step 2: Diagnosis
    diagnosis_agent = DiagnosisAgent(results["general_doctor"])
    results["diagnosis"] = diagnosis_agent.run()
    if not results["diagnosis"] or "Error" in results["diagnosis"] or "Blocked" in results["diagnosis"]:
        logger.warning("Diagnosis Agent failed. Stopping workflow.")
        return results
    
    # Step 3: Medication
    medication_agent = MedicationAgent(results["diagnosis"])
    results["medication"] = medication_agent.run()
    if not results["medication"] or "Error" in results["medication"] or "Blocked" in results["medication"]:
        logger.warning("Medication Agent failed. Stopping workflow.")
        return results
    
    # Step 4: Follow-Up
    follow_up_agent = FollowUpAgent(
        symptoms=symptoms,
        preliminary_assessment=results["general_doctor"],
        diagnosis=results["diagnosis"],
        medications=results["medication"]
    )
    results["follow_up"] = follow_up_agent.run()
    
    logger.info("Workflow completed")
    return results

def get_user_input(prompt: str) -> str:
    """Helper function to get and clean user input."""
    return input(prompt).strip()

def main():
    print("=== Medical Workflow Interface ===")
    print("Choose an option:")
    print("1. Run full workflow")
    print("2. Run General Doctor Agent")
    print("3. Run Diagnosis Agent")
    print("4. Run Medication Agent")
    print("5. Run Follow-Up Agent")
    
    choice = get_user_input("Enter your choice (1-5): ")
    
    if choice == "1":
        print("\n=== Running Full Workflow ===")
        symptoms = get_user_input("Enter patient symptoms: ")
        results = run_workflow(symptoms)
        
        print("\nGeneral Doctor Assessment:")
        print(results.get("general_doctor", "No output available"))
        
        print("\nDiagnosis:")
        print(results.get("diagnosis", "No output available"))
        
        print("\nMedication Recommendations:")
        print(results.get("medication", "No output available"))
        
        print("\nFollow-Up Recommendations:")
        print(results.get("follow_up", "No output available"))
    
    elif choice == "2":
        print("\n=== Running General Doctor Agent ===")
        symptoms = get_user_input("Enter patient symptoms: ")
        agent = GeneralDoctorAgent(symptoms)
        result = agent.run()
        print("\nGeneral Doctor Assessment:")
        print(result if result else "No output available")
    
    elif choice == "3":
        print("\n=== Running Diagnosis Agent ===")
        preliminary_assessment = get_user_input("Enter preliminary assessment: ")
        agent = DiagnosisAgent(preliminary_assessment)
        result = agent.run()
        print("\nDiagnosis:")
        print(result if result else "No output available")
    
    elif choice == "4":
        print("\n=== Running Medication Agent ===")
        diagnosis = get_user_input("Enter diagnosis: ")
        agent = MedicationAgent(diagnosis)
        result = agent.run()
        print("\nMedication Recommendations:")
        print(result if result else "No output available")
    
    elif choice == "5":
        print("\n=== Running Follow-Up Agent ===")
        symptoms = get_user_input("Enter patient symptoms: ")
        preliminary_assessment = get_user_input("Enter preliminary assessment: ")
        diagnosis = get_user_input("Enter diagnosis: ")
        medications = get_user_input("Enter medications: ")
        agent = FollowUpAgent(symptoms, preliminary_assessment, diagnosis, medications)
        result = agent.run()
        print("\nFollow-Up Recommendations:")
        print(result if result else "No output available")
    
    else:
        print("Invalid choice. Please select a number between 1 and 5.")

if __name__ == "__main__":
    main()