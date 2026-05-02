// =====================
// LOGIN PROTECTION
// =====================
window.onload = () => {
    const user = localStorage.getItem("username");

    // Redirect to login if not authenticated
    if (!user) {
        window.location.href = "login.html";
    } else {
        // Show welcome message if element exists
        const welcome = document.getElementById("welcome");
        if (welcome) {
            welcome.innerHTML = "Welcome, <b>" + user + "</b>";
        }
    }
};

// =====================
// LOGOUT
// =====================
function logout() {
    // Clear all stored session data
    localStorage.clear();

    // Redirect to login page
    window.location.href = "login.html";
}

// =====================
// JOB ROLE → SKILL MAP (UI ONLY)
// =====================
const jobRoleSkillMap = {
    web: ["html", "css", "javascript", "react"],
    frontend: ["html", "css", "javascript", "react"],
    backend: ["python", "java", "sql", "flask", "django"],
    fullstack: ["html", "css", "javascript", "react", "python", "sql"],

    data: ["python", "sql", "data analysis", "machine learning"],
    analyst: ["sql", "data analysis", "python"],
    ml: ["python", "machine learning", "deep learning"],
    ai: ["python", "machine learning", "deep learning", "nlp"],

    software: ["java", "python", "c++", "data structures"],
    cloud: ["aws", "docker", "kubernetes"],
    devops: ["aws", "docker", "kubernetes", "ci/cd"],

    cyber: ["cyber security", "networking", "linux"]
};


// =====================
// APPLY ROLE SKILLS
// =====================
function applyJobRoleSkills() {
    const roleSelect = document.getElementById("jobRole");
    if (!roleSelect) return;

    const role = roleSelect.value;

    // Store selected role for result page recommendations
    localStorage.setItem("selectedRole", role);

    // Uncheck all skills first
    document.querySelectorAll(".skills input").forEach(cb => {
        cb.checked = false;
    });

    // Auto-check skills based on selected role
    if (jobRoleSkillMap[role]) {
        jobRoleSkillMap[role].forEach(skill => {
            const checkbox = document.querySelector(
                `.skills input[value="${skill}"]`
            );
            if (checkbox) checkbox.checked = true;
        });
    }
}

// =====================
// ANALYZE RESUME (API CALL)
// =====================
function analyzeResume() {
    const fileInput = document.getElementById("resume");

    // Safety check
    if (!fileInput || !fileInput.files.length) {
        alert("Please upload a resume file");
        return;
    }

    const file = fileInput.files[0];

    // Collect selected skills
    const selectedSkills = [];
    document.querySelectorAll(".skills input:checked").forEach(cb => {
        selectedSkills.push(cb.value);
    });

    if (selectedSkills.length === 0) {
        alert("Please select a job role or skills");
        return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append("resume", file);
    formData.append("skills", selectedSkills.join(","));

    // Send data to backend
    fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        // Store analysis result for result page
        localStorage.setItem("analysisResult", JSON.stringify(data));

        // Redirect to result page
        window.location.href = "result.html";
    })
    .catch(() => {
        alert("Error analyzing resume");
    });
}
