// frontend/script.js
const API_BASE = "http://127.0.0.1:5000";
const drop = document.getElementById('drop');
const fileInput = document.getElementById('file');
const uploadBtn = document.getElementById('uploadBtn');
const downloadBtn = document.getElementById('downloadBtn');
const msg = document.getElementById('msg');

let selectedFile = null;

function showMessage(text, type='success', persistent=false){
  msg.style.display = 'block';
  msg.className = 'alert mt-3 ' + (type==='error' ? 'alert-danger' : 'alert-success');
  msg.textContent = text;
  if(!persistent){
    setTimeout(()=> { msg.style.display = 'none'; }, 6000);
  }
}

/* Drag & drop */
drop.addEventListener('click', () => fileInput.click());

drop.addEventListener('dragover', (e) => {
  e.preventDefault();
  drop.classList.add('drag');
});
drop.addEventListener('dragleave', (e) => {
  e.preventDefault();
  drop.classList.remove('drag');
});
drop.addEventListener('drop', (e) => {
  e.preventDefault();
  drop.classList.remove('drag');
  const f = e.dataTransfer.files && e.dataTransfer.files[0];
  if (f) {
    fileInput.files = e.dataTransfer.files;
    selectedFile = f;
    drop.querySelector('div[style]')?.textContent && (drop.querySelector('div[style]').textContent = `Selected: ${f.name}`);
  }
});

fileInput.addEventListener('change', (e) => {
  selectedFile = e.target.files[0];
  if (selectedFile) {
    drop.querySelector('div[style]')?.textContent && (drop.querySelector('div[style]').textContent = `Selected: ${selectedFile.name}`);
  }
});

/* Upload */
uploadBtn.addEventListener('click', async () => {
  if (!selectedFile) return showMessage('Please select an XML file first.', 'error');

  if (!selectedFile.name.toLowerCase().endsWith('.xml')){
    return showMessage('Only .xml files allowed', 'error');
  }
  if (selectedFile.size > 5 * 1024 * 1024){
    return showMessage('File too large (max 5MB)', 'error');
  }

  uploadBtn.disabled = true;
  uploadBtn.textContent = 'Uploading...';

  const form = new FormData();
  form.append('file', selectedFile);

  try {
    const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body: form });
    const data = await res.json();
    if (!res.ok) {
      showMessage(data.error || 'Upload failed', 'error');
    } else {
      showMessage(data.message || 'Upload successful', 'success', true);
    }
  } catch (err){
    showMessage('Network error during upload', 'error');
  } finally {
    uploadBtn.disabled = false;
    uploadBtn.textContent = 'Upload & Insert';
  }
});

/* Download */
downloadBtn.addEventListener('click', async () => {
  downloadBtn.disabled = true;
  downloadBtn.textContent = 'Preparing...';
  try {
    const res = await fetch(`${API_BASE}/download-excel`);
    if (!res.ok) {
      const e = await res.json().catch(()=>({error:'Export failed'}));
      showMessage(e.error || 'Export failed', 'error');
      return;
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');

    // attempt filename from headers
    const disposition = res.headers.get('Content-Disposition') || '';
    let filename = 'exported_table.xlsx';
    const m = disposition.match(/filename="?(.+)"?/);
    if (m && m[1]) filename = m[1];

    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    showMessage('Excel downloaded', 'success');
  } catch (err){
    showMessage('Download failed', 'error');
  } finally {
    downloadBtn.disabled = false;
    downloadBtn.textContent = 'Download Excel';
  }
});
