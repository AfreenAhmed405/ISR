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
