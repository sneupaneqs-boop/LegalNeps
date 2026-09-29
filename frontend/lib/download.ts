// Triggers a browser download for in-memory data (DOCX blobs, .ics text).
export function saveBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.style.display = "none";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  // give the browser a moment to start the download before releasing the URL
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
}
