// Get references to the table elements
const table = document.getElementById('workout-table');
const timeScaleSelect = document.getElementById('time-scale');

// Initialize the time scale to "week"
let timeScale = "week";

// Get references to the table header cells
const headerCells = table.tHead.rows[0].cells;

// Get references to the time slot cells
const timeSlotCells = [];
for (let i = 0; i < headerCells.length - 1; i++) {
  timeSlotCells.push([]);
  for (let j = 0; j < table.tBodies[0].rows.length; j++) {
    timeSlotCells[i].push(table.tBodies[0].rows[j].cells[i + 1]);
  }
}

// Set up the time scale select element
timeScaleSelect.addEventListener('change', () => {
  timeScale = timeScaleSelect.value;
  updateTable();
});

// Add a workout plan to the specified time slot
function addWorkoutPlan(day, time) {
  const cell = timeSlotCells[time][day];
  const input = document.createElement('input');
  input.type = 'text';
  input.className = 'workout-plan';
  cell.appendChild(input);
}

// Remove the workout plan from the specified time slot
function removeWorkoutPlan(day, time) {
  const cell = timeSlotCells[time][day];
  const input = cell.querySelector('input.workout-plan');
  if (input) {
    cell.removeChild(input);
  }
}

// Update the table to display the appropriate time range based on the selected time scale
function updateTable() {
  // Remove all existing rows except for the header row
  while (table.tBodies[0].rows.length > 1) {
    table.tBodies[0].deleteRow(1);
  }

  // Determine the start and end times based on the selected time scale
  let startTime = 7;
  let endTime = 22;
  if (timeScale === 'week' || timeScale === 'month') {
    startTime = 7;
    endTime = 22;
  } else if (timeScale === 'year') {
    startTime = 0;
    endTime = 24;
  }

  // Add rows for each time slot
  for (let time = startTime; time < endTime; time++) {
    const row = table.tBodies[0].insertRow(-1);

    // Add the time cell
    const timeCell = row.insertCell(0);
    timeCell.textContent = time + ':00';

    // Add cells for each day of the week
    for (let day = 0; day < 7; day++) {
      const cell = row.insertCell(-1);

      // If the time scale is "year", display the month and day
      if (timeScale === 'year') {
        const date = new Date(2023, 0, day * 7 + time + 1);
        cell.textContent = `${date.toLocaleString('default', { month: 'short' })} ${date.getDate()}`;
      }

      // Add a workout plan input if one exists for this time slot
      const input = timeSlotCells[time][day].querySelector('input.workout-plan');
      if (input) {
        cell.appendChild(input);
      }
    }
  }
}

// Initialize the table
updateTable();

