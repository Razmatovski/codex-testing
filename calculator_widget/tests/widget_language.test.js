const fs = require('fs');
const path = require('path');
const {JSDOM} = require('jsdom');

function flushPromises() {
  return new Promise(resolve => setImmediate(resolve));
}

describe('calculator widget language detection', () => {
  test('selects uk language and PLN currency when browser is uk', async () => {
    const htmlPath = path.join(__dirname, '..', 'index.html');
    const html = fs.readFileSync(htmlPath, 'utf8');
    const dom = new JSDOM(html, {
      runScripts: 'dangerously',
      resources: 'usable',
      url: 'file://' + htmlPath
    });

    Object.defineProperty(dom.window.navigator, 'languages', {
      value: ['uk'],
      configurable: true
    });

    const mockData = {
      settings: { default_language_id: 'en', default_currency_id: 'USD' },
      languages: [
        { id: 'en', name: 'English' },
        { id: 'uk', name: 'Ukrainian' }
      ],
      currencies: [
        { id: 'USD', code: 'USD', symbol: '$', name: 'US Dollar' },
        { id: 'PLN', code: 'PLN', symbol: 'z\u0142', name: 'Polish Zloty' }
      ],
      currency_by_lang: { uk: 'PLN', en: 'USD' },
      units_of_measurement: [],
      categories: [
        {
          id: 1,
          name: 'Cat',
          services: [ { id: 1, name: 'Srv', price: '1.00', unit_id: 1 } ]
        }
      ]
    };

    dom.window.fetch = jest.fn(() => Promise.resolve({
      json: () => Promise.resolve(mockData)
    }));

    await new Promise(res => dom.window.addEventListener('load', res));
    await flushPromises();
    await flushPromises();

    const selects = dom.window.document.querySelectorAll('select');
    const langSelect = selects[0];
    const curSelect = selects[1];

    expect(langSelect.value).toBe('uk');
    expect(curSelect.value).toBe('PLN');
  });
});

