import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import prototypeData from "./prototype-data.js";
import "./styles.css";

const data = prototypeData || window.PROTOTYPE_DATA || { pages: [] };
const labels = data.labels || {};

function routeFromHash(pages) {
  const id = decodeURIComponent(window.location.hash.replace(/^#/, ""));
  return pages.find((page) => page.id === id)?.id || pages[0]?.id || "";
}

function App() {
  const pages = data.pages || [];
  const [activeId, setActiveId] = useState(routeFromHash(pages));
  const [toast, setToast] = useState("");
  const [dialog, setDialog] = useState(null);
  const [formState, setFormState] = useState({});

  useEffect(() => {
    document.documentElement.lang = data.lang || "zh-CN";
    document.title = data.title || "React Prototype";
  }, []);

  useEffect(() => {
    const onHash = () => setActiveId(routeFromHash(pages));
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, [pages]);

  const activePage = useMemo(
    () => pages.find((page) => page.id === activeId) || pages[0],
    [activeId, pages],
  );

  function routeTo(id) {
    if (!id || !pages.some((page) => page.id === id)) return;
    window.location.hash = encodeURIComponent(id);
  }

  function showToast(message) {
    setToast(message || labels.saved || "Saved");
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => setToast(""), 1800);
  }

  function handleAction(action = {}) {
    if (action.target) {
      routeTo(action.target);
      return;
    }
    if (action.dialog) {
      setDialog({ title: action.label || labels.actions || "Action", body: action.dialog });
      return;
    }
    showToast(action.toast || labels.saved || "Saved");
  }

  if (!activePage) {
    return <main className="empty-root">{labels.noPages || "No page data"}</main>;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <p className="eyebrow">{data.kicker || "React Prototype"}</p>
        <h1>{data.title || "React Prototype"}</h1>
        <p className="summary">{data.summary || ""}</p>
        <nav className="route-list" aria-label={labels.pages || "Pages"}>
          {pages.map((page) => (
            <button
              key={page.id}
              type="button"
              className="route-button"
              aria-current={page.id === activePage.id}
              onClick={() => routeTo(page.id)}
            >
              <span>{page.navLabel || page.name || page.id}</span>
              <small>{page.endpoint || "screen"}</small>
            </button>
          ))}
        </nav>
      </aside>

      <main className="workspace">
        <section className="phone-stage">
          <div className="phone-frame" data-page-id={activePage.id}>
            <div className="phone-status">
              <span>9:41</span>
              <strong>{activePage.name}</strong>
              <span>5G</span>
            </div>
            <Screen
              page={activePage}
              formState={formState}
              setFormState={setFormState}
              handleAction={handleAction}
              showToast={showToast}
            />
          </div>

          <aside className="audit-panel">
            <p className="eyebrow">{labels.visualParity || "Visual parity"}</p>
            <h2>{activePage.name}</h2>
            <p>
              React 页面应按批准的 AI 原型图复刻布局、层级、配色、按钮和状态；右侧图片只作为复刻参考，不是主界面实现。
            </p>
            {activePage.referenceImage ? (
              <img src={activePage.referenceImage} alt={`${activePage.name} reference`} />
            ) : (
              <p className="missing-reference">{labels.reference || "Reference"} missing</p>
            )}
          </aside>
        </section>
      </main>

      {dialog ? (
        <div className="dialog-backdrop" role="presentation" onClick={() => setDialog(null)}>
          <div className="dialog" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
            <h3>{dialog.title}</h3>
            <p>{dialog.body}</p>
            <button type="button" className="primary" onClick={() => setDialog(null)}>
              {labels.close || "Close"}
            </button>
          </div>
        </div>
      ) : null}

      <div className={`toast ${toast ? "show" : ""}`} role="status">
        {toast}
      </div>
    </div>
  );
}

function Screen({ page, formState, setFormState, handleAction, showToast }) {
  return (
    <section className="screen">
      <header className="screen-header">
        <button type="button" aria-label="Back" onClick={() => window.history.back()}>
          ←
        </button>
        <div>
          <p>{page.endpoint || "mobile"}</p>
          <h2>{page.headline || page.name}</h2>
        </div>
        <button type="button" aria-label="More" onClick={() => showToast(page.status || "")}>
          ···
        </button>
      </header>

      <div className="hero-card">
        <p className="eyebrow">{page.status || labels.approved || "Approved"}</p>
        <h3>{page.headline || page.name}</h3>
        <p>{page.purpose}</p>
      </div>

      {page.controls?.length ? (
        <div className="panel">
          <h3>{labels.controls || "Controls"}</h3>
          {page.controls.map((control) => (
            <Control
              key={control.id || control.label}
              page={page}
              control={control}
              formState={formState}
              setFormState={setFormState}
              showToast={showToast}
            />
          ))}
        </div>
      ) : null}

      {page.sections?.map((section) => (
        <div className="panel" key={section.title}>
          <h3>{section.title}</h3>
          {section.body ? <p>{section.body}</p> : null}
          <div className="item-list">
            {(section.items || []).map((item, index) => (
              <article className="item-row" key={`${section.title}-${index}`}>
                <div>
                  <strong>{item.title || item}</strong>
                  {item.description ? <p>{item.description}</p> : null}
                </div>
                {item.action ? (
                  <button type="button" onClick={() => handleAction(item.action)}>
                    {item.action.label || "→"}
                  </button>
                ) : null}
              </article>
            ))}
          </div>
        </div>
      ))}

      {page.states?.length ? (
        <div className="panel">
          <h3>{labels.states || "States"}</h3>
          <div className="state-grid">
            {page.states.map((state) => (
              <button
                type="button"
                key={state.name || state.state}
                onClick={() => handleAction({ label: state.name || state.state, dialog: state.description })}
              >
                {state.name || state.state}
              </button>
            ))}
          </div>
        </div>
      ) : null}

      <footer className="screen-actions">
        {(page.actions?.length ? page.actions : [{ label: labels.saved || "Save", toast: labels.saved || "Saved" }]).map(
          (action) => (
            <button
              type="button"
              className={action.variant === "secondary" ? "secondary" : "primary"}
              key={action.label}
              onClick={() => handleAction(action)}
            >
              {action.label}
            </button>
          ),
        )}
      </footer>
    </section>
  );
}

function Control({ page, control, formState, setFormState, showToast }) {
  const key = `${page.id}:${control.id || control.label}`;
  const value = formState[key] ?? control.value ?? "";
  const setValue = (next) => setFormState((current) => ({ ...current, [key]: next }));

  if (control.type === "select") {
    return (
      <label className="control">
        <span>{control.label}</span>
        <select value={value} onChange={(event) => setValue(event.target.value)}>
          {(control.options || []).map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>
    );
  }

  if (control.type === "toggle" || control.type === "checkbox") {
    return (
      <label className="toggle-row">
        <span>{control.label}</span>
        <input
          type="checkbox"
          checked={Boolean(value)}
          onChange={(event) => {
            setValue(event.target.checked);
            showToast(labels.saved || "Saved");
          }}
        />
      </label>
    );
  }

  return (
    <label className="control">
      <span>{control.label}</span>
      <input
        type={control.type || "text"}
        placeholder={control.placeholder || ""}
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onBlur={() => showToast(labels.saved || "Saved")}
      />
    </label>
  );
}

createRoot(document.getElementById("root")).render(<App />);
