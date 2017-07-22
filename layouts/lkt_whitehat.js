// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Implements AuSIL keyboard for Aṉangu Yolŋu Australian languages.
// Reference: http://learnline.cdu.edu.au/yolngustudies/resourcesKeyboard.html
// http://www.ausil.org.au/node/3719

var LKT_WHITEHAT_LAYOUT = {
  'id': 'lkt_whitehat',
  'title': 'Lakota Whitehat',
  'mappings': {
    '': {
      '': '{{\u0300}}1234567890-=' +
          'qwertyuiop{{\u0304}}{{\u0301}}\\' +
          'asdfghjkl;{{\u2019}}' +
          'zxcvbnm,.{{\u0307}}'
    },
    'c': {
      '': '`12345678{{\u00ab}}{{\u00bb}}-=' +
          'qwertyuiop[]\\' +
          'asdfghjkl;\'' +
          'zxcvbnm,./'
    },
    's': {
      '': '{{\u2018}}!@#$%^&*()_+' +
          'QWERTYUIOP{{\u201c}}{{\u201d}}|' +
          'ASDFGHJKL:"' +
          'ZXCVBNM<>?'
    },
    'sc': {
      '': '~!@#$%^&*{{\u2039}}{{\u203a}}_+' +
          'QWERTYUIOP{}|' +
          'ASDFGHJKL:"' +
          'ZXCVBNM<>?'
    },
    'l,cl': {
      '': '`1234567890-=' +
          'QWERTYUIOP[]\\' +
          'ASDFGHJKL;\'' +
          'ZXCVBNM,./'
    },
    'sl,scl': {
      '': '~!@#$%^&*()_+' +
          'qwertyuiop{}|' +
          'asdfghjkl:"' +
          'zxcvbnm<>?'
    }
  },
  'transform': {
    '^': '^',  // Placeholder
  }
};

// Load the layout and inform the keyboard to switch layout if necessary.
google.elements.keyboard.loadme(LKT_WHITEHAT_LAYOUT);
