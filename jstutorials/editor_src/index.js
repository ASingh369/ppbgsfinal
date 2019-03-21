/* global $ */

// I am so sorry that you're reading my code

// if you're looking for bad code
// please look at modals.js
// bring a 20 meter stick with you

import { curry } from 'ramda';
import store from './redux/store.js';
import {
  fetchExercise,
  setCoins,
  setHintsUsed,
  setHtmlCode,
  setJsCode,
} from './redux/actions.js';
import './splitHandler.js';
import './modals.js';
import './subscriptions.js';
import { html, js } from './codeEditor.js';
import { runCode } from './codeRunner.js';
import { toFormData } from './utils.js';

// -- Onload dispatch -----------------------------------------------

store.dispatch(setCoins($('#coins').html()));
store.dispatch(setHintsUsed($('#hints-used').html()));
store.dispatch(fetchExercise('/static/exercises/array_flatten.yaml'));

// -- Handle code change --------------------------------------------

let timer;

const handleChange = curry((action, cm) => {
  store.dispatch(action(cm.getValue()));
  clearTimeout(timer);
  timer = setTimeout(runCode, 1000);
});

js.on('change', handleChange(setJsCode));
html.on('change', handleChange(setHtmlCode));

// -- Settings ------------------------------------------------------

$('#reset-html-button').click(() => html.setValue(store.getState().exercise.html));
$('#reset-js-button').click(() => js.setValue(store.getState().exercise.js));

// -- Submit code ---------------------------------------------------

$('#submit-results-button').click(() => {
  const { errorCount, exercise } = store.getState();
  const threshold = exercise.test.errorThreshold;

  fetch('/topics/topic/result', {
    method: 'post',
    headers: {
      'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val(),
    },
    body: toFormData({
      topic_name: $('#topic-name').html(),
      challenge_id: $('#task-id').html(),
      grade: Math.max(threshold - errorCount, 0) / threshold,
      errors: errorCount,
    }),
  });
});
