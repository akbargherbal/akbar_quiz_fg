// const quiz_set = document.getElementById('quiz_set_from_flask')
let quiz_set = document.getElementById('quiz_set_from_flask').textContent
quiz_set = JSON.parse(quiz_set)

let quiz_name = document.getElementById('quiz_name_from_flask').textContent.trim();
console.log(quiz_name)

const start_of_quiz = new Date();
var end_of_quiz;
var duration_of_quiz_minutes; // global variable declarations for duration of quiz in minutes;

console.log(quiz_set)

const quiz_length = quiz_set.length;

const ui_start = document.getElementById('start_game')
const ui_quiz_container = document.getElementById('quiz_container')
const ui_question_text = document.getElementById('question_text')
const ui_quiz_no = document.getElementById('quiz_no')

const ui_correct_answers = document.getElementById('correct_answers')
const ui_wrong_answers = document.getElementById('wrong_answers')
const ui_score = document.getElementById('score')


const ui_answer_text = document.getElementById('answer_area')
const ui_submit_answer = document.getElementById('submit_button')

const ui_progress_bar = document.getElementById('prog_bar')

var quiz_number = 0
var choices;

var correct_answers = 0;
var wrong_answers = 0;
var score = 0;

var progress = 0;


console.log('Language:', `${language}`)
if (language == 'ar') {
    ui_quiz_no.innerText = `السؤال ${quiz_number} من ${quiz_length}`;
    ui_answer_text.placeholder = 'أدخل إجابتك هنا';
    ui_submit_answer.value = 'الإجابة؟';
}



ui_start.addEventListener('click', startGame)
ui_submit_answer.addEventListener('click', submitAnswer)

ui_answer_text.addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.key === "Enter") {
        ui_submit_answer.click();
    }
  });


let someArray = [];

function startGame() {
    console.log('Game Started')
    ui_start.classList.add('hide')
    ui_quiz_container.classList.remove('hide')
    makeQuiz()
}

function gameOver() {
    console.log('Game Over')
    end_of_quiz = new Date();
    duration_of_quiz_minutes = (end_of_quiz - start_of_quiz) / 60000;
    makeForm(someArray, 'post_form_flask_01')
    ui_quiz_container.classList.add('hide')    
}

function makeQuiz() {
    if (quiz_set.length > 0) {
        let currenQuiz = quiz_set.shift();
        quiz_number = quiz_number + 1;

        if (language == 'ar') {
            ui_quiz_no.textContent = `السؤال ${quiz_number} من ${quiz_length}`}
        else {
        ui_quiz_no.textContent = `Question ${quiz_number} of ${quiz_length}`;}
        ui_question_text.textContent = currenQuiz.QUESTION_TEXT;

        choices = [currenQuiz.OPTION_1, currenQuiz.OPTION_2, currenQuiz.OPTION_3]
    } else {gameOver()}
    

}

function submitAnswer() {
    ui_answer_text.classList.remove('answer_correct')
    ui_answer_text.classList.remove('answer_incorrect')
    let answer = ui_answer_text.value
    console.log(`Answer in Text Area: ${answer}`)
    if (choices.includes(answer)) {
        console.log('Correct', `Indeed ${answer} is one of the choices in ${choices}`)
        correct_answers = correct_answers + 1;
    } else {console.log('WRONG;', `Answer ${answer} is not one of the choices in ${choices}`)
            someArray.push(choices[0]) 
            wrong_answers = wrong_answers + 1;}
    score = Math.floor(100 * ((correct_answers)/(correct_answers + wrong_answers)));

    ui_correct_answers.textContent = `Correct Answers: ${correct_answers}`
    ui_wrong_answers.textContent = `Wrong Answers: ${wrong_answers}`
    ui_score.textContent = `Score: ${score}%`
    ui_answer_text.value = ''

    progress = Math.floor(100 * ((correct_answers + wrong_answers) / quiz_length))
    ui_progress_bar.ariaValueNow = `${progress}`
    ui_progress_bar.ariaValueText = `${progress}%`
    ui_progress_bar.style.width = `${progress}%`

    makeQuiz()
}

function makeForm (array_01, form_id) {
    const ui_form_01 = document.getElementById(form_id)
    for (var i = 0; i < array_01.length; i++) {
        var input = document.createElement("input");
        input.type = "hidden";
        input.value = array_01[i];
        input.name = "wrong_answer" + (i+1);
        ui_form_01.appendChild(input);
    }

    var i_quiz_name = document.createElement("input");
    i_quiz_name.type = "hidden";
    i_quiz_name.value = quiz_name;
    i_quiz_name.name = "quiz_name";
    ui_form_01.appendChild(i_quiz_name);
    
    
    var i_quiz_result = document.createElement("input");
    i_quiz_result.type = "hidden";
    i_quiz_result.value = "quiz_result";
    i_quiz_result.name = "quiz_result";
    ui_form_01.appendChild(i_quiz_result);


    var i_quiz_duration = document.createElement("input");
    i_quiz_duration.type = "hidden";
    i_quiz_duration.value = Math.floor(duration_of_quiz_minutes);
    i_quiz_duration.name = "quiz_duration_minutes";
    ui_form_01.appendChild(i_quiz_duration);


    var i_no_wrong = document.createElement("input");
    i_no_wrong.type = "hidden";
    i_no_wrong.value =  wrong_answers;
    i_no_wrong.name = "number_of_wrong_answers";
    ui_form_01.appendChild(i_no_wrong);

    var i_no_correct = document.createElement("input");
    i_no_correct.type = "hidden";
    i_no_correct.value =  correct_answers;
    i_no_correct.name = "number_of_wrong_answers";
    ui_form_01.appendChild(i_no_correct);


    var i_btn = document.createElement("input");
    i_btn.type = "submit";
    i_btn.value = "Submit";
    ui_form_01.appendChild(i_btn);
    ui_form_01.submit();
    console.log('Form Submitted')
}

