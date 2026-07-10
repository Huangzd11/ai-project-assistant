import { useCallback, useEffect, useRef, useState } from "react";
import { checkHealth, sendAgentMessageStream, uploadPdf } from "./api";

function loadSessionId() {
  let id = localStorage.getItem("agent_session_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("agent_session_id", id);
  }
  return id;
}

function MetaBlock({ workflow, plan, toolCalls, sources, usage }) {
  if (
    !workflow &&
    !plan?.length &&
    !toolCalls?.length &&
    !sources?.length &&
    !usage
  ) {
    return null;
  }

  return (
    <div className="meta-block">
      {usage && (
        <div className="meta-section">
          <div className="meta-title">本次请求</div>
          <div className="usage-line">
            Input {usage.prompt_tokens} · Output {usage.completion_tokens} · Cost $
            {Number(usage.cost_usd).toFixed(4)}
          </div>
        </div>
      )}

      {workflow && (
        <div className="meta-section">
          <div className="meta-title">工作流</div>
          <div className="meta-row">
            <span className="chip intent">{workflow.intent}</span>
            <span className="chip">{workflow.need_tool ? "已调用工具" : "直答"}</span>
          </div>
          <div className="meta-hint">{workflow.route}</div>
          <div className="meta-hint">{workflow.reason}</div>
        </div>
      )}

      {plan?.length > 0 && (
        <div className="meta-section">
          <div className="meta-title">工具计划</div>
          {plan.map((step, i) => (
            <div key={i} className="plan-item">
              <span className="chip tool">{step.tool}</span>
              <span className="meta-hint">{step.reason}</span>
              {Object.keys(step.args || {}).length > 0 && (
                <pre className="args-json">{JSON.stringify(step.args, null, 2)}</pre>
              )}
            </div>
          ))}
        </div>
      )}

      {toolCalls?.length > 0 && (
        <div className="meta-section">
          <div className="meta-title">工具调用</div>
          <div className="meta-row">
            {toolCalls.map((tc, i) => (
              <span key={i} className="chip tool">
                {tc.tool}
              </span>
            ))}
          </div>
        </div>
      )}

      {sources?.length > 0 && (
        <div className="meta-section">
          <div className="meta-title">引用来源</div>
          <ul className="sources-list">
            {sources.map((s, i) => (
              <li key={i}>
                {s.url ? (
                  <a href={s.url} target="_blank" rel="noreferrer">
                    {s.source}
                  </a>
                ) : (
                  s.source
                )}
                {s.page != null && s.page > 0 && <> · Page {s.page}</>}
                {s.chunk != null && s.chunk > 0 && <> · chunk {s.chunk}</>}
                {s.score != null && (
                  <span className="score">（{s.score?.toFixed?.(2) ?? s.score}）</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [sessionId] = useState(loadSessionId);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [backend, setBackend] = useState(null);
  const [error, setError] = useState("");
  const listRef = useRef(null);

  useEffect(() => {
    checkHealth()
      .then((data) => setBackend(data))
      .catch(() => setBackend(null));
  }, []);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;

    setError("");
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    const assistantIdx = { current: -1 };
    setMessages((prev) => {
      assistantIdx.current = prev.length;
      return [
        ...prev,
        {
          role: "assistant",
          content: "",
          workflow: null,
          plan: [],
          toolCalls: [],
          sources: [],
          usage: null,
          streaming: true,
        },
      ];
    });

    try {
      await sendAgentMessageStream(text, sessionId, (event) => {
        if (event.type === "workflow") {
          setMessages((prev) => {
            const next = [...prev];
            const msg = next[assistantIdx.current];
            if (msg) msg.workflow = event.workflow;
            return next;
          });
        } else if (event.type === "plan") {
          setMessages((prev) => {
            const next = [...prev];
            const msg = next[assistantIdx.current];
            if (msg) msg.plan = event.plan;
            return next;
          });
        } else if (event.type === "tool_calls") {
          setMessages((prev) => {
            const next = [...prev];
            const msg = next[assistantIdx.current];
            if (msg) msg.toolCalls = event.tool_calls;
            return next;
          });
        } else if (event.type === "token") {
          setMessages((prev) => {
            const next = [...prev];
            const msg = next[assistantIdx.current];
            if (msg) msg.content += event.content;
            return next;
          });
        } else if (event.type === "usage") {
          setMessages((prev) => {
            const next = [...prev];
            const msg = next[assistantIdx.current];
            if (msg) msg.usage = event.usage;
            return next;
          });
        } else if (event.type === "done") {
          setMessages((prev) => {
            const next = [...prev];
            const msg = next[assistantIdx.current];
            if (msg) {
              msg.content = event.answer;
              msg.workflow = event.workflow;
              msg.plan = event.plan;
              msg.toolCalls = event.tool_calls;
              msg.sources = event.sources;
              if (event.usage) msg.usage = event.usage;
              msg.streaming = false;
            }
            return next;
          });
        } else if (event.type === "error") {
          throw new Error(event.detail || "流式请求失败");
        }
      });
    } catch (e) {
      setError(e.message);
      setMessages((prev) => {
        const next = [...prev];
        const msg = next[assistantIdx.current];
        if (msg?.streaming) {
          next[assistantIdx.current] = {
            role: "assistant",
            content: `出错了：${e.message}`,
            isError: true,
          };
        } else {
          next.push({ role: "assistant", content: `出错了：${e.message}`, isError: true });
        }
        return next;
      });
    } finally {
      setLoading(false);
    }
  }, [input, loading, sessionId]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      const data = await uploadPdf(file);
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: `已上传 PDF：${data.filename}（${data.size}）。请执行入库脚本后再提问总结。`,
        },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleNewSession = () => {
    const id = crypto.randomUUID();
    localStorage.setItem("agent_session_id", id);
    window.location.reload();
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>AI Project Assistant</h1>
          <p className="subtitle">企业 Agent · 聊天 · 上传 · 引用来源 · 工具状态</p>
        </div>
        <div className="header-status">
          {backend ? (
            <span className="status ok">后端 {backend.version}</span>
          ) : (
            <span className="status err">后端未连接</span>
          )}
          <button type="button" className="btn-ghost" onClick={handleNewSession}>
            新会话
          </button>
        </div>
      </header>

      <aside className="sidebar">
        <h2>上传文档</h2>
        <p className="hint">支持 PDF，保存至知识库 uploads/</p>
        <label className={`upload-btn ${uploading ? "disabled" : ""}`}>
          {uploading ? "上传中…" : "选择 PDF 文件"}
          <input
            type="file"
            accept="application/pdf,.pdf"
            disabled={uploading}
            onChange={handleUpload}
            hidden
          />
        </label>
        <p className="hint small">上传后需运行入库脚本，Agent 才能 RAG 总结该文档。</p>
        <p className="hint small">会话 ID：{sessionId.slice(0, 8)}…</p>
      </aside>

      <main className="chat">
        <div className="messages" ref={listRef}>
          {messages.length === 0 && (
            <div className="empty">
              <p>试试：</p>
              <ul>
                <li>帮我总结 test.pdf</li>
                <li>北京今天天气怎么样</li>
                <li>今天有什么新闻</li>
                <li>足球比赛比分</li>
                <li>README 里面写了什么（需 MCP_ENABLED=true）</li>
                <li>计算 1+2</li>
              </ul>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`bubble-wrap ${msg.role}`}>
              <div className={`bubble ${msg.isError ? "error" : ""}`}>
                <div className="bubble-label">
                  {msg.role === "user" ? "你" : msg.role === "system" ? "系统" : "助手"}
                </div>
                <div className="bubble-content">
                  {msg.content}
                  {msg.streaming && <span className="cursor-blink">▍</span>}
                </div>
                {msg.role === "assistant" && !msg.isError && !msg.streaming && (
                  <MetaBlock
                    workflow={msg.workflow}
                    plan={msg.plan}
                    toolCalls={msg.toolCalls}
                    sources={msg.sources}
                    usage={msg.usage}
                  />
                )}
              </div>
            </div>
          ))}
          {loading && messages[messages.length - 1]?.role !== "assistant" && (
            <div className="bubble-wrap assistant">
              <div className="bubble loading-bubble">
                <div className="bubble-label">助手</div>
                <div className="bubble-content">思考中…</div>
              </div>
            </div>
          )}
        </div>

        {error && <div className="error-bar">{error}</div>}

        <div className="composer">
          <textarea
            rows={2}
            placeholder="输入问题，Enter 发送，Shift+Enter 换行"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button type="button" className="btn-send" onClick={handleSend} disabled={loading || !input.trim()}>
            发送
          </button>
        </div>
      </main>
    </div>
  );
}
