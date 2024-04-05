document.addEventListener("DOMContentLoaded", function() {
  const copyButton = document.getElementById("copyBtn");
  const shortUrlText = document.getElementById("shortUrl");

  copyButton.addEventListener("click", function() {
    const textToCopy = shortUrlText.innerText;

    navigator.clipboard.writeText(textToCopy)
      .then(function() {
        alert("Link copied to clipboard");
      })
      .catch(function(error) {
        console.error("Failed to copy text: ", error);
      });
  });
});