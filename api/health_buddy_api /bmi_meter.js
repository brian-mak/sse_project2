document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('bmi-form');
    const bmiMeterBar = document.querySelector('.bmi-meter-bar');
    const bmiMeterResult = document.querySelector('.bmi-meter-result');
    const resultContainer = document.querySelector('#result-container');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission behavior

        const height = parseFloat(document.getElementById('height').value);
        const weight = parseFloat(document.getElementById('weight').value);

        // Make a request to the backend to calculate BMI
        fetch('/calculate_bmi', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ height: height, weight: weight })
        })
        .then(response => response.json())
        .then(data => {
            const bmi = data.bmi;
            // Update the BMI meter
            updateBMIMeter(bmi);
            // Display the BMI result
            displayBMIResult(bmi);
        })
        .catch(error => console.error('Error:', error));
    });

    function updateBMIMeter(bmi) {
        // Set the width of the BMI meter bar based on the BMI value
        const meterWidth = Math.min(bmi * 10, 100); // Cap at 100%
        bmiMeterBar.style.transform = `translateX(${meterWidth - 100}%)`;
    }

    function displayBMIResult(bmi) {
        // Display the BMI value below the form
        resultContainer.innerHTML = `BMI: ${bmi.toFixed(2)}`;
    }
});

