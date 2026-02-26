// Navigation: Hide landing and show form
function showForm() {
    document.getElementById('hero').classList.add('hidden');
    document.getElementById('formSection').classList.remove('hidden');
}

// Handle Form Submission
document.getElementById('churnForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    // Show a loading state on the button
    const submitBtn = e.target.querySelector('button');
    submitBtn.innerText = "Analyzing Data...";
    submitBtn.disabled = true;

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        // 1. Switch Views
        document.getElementById('formSection').classList.add('hidden');
        const resultBox = document.getElementById('resultBox');
        resultBox.classList.remove('hidden');

        // 2. Setup Animation & Status
        const aniBox = document.getElementById('animationContainer');
        const statusTitle = document.getElementById('statusTitle');
        const improveSection = document.getElementById('improvementSection');
        const improveText = document.getElementById('improvementText');

        if (result.churn === 1) {
            // CHURN CASE (Sad Mode)
            aniBox.innerHTML = "😟 📉 🛑";
            aniBox.classList.add('shake-animation'); // Defined in your CSS
            statusTitle.innerText = "⚠️ PREDICTION: CHURN RISK";
            statusTitle.style.color = "#ff4d4d"; // Red
            
            // Show Improvements
            improveSection.classList.remove('hidden');
            improveText.innerText = result.improvement;
        } else {
            // LOYAL CASE (Celebration Mode)
            aniBox.innerHTML = "🎉 🥳 ✨";
            aniBox.classList.remove('shake-animation');
            statusTitle.innerText = "✅ PREDICTION: LOYAL CUSTOMER";
            statusTitle.style.color = "#64ffda"; // Teal
            
            // Hide Improvements for loyal customers
            improveSection.classList.add('hidden');
        }

        // 3. Fill in the Details
        document.getElementById('probText').innerText = `Risk Probability: ${result.probability}`;
        document.getElementById('reasonText').innerText = result.reason;

    } catch (error) {
        console.error("Error:", error);
        alert("Something went wrong with the prediction server.");
    } finally {
        submitBtn.innerText = "Generate Analysis";
        submitBtn.disabled = false;
    }
});

// Reset Function
function restart() {
    window.location.reload();
}