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

var LKT_LAYOUT = {
  'id': 'lkt',
  'title': 'Lakota',
  'mappings': {
    ',c': {
      '': '`1234567890-=' +
          '{{g\u0307}}we{{s\u0307}}tyuiop[]\\' +
          'as{{}}{{ŋ}}gh{{h\u0307}}kl;{{\u2019}}' +
          'z{{z\u0307}}{{c\u0307}}{{}}bnm,./'
    },
    's,sc': {
      '': '~!@#$%^&*()_+' +
          '{{G\u0307}}WE{{S\u0307}}TYUIOP{}|' +
          'AS{{}}{{\u014a}}GH{{H\u0307}}KL:"' +
          'Z{{Z\u0307}}{{C\u0307}}{{}}BNM<>?'
    },
    'l,cl': {
      '': '`1234567890-=' +
          'qwertyuiop{}|' +
          'asdfghjkl:"' +
          'zxcvbnm<>?'
    },
    'sl,scl': {
      '': '~!@#$%^&*()_+' +
          'QWERTYUIOP[]\\' +
          'ASDFGHJKL;\'' +
          'ZXCVBNM,./'
    }
  },
  'transform': {
    '^': '^',  // Placeholder
    'an': 'aŋ',
    'aN': 'aŋ',
    'An': 'Aŋ',
    'AN': 'Aŋ',
    'c~': 'č',
    'C~': 'Č',
    'in': 'iŋ',
    'iN': 'iŋ',
    'In': 'Iŋ',
    'IN': 'Iŋ',
  }
};

// Load the layout and inform the keyboard to switch layout if necessary.
google.elements.keyboard.loadme(LKT_LAYOUT);
