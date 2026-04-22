import { useState, useEffect, useRef, useCallback } from "react";
import { DotLottieReact } from "@lottiefiles/dotlottie-react";

const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { overflow: hidden; background: #020617; }
  ::-webkit-scrollbar { width: 3px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(0,210,255,0.2); border-radius: 99px; }

  @keyframes fadeUp {
    from { opacity:0; transform:translateY(12px); }
    to   { opacity:1; transform:translateY(0); }
  }
  @keyframes fadeIn  { from{opacity:0} to{opacity:1} }
  @keyframes blink   { 0%,100%{opacity:1} 50%{opacity:0.15} }
  @keyframes spin    { to{transform:rotate(360deg)} }
  @keyframes gradShift {
    0%,100%{background-position:0% 50%}
    50%{background-position:100% 50%}
  }
  @keyframes glow { 0%,100%{opacity:1} 50%{opacity:0.4} }

  .hg-msg  { animation: fadeUp 0.38s cubic-bezier(0.22,1,0.36,1) both; }

  .hg-chip { transition: all 0.2s ease; cursor: pointer; }
  .hg-chip:hover {
    background: rgba(0,210,255,0.1) !important;
    border-color: rgba(0,210,255,0.5) !important;
    transform: translateY(-2px);
  }

  .hg-nav { transition: background 0.15s, color 0.15s; cursor: pointer; }
  .hg-nav:hover { background: rgba(0,210,255,0.09) !important; color: #00d2ff !important; }

  .hg-send { transition: transform 0.15s, box-shadow 0.15s; }
  .hg-send:hover:not(:disabled) { transform:scale(1.07); box-shadow:0 0 26px rgba(0,210,255,0.65) !important; }
  .hg-send:active:not(:disabled) { transform:scale(0.94); }

  .hg-textarea { resize:none; }
  .hg-textarea:focus { outline:none; }
  .hg-textarea::placeholder { color:rgba(148,163,184,0.38); }

  .hg-wrap { transition: border-color 0.2s, box-shadow 0.2s; }
  .hg-wrap:focus-within {
    border-color: rgba(0,210,255,0.5) !important;
    box-shadow: 0 0 0 1px rgba(0,210,255,0.12) !important;
  }

  .hg-dot {
    width:7px; height:7px; border-radius:50%;
    background:#00d2ff;
    animation: blink 1.1s ease-in-out infinite;
  }
  .hg-dot:nth-child(2){animation-delay:.22s}
  .hg-dot:nth-child(3){animation-delay:.44s}

  .hg-hist { transition:background 0.15s; cursor:pointer; }
  .hg-hist:hover { background:rgba(255,255,255,0.05) !important; }

  .hg-clr { transition:background 0.15s; }
  .hg-clr:hover { background:rgba(255,255,255,0.07) !important; }

  .hg-newchat { transition:opacity 0.15s, transform 0.15s; }
  .hg-newchat:hover { opacity:0.85; transform:translateY(-1px); }
`;

if (!document.getElementById("hg-chat-css")) {
  const el = document.createElement("style");
  el.id = "hg-chat-css";
  el.textContent = CSS;
  document.head.appendChild(el);
}

const ACCENT  = "#00d2ff";
const ACCENT2 = "#0055ff";
const BORDER  = "rgba(0,210,255,0.11)";
const GLASS_AI = "rgba(255,255,255,0.035)";
const GLASS_US = "rgba(0,75,255,0.13)";
const STORE    = "hg_chat_v3";

const WELCOME = {
  role:"ai", id:"welcome", time:"",
  text:"Hello! I'm **HealthGuard AI**, your personal medical intelligence assistant.\n\nI can help you understand symptoms, interpret lab reports, and answer health-related questions.\n\n*Please note: I provide information only — always consult a qualified physician for diagnosis and treatment.*",
};

const CHIPS = [
  "What are symptoms of Type 2 Diabetes?",
  "Explain my CBC blood test results",
  "Is my blood pressure reading normal?",
  "What does elevated creatinine indicate?",
];

const uid = () => Math.random().toString(36).slice(2,9);
const now = () => new Date().toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"});
const md  = t =>
  t.replace(/\*\*(.*?)\*\*/g,"<strong>$1</strong>")
   .replace(/\*(.*?)\*/g,"<em>$1</em>")
   .replace(/`(.*?)`/g,"<code style='background:rgba(0,210,255,0.12);padding:1px 6px;border-radius:4px;font-size:.87em'>$1</code>")
   .replace(/\n/g,"<br/>");

function LottieBG() {
  return (
    <div style={{
      position     :"fixed",
      inset        :0,
      zIndex       :0,
      pointerEvents:"none",
      overflow     :"hidden",
      background   :"transparent",
    }}>
      <DotLottieReact
        src="https://lottie.host/ce742026-b89b-4d25-bbaa-0bd9b724260e/pWiZzQBUSm.lottie"
        loop
        autoplay
        style={{
          width         :"100vw",
          height        :"100vh",
          opacity       :0.45,
          pointerEvents :"none",
          display       :"block",
          background    :"transparent",
        }}
      />
    </div>
  );
}

function Avatar() {
  return (
    <div style={{
      width:32, height:32, borderRadius:"50%", flexShrink:0,
      background:`linear-gradient(135deg,${ACCENT2},${ACCENT})`,
      display:"flex", alignItems:"center", justifyContent:"center",
      fontFamily:"Syne,sans-serif", fontWeight:800, fontSize:11,
      color:"#fff", boxShadow:`0 0 12px rgba(0,210,255,0.4)`,
      letterSpacing:"0.03em", userSelect:"none",
    }}>HG</div>
  );
}

function Bubble({ msg }) {
  const u = msg.role === "user";
  return (
    <div className="hg-msg" style={{
      display:"flex",
      flexDirection: u ? "row-reverse" : "row",
      alignItems:"flex-end", gap:9, marginBottom:14,
    }}>
      {!u && <Avatar />}
      <div style={{
        maxWidth:"70%", padding:"12px 17px",
        borderRadius: u ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
        background: u ? GLASS_US : GLASS_AI,
        border:`1px solid ${u ? "rgba(0,80,255,0.3)" : BORDER}`,
        backdropFilter:"blur(18px)", WebkitBackdropFilter:"blur(18px)",
        color:"#cbd5e1", fontFamily:"'DM Sans',sans-serif",
        fontSize:"0.9rem", lineHeight:1.7, wordBreak:"break-word",
        boxShadow: u ? "0 4px 20px rgba(0,80,255,0.1)" : "0 4px 20px rgba(0,0,0,0.28)",
        position:"relative",
      }}>
        <div style={{
          position:"absolute", top:0, left:18, right:18, height:1,
          background:`linear-gradient(90deg,transparent,${u?"rgba(0,100,255,0.4)":"rgba(0,210,255,0.18)"},transparent)`,
        }}/>
        <div dangerouslySetInnerHTML={{__html: md(msg.text)}} />
        {msg.time && (
          <div style={{fontSize:".66rem",color:"rgba(148,163,184,0.32)",marginTop:6,textAlign:u?"right":"left"}}>
            {msg.time}
          </div>
        )}
      </div>
    </div>
  );
}

function Typing() {
  return (
    <div style={{display:"flex",alignItems:"flex-end",gap:9,marginBottom:14}}>
      <Avatar/>
      <div style={{
        padding:"13px 18px", background:GLASS_AI,
        border:`1px solid ${BORDER}`,
        borderRadius:"18px 18px 18px 4px",
        backdropFilter:"blur(18px)",
        display:"flex", gap:5, alignItems:"center",
      }}>
        <div className="hg-dot"/>
        <div className="hg-dot"/>
        <div className="hg-dot"/>
      </div>
    </div>
  );
}

export default function Chat({ setPage }) {
  const [messages, setMessages] = useState(() => {
    try { const s = localStorage.getItem(STORE); return s ? JSON.parse(s) : [WELCOME]; }
    catch { return [WELCOME]; }
  });
  const [input,   setInput]   = useState("");
  const [loading, setLoading] = useState(false);
  const [sidebar, setSidebar] = useState(true);
  const [file,    setFile]    = useState(null);

  const bottomRef = useRef(null);
  const inputRef  = useRef(null);
  const fileRef   = useRef(null);

  useEffect(() => {
    try { localStorage.setItem(STORE, JSON.stringify(messages)); } catch {}
  }, [messages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior:"smooth" });
  }, [messages, loading]);

  useEffect(() => { inputRef.current?.focus(); }, []);

  const send = useCallback(async (text) => {
    const q = (text ?? input).trim();
    if ((!q && !file) || loading) return;

    const label = q
      ? (file ? `${q}\n\n📎 *${file.name}*` : q)
      : `📎 *${file.name}*`;

    setMessages(p => [...p, { role:"user", id:uid(), time:now(), text:label }]);
    setInput("");
    const attachedFile = file;
    setFile(null);
    setLoading(true);

    try {
      let res;
      if (attachedFile) {
        const form = new FormData();
        form.append("file", attachedFile);
        if (q) form.append("message", q);
        res = await fetch("http://localhost:8000/chat/upload", { method:"POST", body:form });
      } else {
        res = await fetch("http://localhost:8000/chat", {
          method:"POST",
          headers:{"Content-Type":"application/json"},
          body:JSON.stringify({ message:q }),
        });
      }
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const ans  = data.response ?? data.explanation ?? data.answer ?? JSON.stringify(data);
      setMessages(p => [...p, { role:"ai", id:uid(), time:now(), text:ans }]);
    } catch(err) {
      setMessages(p => [...p, {
        role:"ai", id:uid(), time:now(),
        text:`Unable to reach HealthGuard backend.\n\n*${err.message}*\n\nMake sure the API server is running at \`localhost:8000\`.`,
      }]);
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 60);
    }
  }, [input, file, loading]);

  const clear      = () => { setMessages([WELCOME]); localStorage.removeItem(STORE); };
  const onKey      = e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } };
  const onFilePick = e => { const f = e.target.files?.[0]; if (f) setFile(f); e.target.value = ""; };
  const removeFile = () => setFile(null);
  const recent     = messages.filter(m => m.role === "user");

  return (
    <>
      <LottieBG />
      <div style={{
        position :"relative",
        zIndex   :1,
        display  :"flex",
        height   :"100vh",
        width    :"100vw",
        overflow :"hidden",
        fontFamily:"'DM Sans',sans-serif",
      }}>
        <div style={{
          width     :sidebar ? 240 : 0,
          minWidth  :sidebar ? 240 : 0,
          transition:"width .28s cubic-bezier(.4,0,.2,1), min-width .28s",
          overflow  :"hidden",
          flexShrink:0,
          position  :"relative",
          zIndex    :20,
        }}>
          <div style={{
            width    :240,
            height   :"100vh",
            display  :"flex",
            flexDirection:"column",
            background:"rgba(2,6,23,0.96)",
            backdropFilter:"blur(28px)",
            WebkitBackdropFilter:"blur(28px)",
            borderRight:`1px solid ${BORDER}`,
          }}>
            <div style={{flex:1, overflowY:"auto", overflowX:"hidden", padding:"18px 14px 0"}}>
              <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:24}}>
                <div style={{
                  width:38, height:38, borderRadius:11, flexShrink:0,
                  background:`linear-gradient(135deg,${ACCENT2},${ACCENT})`,
                  display:"flex", alignItems:"center", justifyContent:"center",
                  fontFamily:"Syne,sans-serif", fontWeight:800, fontSize:13,
                  color:"#fff", boxShadow:`0 0 18px rgba(0,210,255,0.45)`,
                  userSelect:"none",
                }}>HG</div>
                <div>
                  <div style={{fontFamily:"Syne,sans-serif",fontWeight:700,fontSize:".9rem",color:"#f1f5f9",whiteSpace:"nowrap"}}>
                    HealthGuard
                  </div>
                  <div style={{fontSize:".61rem",color:ACCENT,letterSpacing:".1em",whiteSpace:"nowrap"}}>
                    AI ASSISTANT
                  </div>
                </div>
              </div>

              <button
                className="hg-newchat"
                onClick={clear}
                style={{
                  width:"100%", padding:"10px 14px", marginBottom:20,
                  background:`linear-gradient(135deg,rgba(0,75,255,0.18),rgba(0,210,255,0.18))`,
                  border:`1px solid rgba(0,210,255,0.25)`,
                  borderRadius:10, color:ACCENT,
                  fontFamily:"'DM Sans',sans-serif", fontSize:".84rem", fontWeight:500,
                  cursor:"pointer", display:"flex", alignItems:"center", gap:8,
                  whiteSpace:"nowrap",
                }}
              >
                <span style={{fontSize:18,lineHeight:1}}>＋</span>
                New Conversation
              </button>

              <div style={{fontSize:".6rem",color:"rgba(148,163,184,0.36)",letterSpacing:".13em",marginBottom:7,paddingLeft:2}}>
                NAVIGATION
              </div>

              <div style={{display:"flex",flexDirection:"column",gap:3,marginBottom:20}}>
                {[
                  { icon:"💬", label:"Chat", pg:"chat" },
                  { icon:"🏠", label:"Home", pg:"home" },
                ].map(({ icon, label, pg }) => (
                  <button
                    key={pg}
                    className="hg-nav"
                    onClick={() => setPage?.(pg)}
                    style={{
                      display:"flex", alignItems:"center", gap:9,
                      width:"100%", padding:"9px 12px",
                      background: pg === "chat" ? "rgba(0,210,255,0.09)" : "transparent",
                      border: pg === "chat" ? `1px solid rgba(0,210,255,0.2)` : "1px solid transparent",
                      borderRadius:9,
                      color: pg === "chat" ? ACCENT : "rgba(148,163,184,0.65)",
                      fontFamily:"'DM Sans',sans-serif", fontSize:".84rem",
                      textAlign:"left",
                    }}
                  >
                    <span style={{fontSize:15}}>{icon}</span>
                    {label}
                  </button>
                ))}
              </div>

              <div style={{height:1,background:BORDER,margin:"0 0 14px"}}/>

              <div style={{fontSize:".6rem",color:"rgba(148,163,184,0.36)",letterSpacing:".13em",marginBottom:7,paddingLeft:2}}>
                RECENT CHATS
              </div>

              {recent.length === 0 && (
                <div style={{fontSize:".76rem",color:"rgba(100,116,139,0.4)",paddingLeft:2}}>
                  No messages yet
                </div>
              )}
              {recent.slice(-6).reverse().map(m => (
                <div key={m.id} className="hg-hist" style={{
                  padding:"7px 10px", borderRadius:8,
                  color:"rgba(148,163,184,0.5)", fontSize:".76rem",
                  whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis",
                  marginBottom:2, background:"transparent",
                }}>
                  {m.text.length > 32 ? m.text.slice(0,32)+"…" : m.text}
                </div>
              ))}
            </div>

            <div style={{padding:"12px 14px",borderTop:`1px solid ${BORDER}`,flexShrink:0}}>
              <div style={{
                display:"flex", alignItems:"center", gap:9,
                padding:"8px 10px", borderRadius:9,
                background:"rgba(255,255,255,0.025)",
              }}>
                <div style={{
                  width:28, height:28, borderRadius:"50%",
                  background:"rgba(0,80,255,0.25)",
                  border:`1px solid rgba(0,210,255,0.25)`,
                  display:"flex", alignItems:"center", justifyContent:"center",
                  fontSize:13,
                }}>👤</div>
                <div>
                  <div style={{fontSize:".78rem",color:"#e2e8f0"}}>Patient Portal</div>
                  <div style={{fontSize:".64rem",color:"rgba(148,163,184,0.4)"}}>Secure Session</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <main style={{
          flex:1, display:"flex", flexDirection:"column",
          height:"100vh", overflow:"hidden",
          position:"relative", zIndex:1,
          background:"rgba(2,6,23,0.55)",
        }}>
          <header style={{
            display:"flex", alignItems:"center", justifyContent:"space-between",
            padding:"0 20px", height:56, flexShrink:0,
            borderBottom:`1px solid ${BORDER}`,
            background:"rgba(2,6,23,0.85)",
            backdropFilter:"blur(24px)", WebkitBackdropFilter:"blur(24px)",
            position:"relative", zIndex:5,
          }}>
            <div style={{display:"flex",alignItems:"center",gap:12}}>
              <button
                onClick={() => setSidebar(s => !s)}
                style={{
                  background:"none", border:"none", cursor:"pointer",
                  color:"rgba(148,163,184,0.6)", fontSize:21,
                  display:"flex", alignItems:"center", padding:"4px 6px",
                  borderRadius:7, lineHeight:1,
                }}
              >☰</button>
              <div style={{display:"flex",alignItems:"center",gap:8}}>
                <div style={{
                  width:7, height:7, borderRadius:"50%",
                  background:"#22c55e", boxShadow:"0 0 7px #22c55e",
                  animation:"glow 2s ease-in-out infinite",
                }}/>
                <span style={{fontFamily:"Syne,sans-serif",fontWeight:700,fontSize:".92rem",color:"#e2e8f0"}}>
                  HealthGuard AI
                </span>
                <span style={{
                  fontSize:".61rem", padding:"2px 8px", borderRadius:99,
                  background:"rgba(0,210,255,0.09)",
                  border:`1px solid rgba(0,210,255,0.22)`,
                  color:ACCENT, letterSpacing:".07em",
                }}>ONLINE</span>
              </div>
            </div>
            <button
              className="hg-clr"
              onClick={clear}
              style={{
                background:"rgba(255,255,255,0.03)",
                border:`1px solid ${BORDER}`,
                color:"rgba(148,163,184,0.6)",
                borderRadius:8, padding:"5px 14px",
                cursor:"pointer", fontSize:".78rem",
                fontFamily:"'DM Sans',sans-serif",
                display:"flex", alignItems:"center", gap:6,
              }}
            >🗑 Clear</button>
          </header>

          <div style={{
            flex:1, overflowY:"auto", padding:"26px 0",
            position:"relative", zIndex:2,
          }}>
            <div style={{maxWidth:740,width:"100%",margin:"0 auto",padding:"0 18px"}}>
              {messages.length === 1 && (
                <div style={{marginBottom:28,animation:"fadeIn .5s both"}}>
                  <div style={{textAlign:"center",marginBottom:22}}>
                    <div style={{
                      fontFamily:"Syne,sans-serif", fontWeight:800,
                      fontSize:"clamp(1.5rem,3vw,2rem)", marginBottom:8,
                      background:`linear-gradient(90deg,#fff,${ACCENT},${ACCENT2})`,
                      backgroundSize:"200% auto",
                      WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent",
                      animation:"gradShift 3.5s linear infinite",
                    }}>
                      How can I help you today?
                    </div>
                    <div style={{color:"rgba(148,163,184,0.55)",fontSize:".88rem"}}>
                      Ask about symptoms, lab tests, medications, or anything health-related.
                    </div>
                  </div>
                  <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
                    {CHIPS.map((c,i) => (
                      <button key={i} className="hg-chip" onClick={() => send(c)} style={{
                        background:GLASS_AI, border:`1px solid ${BORDER}`,
                        borderRadius:13, padding:"13px 16px",
                        color:"rgba(203,213,225,0.8)", textAlign:"left",
                        fontSize:".82rem", fontFamily:"'DM Sans',sans-serif",
                        lineHeight:1.5, backdropFilter:"blur(12px)",
                      }}>
                        {c}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map(m => <Bubble key={m.id} msg={m} />)}
              {loading && <Typing />}
              <div ref={bottomRef} />
            </div>
          </div>

          <div style={{
            padding:"12px 18px 18px",
            background:"rgba(2,6,23,0.9)",
            backdropFilter:"blur(24px)", WebkitBackdropFilter:"blur(24px)",
            borderTop:`1px solid ${BORDER}`,
            flexShrink:0, position:"relative", zIndex:5,
          }}>
            {file && (
              <div style={{
                maxWidth:740, margin:"0 auto 8px",
                display:"flex", alignItems:"center", gap:8,
              }}>
                <div style={{
                  display:"inline-flex", alignItems:"center", gap:8,
                  background:"rgba(0,210,255,0.08)",
                  border:`1px solid rgba(0,210,255,0.25)`,
                  borderRadius:99, padding:"5px 12px 5px 10px",
                  animation:"fadeIn .2s both",
                }}>
                  <span style={{fontSize:15}}>
                    {/\.(pdf)$/i.test(file.name) ? "📄"
                      : /\.(png|jpg|jpeg|webp|gif)$/i.test(file.name) ? "🖼️"
                      : /\.(docx?|txt)$/i.test(file.name) ? "📝"
                      : "📎"}
                  </span>
                  <span style={{
                    fontSize:".78rem", color:"rgba(203,213,225,0.9)",
                    fontFamily:"'DM Sans',sans-serif",
                    maxWidth:260, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap",
                  }}>
                    {file.name}
                  </span>
                  <span style={{fontSize:".7rem",color:"rgba(148,163,184,0.5)"}}>
                    ({(file.size/1024).toFixed(0)} KB)
                  </span>
                  <button
                    onClick={removeFile}
                    style={{
                      background:"none", border:"none", cursor:"pointer",
                      color:"rgba(148,163,184,0.55)", fontSize:14,
                      display:"flex", alignItems:"center",
                      padding:"0 2px", lineHeight:1,
                      transition:"color 0.15s",
                    }}
                    onMouseEnter={e=>e.currentTarget.style.color="rgba(255,100,100,0.8)"}
                    onMouseLeave={e=>e.currentTarget.style.color="rgba(148,163,184,0.55)"}
                    title="Remove file"
                  >✕</button>
                </div>
              </div>
            )}

            <div style={{maxWidth:740,margin:"0 auto",display:"flex",alignItems:"flex-end",gap:8}}>
              <input
                ref={fileRef}
                type="file"
                accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg,.webp,.csv,.xlsx"
                onChange={onFilePick}
                style={{display:"none"}}
              />

              <button
                onClick={() => fileRef.current?.click()}
                title="Attach document or report"
                style={{
                  width:46, height:46, borderRadius:13,
                  flexShrink:0, border:`1px solid ${file ? "rgba(0,210,255,0.45)" : BORDER}`,
                  background: file ? "rgba(0,210,255,0.1)" : "rgba(255,255,255,0.04)",
                  cursor:"pointer",
                  display:"flex", alignItems:"center", justifyContent:"center",
                  transition:"all 0.2s",
                  boxShadow: file ? "0 0 12px rgba(0,210,255,0.2)" : "none",
                }}
                onMouseEnter={e=>{
                  e.currentTarget.style.background="rgba(0,210,255,0.1)";
                  e.currentTarget.style.borderColor="rgba(0,210,255,0.45)";
                }}
                onMouseLeave={e=>{
                  if (!file) {
                    e.currentTarget.style.background="rgba(255,255,255,0.04)";
                    e.currentTarget.style.borderColor=BORDER;
                  }
                }}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66L9.41 17.41a2 2 0 01-2.83-2.83l8.49-8.48"
                    stroke={file ? ACCENT : "rgba(148,163,184,0.7)"}
                    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>

              <div className="hg-wrap" style={{
                flex:1,
                background:"rgba(255,255,255,0.04)",
                border:`1px solid rgba(0,210,255,0.16)`,
                borderRadius:14,
              }}>
                <textarea
                  ref={inputRef}
                  className="hg-textarea"
                  rows={1}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={onKey}
                  onInput={e => {
                    e.target.style.height = "auto";
                    e.target.style.height = Math.min(e.target.scrollHeight, 130) + "px";
                  }}
                  placeholder={file ? "Add a question about this file… (or press Enter to send)" : "Ask about symptoms, lab tests, medications…"}
                  style={{
                    width:"100%", background:"none", border:"none",
                    color:"#e2e8f0", fontSize:".9rem",
                    fontFamily:"'DM Sans',sans-serif", lineHeight:1.65,
                    padding:"13px 16px", maxHeight:130, overflowY:"auto",
                    display:"block",
                  }}
                />
              </div>

              <button
                className="hg-send"
                onClick={() => send()}
                disabled={(!input.trim() && !file) || loading}
                style={{
                  width:46, height:46, borderRadius:13,
                  flexShrink:0, border:"none",
                  background: ((!input.trim() && !file) || loading)
                    ? "rgba(255,255,255,0.05)"
                    : `linear-gradient(135deg,${ACCENT2},${ACCENT})`,
                  cursor: ((!input.trim() && !file) || loading) ? "not-allowed" : "pointer",
                  display:"flex", alignItems:"center", justifyContent:"center",
                  boxShadow: ((!input.trim() && !file) || loading)
                    ? "none"
                    : `0 0 16px rgba(0,210,255,0.38)`,
                }}
              >
                {loading
                  ? <div style={{
                      width:17, height:17,
                      border:"2px solid rgba(255,255,255,0.15)",
                      borderTopColor:ACCENT, borderRadius:"50%",
                      animation:"spin .75s linear infinite",
                    }}/>
                  : <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
                      <path d="M22 2L11 13" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                }
              </button>
            </div>

            <div style={{
              maxWidth:740, margin:"7px auto 0",
              textAlign:"center", fontSize:".65rem",
              color:"rgba(100,116,139,0.4)",
            }}>
              HealthGuard AI can make mistakes. Always consult a qualified medical professional.
            </div>
          </div>
        </main>
      </div>
    </>
  );
}