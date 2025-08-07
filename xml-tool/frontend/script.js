// frontend/script.js
function uploadXML() {
  const fileInput = document.getElementById('xmlFile');
  const file = fileInput.files[0];
  const result = document.getElementById('result');

  if (!file) {
    showMessage("❗ No file selected.", true);
    return;
  }

  if (!file.name.toLowerCase().endsWith(".xml")) {
    showMessage("⚠️ Please upload a valid XML file.", true);
    return;
  }

  const maxSize = 2 * 1024 * 1024;
  if (file.size > maxSize) {
    showMessage("⚠️ File too large! Max size is 2MB.", true);
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  fetch('http://localhost:5000/upload', {
    method: 'POST',
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      if (data.message) {
        showMessage(data.message);  // ✅ Show success message
      } else {
        showMessage(data.error || "Unknown error", true);
      }
    })
    .catch(err => {
      showMessage("❌ Upload failed: " + err.message, true);
    });
}


function showMessage(msg, isError = false) {
  const result = document.getElementById('result');
  result.style.display = "block";
  result.style.color = isError ? "crimson" : "green";
  result.textContent = msg;
}