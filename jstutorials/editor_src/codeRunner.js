/* global $, Babel */
/* eslint-disable no-console */

import protect from 'loop-protect';
import { nl2br } from './utils.js';

let state = {
  // secret javascript code not shown to the user
  secret: '',
  // a testing 'suite' ran against user code
  codeChecks: {
    setup: '', // run before user code
    run: '', // run after user code
    cleanup: '', // runs last
    has: [], // checks if code contains a pattern
    hasNot: [], // opposite of 'has'
    maxLines: 200, // max number of lines user should code
    errorThreshold: 0, // (errorThreshold - errorCount) / errorThreshold = grade
  },
  errorCount: 0,
};

export const log = x => {
  $('#console-output').append(`<samp>${x}</samp><br />`);
  console.log(x);
};

export const fail = x => {
  state.errorCount++;
  $('#console-output').append(
    `<code><i class="fas fa-times-circle"></i> ${x}</code><br />`,
  );
};

Babel.registerPlugin('loopProtection', protect(200, line => {
  throw new Error(`Possible infinite loop on line ${line}`);
}));

const transform = source => Babel.transform(source, {
  plugins: ['loopProtection'],
}).code;

window.transform = transform;

// write code to the iframe
const writeToFrame = code => {
  const iframeDocument = $('iframe')[0].contentWindow.document;

  iframeDocument.open();
  iframeDocument.write(code);
  iframeDocument.close();
};

const escapeCode = str =>
  str
    .replace(/\\/g, '\\\\') // preserve backslash
    .replace(/[\n\r]/g, '\\n') // escape new lines
    .replace(/'/g, "\\'"); // escape quotes

const testCode = jsCode => {
  // test if code exceeds maxLines
  if (state.codeChecks.maxLines < jsCode.trim().split('\n').length) {
    fail(
      `You must complete this exercise with ${
        state.codeChecks.maxLines
      } lines of JavaScript or less.`,
    );
  }

  // test if code contains certain strings
  state.codeChecks.has.forEach(piece => {
    const re = new RegExp(piece.regex);

    if (!re.test(jsCode)) {
      fail(piece.message);
    }
  });

  // test if code does not contain certain strings
  state.codeChecks.hasNot.forEach(piece => {
    const re = new RegExp(piece.regex);

    if (re.test(jsCode)) {
      fail(piece.message);
    }
  });

  if (state.errorCount === 0) {
    log(
      `<span class="text-success">
        <i class="fas fa-check-circle"></i> Yay! All tests passed!
      </span>`,
    );
  }
};

// run the user's code against some tests
export const runCode = editors => {
  state.errorCount = 0;

  $('#console-output').empty();

  const htmlCode = editors.html.getValue();
  const jsCode = (() => {
    let code = '';
    try {
      code = escapeCode(transform(editors.js.getValue()));
    } catch (e) {
      fail(nl2br(e.message));
    }
    return code;
  })();

  const scriptToRun = `
    {
      ${state.secret}
    }
    {
      ${state.codeChecks.setup}
      {
        try {
          eval('${jsCode}');
        } catch (e) {
          fail(e);
        }
      }
      ${state.codeChecks.run}
      ${state.codeChecks.cleanup}
    }`;

  writeToFrame(`
    ${htmlCode}
    <script>
      {
        const fail = window.parent.fail;
        console.log = window.parent.log;
        ${scriptToRun}
      }
    </script>`);

  testCode(jsCode);

  // show error count on the footer
  $('#error-count-container').html(
    `<span class="${state.errorCount ? 'text-danger' : ''}">
      <i class="fas fa-times-circle"></i> ${state.errorCount} Errors
    </span>`,
  );

  // warn user about errors in modal
  if (state.errorCount) {
    $('#modal-body-optional-info').html(
      `You currently have ${state.errorCount} errors in your JavaScript code!`,
    );
  } else {
    $('#modal-body-optional-info').empty();
  }
};

export const setState = newState => {
  state = { ...state, ...newState };
};

export const getState = () => state;

window.fail = fail;
window.log = log;