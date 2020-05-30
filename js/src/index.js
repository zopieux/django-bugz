import React, {useEffect, useState} from 'react';
import ReactDOM from 'react-dom';
import Select from 'react-select';
import chroma from 'chroma-js';

const labelColorRect = ({backgroundColor, borderColor}) => ({
  alignItems: 'center',
  display: 'flex',
  ':before': {
    backgroundColor,
    borderColor,
    borderRadius: 3,
    border: '1px solid',
    content: '" "',
    display: 'block',
    marginRight: 8,
    height: 14,
    width: 14,
  },
});

async function post(url, data) {
  const token = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken'))
    .split('=')[1];
  return await fetch(url, {
    method: 'POST',
    headers: {'content-type': 'application/json', 'X-CSRFToken': token},
    credentials: 'same-origin',
    body: JSON.stringify(data),
  });
}

function useDebounce(value, delay, callback) {
  useEffect(() => {
    const t = setTimeout(() => {
      callback(value);
    }, delay);
    return () => {
      clearTimeout(t);
    }
  }, [value, delay, callback]);
}

function LabelSelect({url, ticket, initial}) {
  const [options, setOptions] = useState();
  const [selection, setSelection] = useState();
  const [canUpdate, setCanUpdate] = useState(false);

  useDebounce(selection, 1500, async function (newLabels) {
    if (!canUpdate) return;
    await post(url, {
      ticket: ticket,
      labels: (newLabels || []).map(e => e.value),
    });
  });

  useEffect( () => {
    async function fetchLabels() {
      const labels = await (await fetch(url)).json();
      const options = labels.map(l => ({
        value: l.pk,
        label: l.name,
        color: l.color,
      }));
      const optionsById = Object.fromEntries(options.map(o => [o.value, o]));
      const selected = initial.map(i => optionsById[i]);
      setOptions(options);
      setSelection(selected);
      setCanUpdate(true);
    }
    fetchLabels();
  }, [url, initial]);

  function getColor({data}) {
    const color = chroma(data.color);
    const textColor = chroma.contrast(color, 'white') > 2 ? 'white' : 'black';
    return {
      backgroundColor: data.color,
      color: textColor,
      borderColor: textColor
    };
  }

  const styles = {
    option: (styles, e) => ({...styles, ...labelColorRect(getColor(e))}),
    multiValue: (styles, e) => ({...styles, ...getColor(e)}),
    multiValueLabel: (styles, e) => ({...styles, color: getColor(e).color}),
  };

  return (
    <Select isMulti
            options={options}
            value={selection}
            onChange={setSelection}
            styles={styles}/>
  );
}

window.bugz = window.bugz || {};
window.bugz.labels = function bugz_tags({url, element}) {
  const initial = element.dataset.labels.split(',').map(e => parseInt(e)).filter(isFinite);
  const ticket = parseInt(element.dataset.ticket);
  ReactDOM.render(<React.StrictMode>
    <LabelSelect url={url} initial={initial} ticket={ticket}/>
  </React.StrictMode>, element);
}