function uploadXML() {
  const fileInput = document.getElementById('xmlFile');
  const file = fileInput.files[0];
  const result = document.getElementById('result');

  if (!file) {
    result.textContent = "No file selected.";
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
    console.log("✅ Server response:", data);  // 👈 shows output in DevTools
    result.textContent = data.message || data.error || "Unknown response.";
  })
  .catch(err => {
    console.error("❌ Upload failed:", err);   // 👈 logs any fetch error
    result.textContent = "Upload failed: " + err.message;
  });
}