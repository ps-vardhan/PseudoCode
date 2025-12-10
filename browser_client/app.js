console.log('Browser client loaded.');

function copyText(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;

    // Check if it's a textarea or a code block
    let textToCopy = "";
    if (el.tagName.toLowerCase() === 'textarea' || el.tagName.toLowerCase() === 'input') {
        textToCopy = el.value;
    } else {
        textToCopy = el.innerText || el.textContent;
    }

    navigator.clipboard.writeText(textToCopy).then(() => {
        console.log(`Copied text from ${elementId}`);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}

function copyCode() {
    copyText('code-output');
}

function autoResize(el) {
    el.style.height = 'auto'; // Reset height
    el.style.height = el.scrollHeight + 'px'; // Set to scroll height
}

function displayCode(code, language = "plaintext") {
    const el = document.getElementById("code-output");
    if (!el) return;

    // Remove old class
    el.className = "";
    el.classList.add("language-" + language);
    el.textContent = code;

    // Apply highlight.js
    hljs.highlightElement(el);
}

function mockGenerate() {
    console.log("Mock Generate Clicked");
    const descInput = document.getElementById("description-input");
    const desc = descInput ? descInput.value.trim() : "";

    if (!desc) {
        displayCode("Please enter a description first.", "plaintext");
        return;
    }

    // TEMP MOCK JSON
    const mockJson = {
        language: "python",
        code:
            `def generate_response(description):
    """
    Mock function generated for:
    ${desc}
    """
    print("This is a generated response based on your input.")
    return True

if __name__ == "__main__":
    generate_response("Test")`
    };

    displayCode(mockJson.code, mockJson.language);
}

function init() {
    const micBtn = document.getElementById('mic-btn');
    const descriptionInput = document.getElementById('description-input');

    // Auto-resize listeners
    if (descriptionInput) {
        descriptionInput.addEventListener('input', () => autoResize(descriptionInput));
    }

    if (micBtn) {
        micBtn.addEventListener('click', () => {
            console.log('Mic button clicked. Voice connection logic is deferred.');

            micBtn.classList.toggle('listening');

            if (micBtn.classList.contains('listening')) {
                setTimeout(() => {
                    descriptionInput.value += " [Listening...]";
                    autoResize(descriptionInput);
                }, 500);
            } else {
                descriptionInput.value = descriptionInput.value.replace(" [Listening...]", "");
                autoResize(descriptionInput);
            }
        });
    }

    // Initial resize
    if (descriptionInput) autoResize(descriptionInput);
}

window.addEventListener('DOMContentLoaded', init);
window.copyText = copyText;
window.copyCode = copyCode;
window.mockGenerate = mockGenerate;
