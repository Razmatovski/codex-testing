(function () {
  const API_BASE = '/api/v1';
  const container = document.getElementById('calculator-widget');
  if (!container) return;

  const translations = {
    en: {
      service: 'Service',
      quantity: 'Qty',
      unitPrice: 'Unit price',
      total: 'Total',
      addItem: 'Add item',
      removeSelected: 'Remove selected',
      selectAll: 'Select all',
      grandTotal: 'Grand total',
      send: 'Send email',
      export: 'Export CSV',
      emailPlaceholder: 'your@email',
      clearAll: 'Clear all',
      negativeQuantityError: 'Quantity cannot be negative.'
    },
    ru: {
      service: '\u0423\u0441\u043b\u0443\u0433\u0430',
      quantity: '\u041a\u043e\u043b-\u0432\u043e',
      unitPrice: '\u0426\u0435\u043d\u0430',
      total: '\u0418\u0442\u043e\u0433',
      addItem: '\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c',
      removeSelected: '\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u0435',
      grandTotal: '\u041e\u0431\u0449\u0430\u044f \u0441\u0443\u043c\u043c\u0430',
      send: '\u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c',
      export: 'CSV',
      emailPlaceholder: 'email',
      selectAll: '\u0412\u044b\u0431\u0440\u0430\u0442\u044c \u0432\u0441\u0435',
      clearAll: '\u041e\u0447\u0438\u0441\u0442\u0438\u0442\u044c \u0432\u0441\u0435',
      negativeQuantityError: '\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043d\u0435 \u043c\u043e\u0436\u0435\u0442 \u0431\u044b\u0442\u044c \u043e\u0442\u0440\u0438\u0446\u0430\u0442\u0435\u043b\u044c\u043d\u044b\u043c.'
    },
    pl: {
      service: 'Us\u0142uga',
      quantity: 'Liczba',
      unitPrice: 'Cena jednostkowa',
      total: 'Suma',
      addItem: 'Dodaj pozycj\u0119',
      removeSelected: 'Usu\u0144 zaznaczone',
      grandTotal: 'Suma ca\u0142kowita',
      send: 'Wy\u015blij',
      export: 'Eksportuj CSV',
      emailPlaceholder: 'tw\xf3j email',
      selectAll: 'Zaznacz wszystko',
      clearAll: 'Wyczy\u015b\u0107 wszystko',
      negativeQuantityError: 'Ilo\u015b\u0107 nie mo\u017ce by\u0107 ujemna.'
    },
    uk: {
      service: '\u041F\u043E\u0441\u043B\u0443\u0433\u0430',
      quantity: '\u041A\u0456\u043B\u044C\u043A\u0456\u0441\u0442\u044C',
      unitPrice: '\u0426\u0456\u043D\u0430 \u0437\u0430 \u043E\u0434\u0438\u043D\u0438\u0446\u044E',
      total: '\u0412\u0441\u044C\u043E\u0433\u043E',
      addItem: '\u0414\u043E\u0434\u0430\u0442\u0438',
      removeSelected: '\u0412\u0438\u0434\u0430\u043B\u0438\u0442\u0438 \u043E\u0431\u0440\u0430\u043D\u0435',
      grandTotal: '\u0417\u0430\u0433\u0430\u043B\u044C\u043D\u0430 \u0441\u0443\u043C\u0430',
      send: '\u0412\u0456\u0434\u043F\u0440\u0430\u0432\u0438\u0442\u0438',
      export: 'CSV',
      emailPlaceholder: '\u0442\u0432\u0456\u0439 email',
      selectAll: '\u041e\u0431\u0440\u0430\u0442\u0438 \u0432\u0441\u0435',
      clearAll: '\u041e\u0447\u0438\u0441\u0442\u0438\u0442\u0438 \u0432\u0441\u0435',
      negativeQuantityError: '\u041a\u0456\u043b\u044c\u043a\u0456\u0441\u0442\u044c \u043d\u0435 \u043c\u043e\u0436\u0435 \u0431\u0443\u0442\u0438 \u0432\u0456\u0434\u0454\u043c\u043d\u043e\u044e.'
    }
  };

  const currencyByLang = { pl: 'PLN', en: 'USD', ru: 'USD', uk: 'PLN' };
  if (typeof window !== 'undefined') {
    window.currencyByLang = currencyByLang;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports.currencyByLang = currencyByLang;
  }

  const state = {
    language: 'en',
    currency: 'USD',
    categories: [],
    currencies: [],
    languages: [],
    items: []
  };

  let selectAllChk;

  function t(key) {
    return (translations[state.language] && translations[state.language][key]) || key;
  }

  function createElem(tag, className, text) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text) el.textContent = text;
    return el;
  }

  function getCurrencySymbol(code) {
    const cur = state.currencies.find(c => (c.code || c.id) === code);
    return cur && cur.symbol ? cur.symbol : code;
  }

  function recalc() {
    let grand = 0;
    let hasError = false;
    errorContainer.textContent = '';
    state.items.forEach(item => {
      const qty = parseFloat(item.qty.value) || 0;
      if (qty < 0) {
        hasError = true;
        errorContainer.textContent = t('negativeQuantityError');
      }
      const srvId = item.service.value;
      const srv = findService(srvId);
      if (srv) {
        const total = qty * parseFloat(srv.price);
        item.total.textContent = total.toFixed(2);
        grand += total;
      }
    });
    grandTotalEl.textContent = `${t('grandTotal')}: ${grand.toFixed(2)} ${getCurrencySymbol(state.currency)}`;
  }

  function findService(id) {
    for (const cat of state.categories) {
      for (const srv of cat.services) {
        if (String(srv.id) === String(id)) return srv;
      }
    }
    return null;
  }

  function addRow() {
    const tr = createElem('tr', 'row-enter');
    const tdService = createElem('td');
    const select = createElem('select');
    state.categories.forEach(cat => {
      const optGroup = createElem('optgroup');
      optGroup.label = cat.name;
      cat.services.forEach(srv => {
        const opt = createElem('option');
        opt.value = srv.id;
        opt.textContent = srv.name;
        optGroup.appendChild(opt);
      });
      select.appendChild(optGroup);
    });
    tdService.appendChild(select);

    const tdQty = createElem('td');
    const qtyInput = createElem('input');
    qtyInput.type = 'number';
    qtyInput.min = '0';
    qtyInput.placeholder = t('quantity');
    tdQty.appendChild(qtyInput);

    const tdPrice = createElem('td');
    const priceSpan = createElem('span', 'price');
    tdPrice.appendChild(priceSpan);

    const tdTotal = createElem('td');
    const totalSpan = createElem('span', 'item-total', '0');
    tdTotal.appendChild(totalSpan);

    const tdSelect = createElem('td', 'select-col');
    const selectChk = createElem('input');
    selectChk.type = 'checkbox';
    tdSelect.appendChild(selectChk);

    const tdRemove = createElem('td');
    const removeBtn = createElem('button', 'remove-btn', 'x');
    tdRemove.appendChild(removeBtn);

    tr.appendChild(tdService);
    tr.appendChild(tdQty);
    tr.appendChild(tdPrice);
    tr.appendChild(tdTotal);
    tr.appendChild(tdSelect);
    tr.appendChild(tdRemove);
    tbody.appendChild(tr);
    setTimeout(() => {
      tr.classList.remove('row-enter');
      qtyInput.focus();
    }, 500);


    // data labels for responsive layout
    tdService.setAttribute('data-label-service', t('service'));
    tdQty.setAttribute('data-label-qty', t('quantity'));
    tdPrice.setAttribute('data-label-price', t('unitPrice'));
    tdTotal.setAttribute('data-label-total', t('total'));

    const item = { row: tr, service: select, qty: qtyInput, price: priceSpan, total: totalSpan, select: selectChk };
    state.items.push(item);

    function updatePrice() {
      const srv = findService(select.value);
      priceSpan.textContent = srv ? srv.price : '0';
      recalc();
    }

    select.addEventListener('change', updatePrice);
    qtyInput.addEventListener('input', recalc);
    removeBtn.addEventListener('click', () => {
      tr.classList.add('row-exit');
      setTimeout(() => {
        tbody.removeChild(tr);
        state.items = state.items.filter(i => i !== item);
        recalc();
      }, 500);
    });
    updatePrice();
  }

  function exportCSV() {
    const rows = [
      ['service', 'quantity', 'unit_price', 'total']
    ];
    state.items.forEach(item => {
      const srv = findService(item.service.value);
      if (!srv) return;
      const qty = parseFloat(item.qty.value) || 0;
      const total = qty * parseFloat(srv.price);
      rows.push([srv.name, qty, srv.price, total.toFixed(2)]);
    });
    const csv = rows.map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = createElem('a');
    a.href = url;
    a.download = 'calculation.csv';
    a.click();
    URL.revokeObjectURL(url);
  }

  function removeSelected() {
    const toRemove = state.items.filter(item => item.select && item.select.checked);
    toRemove.forEach(item => {
      item.row.classList.add('row-exit');
    });
    setTimeout(() => {
      toRemove.forEach(item => {
        tbody.removeChild(item.row);
      });
      state.items = state.items.filter(item => !(item.select && item.select.checked));
      recalc();
    }, 500);
  }

  function clearAll() {
    state.items.forEach(item => {
      item.row.classList.add('row-exit');
    });
    setTimeout(() => {
      tbody.innerHTML = '';
      state.items = [];
      recalc();
      addRow();
    }, 500);
  }

  function sendEmail() {
    const email = emailInput.value.trim();
    const items = state.items.map(item => {
      const srv = findService(item.service.value);
      const qty = parseFloat(item.qty.value) || 0;
      const total = qty * parseFloat(srv.price);
      return {
        service_id: srv.id,
        quantity: qty,
        price_per_unit: srv.price,
        item_total_price: total.toFixed(2)
      };
    });
    const grand = items.reduce((acc, it) => acc + parseFloat(it.item_total_price), 0).toFixed(2);
    fetch(API_BASE + '/send-calculation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_email: email,
        language_code: state.language,
        calculation_items: items,
        grand_total_price: grand
      })
    }).then(r => r.json()).then(data => {
      alert(data.message || 'Ok');
    }).catch(() => alert('Error'));
  }

  const errorContainer = createElem('div', 'error-container');
  const table = createElem('table', 'calc-table');
  const thead = createElem('thead');
  const headRow = createElem('tr');
  ['service', 'quantity', 'unitPrice', 'total'].forEach(key => {
    headRow.appendChild(createElem('th', null, t(key)));
  });
  const selectAllTh = createElem('th', 'select-col');
  selectAllChk = createElem('input');
  selectAllChk.type = 'checkbox';
  selectAllTh.appendChild(selectAllChk);
  selectAllChk.addEventListener('change', () => {
    state.items.forEach(item => {
      if (item.select) item.select.checked = selectAllChk.checked;
    });
  });
  headRow.appendChild(selectAllTh);
  headRow.appendChild(createElem('th')); // remove column header
  thead.appendChild(headRow);
  const tbody = createElem('tbody');
  table.appendChild(thead);
  table.appendChild(tbody);

  const controls = createElem('div', 'controls');
  const langSelect = createElem('select', 'minimal-select');
  const currSelect = createElem('select', 'minimal-select');
  controls.appendChild(langSelect);
  controls.appendChild(currSelect);

  const addBtn = createElem('button', 'add-btn', t('addItem'));
  const removeSelectedBtn = createElem('button', 'remove-selected-btn', t('removeSelected'));
  const clearAllBtn = createElem('button', 'clear-all-btn', t('clearAll'));
  const grandTotalEl = createElem('div', 'grand-total');
  const emailInput = createElem('input');
  emailInput.type = 'email';
  emailInput.placeholder = t('emailPlaceholder');
  const sendBtn = createElem('button', 'send-btn', t('send'));
  const exportBtn = createElem('button', 'export-btn', t('export'));

  const exportControls = createElem('div', 'export-controls');
  exportControls.appendChild(emailInput);
  exportControls.appendChild(sendBtn);
  exportControls.appendChild(exportBtn);

  container.appendChild(controls);
  container.appendChild(errorContainer);
  container.appendChild(table);
  container.appendChild(addBtn);
  container.appendChild(removeSelectedBtn);
  container.appendChild(clearAllBtn);
  container.appendChild(grandTotalEl);
  container.appendChild(exportControls);

  addBtn.addEventListener('click', addRow);
  removeSelectedBtn.addEventListener('click', removeSelected);
  clearAllBtn.addEventListener('click', clearAll);
  exportBtn.addEventListener('click', exportCSV);
  sendBtn.addEventListener('click', sendEmail);

  langSelect.addEventListener('change', () => {
    state.language = langSelect.value;
    updateTexts();
  });
  currSelect.addEventListener('change', () => {
    state.currency = currSelect.value;
    recalc();
  });

  function updateTexts() {
    headRow.childNodes[0].textContent = t('service');
    headRow.childNodes[1].textContent = t('quantity');
    headRow.childNodes[2].textContent = t('unitPrice');
    headRow.childNodes[3].textContent = t('total');
    selectAllChk.title = t('selectAll');
    addBtn.textContent = t('addItem');
    removeSelectedBtn.textContent = t('removeSelected');
    clearAllBtn.textContent = t('clearAll');
    grandTotalEl.textContent = `${t('grandTotal')}: 0 ${getCurrencySymbol(state.currency)}`;
    sendBtn.textContent = t('send');
    exportBtn.textContent = t('export');
    emailInput.placeholder = t('emailPlaceholder');
    updateRowLabels();
  }

  function updateRowLabels() {
    state.items.forEach(item => {
      const cells = item.row.children;
      cells[0].setAttribute('data-label-service', t('service'));
      cells[1].setAttribute('data-label-qty', t('quantity'));
      cells[2].setAttribute('data-label-price', t('unitPrice'));
      cells[3].setAttribute('data-label-total', t('total'));
    });
  }

  function populateSelectors() {
    state.languages.forEach(l => {
      const opt = createElem('option');
      opt.value = l.id;
      opt.textContent = l.name;
      langSelect.appendChild(opt);
    });
    langSelect.value = state.language;

    state.currencies.forEach(c => {
      const opt = createElem('option');
      const val = c.code || c.id;
      opt.value = val;
      opt.textContent = c.symbol || val;
      currSelect.appendChild(opt);
    });
    currSelect.value = state.currency;
  }

  function fetchData() {
    fetch(API_BASE + '/calculator-data')
      .then(r => r.json())
      .then(data => {
        state.languages = data.languages;
        state.currencies = data.currencies;
        state.categories = data.categories;

        const fallbackLang = data.settings.default_language_id || 'en';
        const fallbackCur = data.settings.default_currency_id || 'USD';

        const browserLang = ((navigator.languages && navigator.languages[0]) || navigator.language || '').slice(0, 2).toLowerCase();
        if (browserLang && state.languages.some(l => l.id === browserLang)) {
          state.language = browserLang;
        } else {
          state.language = fallbackLang;
        }

        const mappedCur = currencyByLang[browserLang];
        if (mappedCur && state.currencies.some(c => c.code === mappedCur)) {
          state.currency = mappedCur;
        } else {
          state.currency = fallbackCur;
        }

        populateSelectors();
        updateTexts();
        addRow();
      })
      .catch(err => console.error(err));
  }

  fetchData();
})();
