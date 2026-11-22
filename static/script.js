const API_ENDPOINT = 'http://localhost:8000/classify'; // Update to match your backend URL

const FEATURE_KEYS = [
    "Area",
    "Perimeter",
    "Major_Axis_Length",
    "Minor_Axis_Length",
    "Eccentricity",
    "Convex_Area",
    "Extent",
];

const tableBody = document.getElementById('table-body');
const addRowBtn = document.getElementById('add-row-btn');
const classifyBtn = document.getElementById('classify-btn');
const statusDiv = document.getElementById('status');
const resultBox = document.getElementById('result-box');

function showError(err) {
    errorText.textContent = err;
    errorPopup.showModal();
}

// Creates and appends a new row with 7 numeric inputs
function addRow(defaultValues = []) {
    const row = document.createElement('tr');

    FEATURE_KEYS.forEach((key, index) => {
        const td = document.createElement('td');
        const input = document.createElement('input');
        input.type = 'number';
        input.step = 'any';
        input.required = true;
        input.name = key;
        input.placeholder = '0.0';

        if (defaultValues[index] !== undefined) {
            input.value = defaultValues[index];
        }

        td.appendChild(input);
        row.appendChild(td);
    });

    // Cell for remove button
    const actionTd = document.createElement('td');
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'remove-btn';
    removeBtn.textContent = 'Удалить';
    removeBtn.addEventListener('click', () => {
        row.remove();
    });
    actionTd.appendChild(removeBtn);
    row.appendChild(actionTd);

    tableBody.appendChild(row);
}

// Calculates column averages across all rows and sends a single POST request
async function classifyAverage() {
    const rows = Array.from(tableBody.querySelectorAll('tr'));

    if (rows.length === 0) {
        showError('Добавьте хотя бы одну запись');
        return;
    }

    // Initialize sums for all 7 parameters
    const sums = {};
    FEATURE_KEYS.forEach(key => {
        sums[key] = 0;
    });

    // Validate inputs and accumulate column sums
    for (const row of rows) {
        const inputs = row.querySelectorAll('input');

        for (const input of inputs) {
            const val = parseFloat(input.value);
            if (Number.isNaN(val)) {
                showError('Впишите значения всех параметров для каждой записи')
                errorPopup.showModal();
                return;
            }
            sums[input.name] += val;
        }
    }

    // Compute averages for the single data entry
    const averagesPayload = {};
    FEATURE_KEYS.forEach(key => {
        averagesPayload[key] = sums[key] / rows.length;
    });

    try {
        const response = await fetch('/classify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(averagesPayload)
        });

        if (!response.ok) {
            throw new Error(`Server responded with status ${response.status}`);
        }

        const data = await response.json();

        riceType.textContent = data.prediction;
        predictPercents.textContent = `${data.probability}%`
        popup.showModal();
    } catch (error) {
        console.error('Classification error:', error);
        showError(`Error: ${error.message}`);
    } finally {
        classifyBtn.disabled = false;
    }
}

addRowBtn.addEventListener('click', () => addRow());
classifyBtn.addEventListener('click', classifyAverage);

// Initialize with one empty row on page load
addRow();

const uploadBtn = document.getElementById('uploadBtn');

// 2. Listen for when a file is selected
uploadBtn.addEventListener('change', (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();

  // 3. Read the file content once loaded
  reader.onload = (e) => {
    const text = e.target.result;
    const parsedData = parseCSV(text);
    for (const row of parsedData) {
        addRow(row)
    }
  };

  reader.readAsText(file);

  // Reset input so the same file can be selected again if needed
  uploadBtn.value = '';
});

// 4. Parse text into rows of 7 numbers
function parseCSV(csvText) {
  // Split by line breaks (handles both Windows \r\n and Unix \n) and remove empty lines
  const lines = csvText.trim().split(/\r?\n/).filter(line => line.trim() !== '');
  const result = [];

  lines.forEach((line, index) => {
    // Split by comma and convert each cell to a Number
    const row = line.split(',').map(cell => Number(cell.trim()));

    // Check if the row has 7 columns and all values are valid numbers
    // (This automatically skips a text header row if one exists)
    if (row.length === 7 && row.every(val => !isNaN(val))) {
      result.push(row);
    } else {
      console.warn(`Skipped row ${index + 1}:`, line);
    }
  });

  return result;
}
