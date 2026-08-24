import streamlit as st
from groq import Groq 
import pypdf
from logsnag import LogSnag

log_client = LogSnag(token=st.secrets["LOGSNAG_TOKEN"], project="vetly-ai")
log_client.track(channel="visits", event="New Visit")
st.set_page_config(page_title="Vetly AI", page_icon="🎯", layout="wide")
st.title("🎯 Vetly AI")
st.subheader("Advanced Technical Evaluation System & Executive Interview Guide Generator")

try:
    client = Groq(api_key=st.secrets["API_e"])
except Exception as e:
    st.error("Tactical Error: The secret variable API_e is not defined in Secrets!")
    st.stop()

def extract_text_from_pdf(pdf_file):
    try:
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except:
        return ""

st.sidebar.header("🛠️ Interview Evaluation Criteria")
job_description = st.sidebar.text_area("Target Job Description Requirements:", 
                                       placeholder="Enter the required tasks and experiences for the job here...")

num_questions = st.sidebar.slider("Number of questions required per candidate:", min_value=1, max_value=10, value=3)
difficulty_level = st.sidebar.selectbox("Technical Questions Depth Level:", 
                                         ["Basic and progressive evaluation", "Intermediate evaluation to test understanding", "Advanced and deeply technical evaluation"])

if "cv_count" not in st.session_state:
    st.session_state.cv_count = 1

st.write("### 👥 Target Candidates Resumes")
candidates_data = []

for i in range(st.session_state.cv_count):
    col1, col2 = st.columns(2)
    with col1:
        c_name = st.text_input(f"Candidate Name #{i+1}", value=f"Candidate {i+1}", key=f"name_{i}")
    with col2:
        c_file = st.file_uploader(f"Upload PDF file for Candidate #{i+1}", type=["pdf"], key=f"file_{i}")
    candidates_data.append({"name": c_name, "file": c_file})
    st.divider()

if st.button("➕ Add Another Candidate for Cross-Interview"):
    st.session_state.cv_count += 1
    st.rerun()

if st.button("🔥 Engineer Executive Interview Guide"):
    if not job_description:
        st.warning("Please enter the job description first in the sidebar.")
    else:
        st.write("### 🎯 Ready Hidden Questions Guide for the Manager:")
        
        system_instruction = """
        You are a Senior Technical Recruitment Consultant and Technical Screening Lead at top global companies. Your task is to accurately analyze the resume, compare it against the job description, and extract deep, strategic technical questions to uncover the candidate's true expertise.
        You must format your output directly as fully enclosed HTML code with a clean card design that supports English left-to-right (LTR) layout.
        
        Use this exact structure for each candidate and print it as ready HTML code without writing any introductory text outside it:
        <div style="background-color: #f8f9fa; border-left: 5px solid #007bff; padding: 20px; border-radius: 5px; margin-bottom: 25px; direction: ltr; text-align: left; font-family: sans-serif; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
           <h3 style="color: #007bff; font-size: 22px; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #dee2e6; padding-bottom: 5px;">👤 Candidate: [Candidate Name]</h3>
           
           <div style="background-color: #ffffff; padding: 12px; border-radius: 4px; margin-bottom: 10px; border: 1px solid #e9ecef;">
               <p style="font-weight: bold; color: #212529; margin-bottom: 5px; font-size: 16px;">❓ Question [Number]: [Advanced Technical Question Text]</p>
               <p style="color: #28a745; font-weight: 500; font-size: 15px; font-style: italic;">💡 Expected Ideal Answer: [Decisive and deep technical response]</p>
           </div>
        </div>
        """
        
        for person in candidates_data:
            if person["file"] is not None:
                with st.spinner(f"Parsing PDF and engineering reports for {person['name']}..."):
                    cv_text = extract_text_from_pdf(person["file"])
                    
                    if not cv_text:
                        st.error(f"Failed to extract text from {person['name']}'s file.")
                        continue
                    
                    user_instruction = f"""
                    Generate ({num_questions}) advanced technical questions with a level of ({difficulty_level}) for the candidate ({person['name']}).
                    Based on the resume text extracted from the PDF: {cv_text}
                    And the job requirements: {job_description}
                    
                    Remember: Strictly format the output in the structured HTML code mentioned in the system instructions, and do not write any other text outside the HTML tags.
                    """
                    
                    chat_completion = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_instruction}
                        ],
                        temperature=0.1
                    )
                    
                    html_content = chat_completion.choices[0].message.content
                    st.markdown(html_content, unsafe_allow_html=True)
                    
        st.success("Technical evaluation generated successfully! You can now press (Ctrl + P) to print the guide or save it as a cleanly formatted PDF directly from your browser!")
