// INDEX

function showSuggestions() {
    const type = document.getElementById("report-type").value;
    const guidance = {
      blood: ["Hemoglobin levels", "Liver enzymes (ALT/AST)", "Kidney function markers"],
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
document.addEventListener("DOMContentLoaded", function () {
    const askForm = document.getElementById("ask-form");
    const questionInput = document.getElementById("question");
    const answerBox = document.getElementById("answer-box");
    const questionText = document.getElementById("question-text");
    const answerText = document.getElementById("answer-text");
  
    if (askForm) {
      askForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const question = questionInput.value.trim();
        if (!question) return;
  
        fetch("/ask", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          body: `question=${encodeURIComponent(question)}`
        })
        .then(res => res.json())
        .then(data => {
          questionText.innerText = question;
          answerText.innerText = data.answer;
          answerBox.style.display = "block";
          questionInput.value = "";
        })
        .catch(err => {
          console.error("Error fetching answer:", err);
          answerText.innerText = "Sorry, something went wrong. Please try again.";
          answerBox.style.display = "block";
        });
      });
    }
  });

