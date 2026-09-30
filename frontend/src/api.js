async function request(path, options) {
  const r = await fetch(path, options)
  if (!r.ok) {
    let detail
    try {
      const body = await r.json()
      if (Array.isArray(body.detail) && body.detail.length) {
        const e = body.detail[0]
        const loc = Array.isArray(e.loc) ? e.loc.filter((x) => x !== 'body').join('.') : ''
        detail = `${loc ? loc + ': ' : ''}${e.msg}`
      } else {
        detail = body.detail || JSON.stringify(body)
      }
    } catch {
      detail = await r.text().catch(() => `${r.status} ${r.statusText}`)
    }
    throw new Error(detail)
  }
  return r.json()
}

export function getJSON(path) {
  return request(path)
}
export function postJSON(path, body) {
  return request(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}
export function putJSON(path, body) {
  return request(path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}
