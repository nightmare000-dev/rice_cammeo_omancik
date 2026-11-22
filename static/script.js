const fileInput = document.getElementById("file-input");
const fileName = document.getElementById("file-name");
const output = document.getElementById("output");

const classifyButton = document.getElementById("classify-button");
const clearButton = document.getElementById("clear-button");
const additionalRows = document.getElementById("additional-rows");


// Выбор файла
fileInput.addEventListener("change", function() {

    const file = fileInput.files[0];

    if (file) {
        fileName.textContent = "Выбран файл: " + file.name;
        output.value = "";
    }

});


// Очистка
function clearResults() {

    fileInput.value = "";
    fileName.textContent = "Файл не выбран";
    output.value = "";
    additionalRows.innerHTML = "";

}


// Добавление строки
function addRow() {

    const row = document.createElement("div");

    row.className = "additional-row";

    row.textContent = "Новая строка";

    additionalRows.appendChild(row);

}


// Классификация
async function classifyRice() {

    const file = fileInput.files[0];

    if (!file) {
        output.value = "Сначала выберите CSV-файл.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    output.value = "Выполняется классификация...";

    classifyButton.disabled = true;
    clearButton.disabled = true;

    try {

        const response = await fetch("/classify", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Ошибка сервера");
        }

        let result = `Обработано зёрен: ${data.count}\n\n`;

        data.results.forEach((item, index) => {

            result +=
                `${index + 1}. ${item.Class} — ${item.Confidence}%\n`;

        });

        output.value = result;

    } catch (error) {

        output.value = "Ошибка: " + error.message;

    } finally {

        classifyButton.disabled = false;
        clearButton.disabled = false;

    }

}


// Очистка при обновлении страницы
window.addEventListener("load", clearResults);