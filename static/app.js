let quiz = null;
let current_answer = 0;
let max = 0;
let history = {
    score: 0,
    correct: 0,
    wrong: 0
};

const views = [
    document.getElementById('home'),
    document.getElementById('quiz'),
    document.getElementById('history')
];

const userinput = document.getElementById('input');
const minAnswer = document.getElementById('minAnswer');
const maxAnswer = document.getElementById('maxAnswer');
const question = document.getElementById('question');
const score = document.getElementById('score');
const correct = document.getElementById('correct');
const wrong = document.getElementById('wrong');
const table = document.getElementById('table');

ready();
async function ready() {
    let response = await fetch('/data', {mode: 'cors',method: 'GET'});
    let json = await response.json();

    let inner = '';
    Array.from(Object.keys(json)).forEach((k) => {
        inner += `<a onclick="getQuiz('${k}')" class="button">${k}</a>`
    });
    inner += `<a onclick="getHistory()" class="button">HISTORY</a>`
    document.getElementById('home').innerHTML = inner;

    userinput.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
          event.preventDefault();
          Answer();
        }
    }); 
}

function ShowView(id) {
    views.forEach( v => v.style.display = 'none' );
    document.getElementById(id).style.display = '';
}

async function getQuiz(collection) {
    let response = await fetch(`/quiz/${collection}`, {mode: 'cors',method: 'GET'});
    let json = await response.json();
    quiz = json;
    ShowView('quiz');
    history.score = history.wrong = history.correct = current_answer = 0;
    max = Object.keys(quiz['QUESTION_TEXT']).length;
    maxAnswer.innerText = max;
    NextAnswer();
}

async function Answer() {
    let v = userinput.value;
    if(v === quiz.OPTION_1[current_answer -1] || v === quiz.OPTION_2[current_answer -1] || v === quiz.OPTION_3[current_answer -1])
        history.correct++;
    else
        history.wrong++;
    history.score = (history.correct * 100) / max;
    NextAnswer();
}

function NextAnswer() {
    userinput.value = '';
    current_answer++;
    if(current_answer == max+1) {
        saveHistory();
        return;
    }
    minAnswer.innerText = current_answer;
    question.innerText = quiz['QUESTION_TEXT'][current_answer - 1];
    score.innerText = history.score;
    correct.innerText = history.correct;
    wrong.innerText = history.wrong;
    userinput.focus();
}

async function getHistory() {
    let response = await fetch(`/history`, {mode: 'cors',method: 'GET'});
    let json = await response.json();
    ShowView('history');
    RenderHistory(json);
}

async function saveHistory() {
    let h = JSON.stringify(history);
    let response = await fetch(`/history`, {mode: 'cors', method: 'POST', headers:{
        'Content-Type':'application/json',
        'Content-Length': h.length + 1000
    }, body: h});
    let json = await response.json();
    ShowView('history');
    RenderHistory(json);
}

function RenderHistory(data) {
    inner = `
        <tr>
            <th>Score</th>
            <th>Correct</th>
            <th>Wrong</th>
        </tr>
    `;
    data['score'].forEach((v, i) => {
        inner += `
            <tr>
                <td>${v}%</td>
                <td>${data['correct'][i]}</td>
                <td>${data['wrong'][i]}</td>
            </tr>
        `;
    });
    table.innerHTML = inner;
}