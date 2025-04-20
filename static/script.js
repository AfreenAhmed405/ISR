// INDEX

function showSuggestions() {
    const type = document.getElementById("report-type").value;
    const guidance = {
      blood: ["Hemoglobin levels", "Liver enzymes (ALT/AST)", "Kidney function markers"],
      radiology: ["Scan type", "Findings (e.g., opacity, lesion)", "Impressions"],
      discharge: ["Diagnosis", "Medication instructions", "Follow-up recommendations"],
      lab: ["Chemical levels", "Pathology results", "Reference ranges"],
      other: ["Custom info based on report content"]
    };
    const target = document.getElementById("report-guidance");
    if (type && guidance[type]) {
      target.innerHTML = `<div class="guidance-box"><strong>Typically includes:</strong><ul>${guidance[type].map(x => `<li>${x}</li>`).join('')}</ul></div>`;
    } else {
      target.innerHTML = "";
    }
  }

  function previewImages(event) {
    const previewContainer = document.getElementById("image-preview");
    const fileInfo = document.getElementById("image-info");
    previewContainer.innerHTML = "";
    const files = event.target.files;
    let info = "";

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const img = document.createElement("img");
      img.src = URL.createObjectURL(file);
      img.className = "thumb";
      previewContainer.appendChild(img);
      info += `${file.name} (${Math.round(file.size / 1024)} KB)<br>`;
    }

    fileInfo.innerHTML = info;
  }

  function showFileName(event) {
    const file = event.target.files[0];
    const fileDetails = document.getElementById("pdf-info");
    if (file) {
      fileDetails.innerHTML = `${file.name} (${Math.round(file.size / 1024)} KB)`;
    }
  }

  function resetForm() {
    document.getElementById("upload-form").reset();
    document.getElementById("report-guidance").innerHTML = "";
    document.getElementById("pdf-info").innerHTML = "";
    document.getElementById("image-info").innerHTML = "";
    document.getElementById("image-preview").innerHTML = "";
  }

// SUMMARY 

function handleQuestion() {
    const q = document.getElementById("question").value.toLowerCase();
    const answerBox = document.getElementById("answer-box");
    let answer = "I'm not sure about that one — please try rephrasing your question.";

    if (q.includes("vitamin d") && q.includes("level")) {
      answer = "Good levels for Vitamin D are typically 30–100 ng/mL. Yours is below 20, which is considered deficient. Supplementation is usually recommended.";
    } else if (q.includes("vitamin d")) {
      answer = "Vitamin D helps with bone strength and immune function. Low levels may cause fatigue, depression, or bone pain.";
    } else if (q.includes("hemoglobin")) {
      answer = "Hemoglobin carries oxygen. Low levels can lead to anemia and cause tiredness, weakness, and dizziness.";
    } else if (q.includes("creatinine")) {
      answer = "Creatinine is a kidney marker. Normal levels like yours suggest healthy kidney function.";
    } else if (q.includes("ldl")) {
      answer = "LDL is the 'bad' cholesterol. Lower is better. Your value (70 mg/dL) is excellent and protective for heart health.";
    } else if (q.includes("alt")) {
      answer = "ALT is a liver enzyme. Yours is in the normal range, so no signs of liver issues were found.";
    }

    answerBox.innerHTML = `<strong>Answer:</strong><br>${answer}`;
    answerBox.style.display = "block";

    // Set example question
    document.getElementById("question").value = "What are the good vitamin d levels?";
}