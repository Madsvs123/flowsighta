import { FormEvent, useState } from "react";
import { useList, useMutate } from "../../hooks/useApi";
import { dt } from "../../lib/format";

type Comment = { id: string; body: string; author_name: string; created_at: string };

export function CommentThread({ model, objectId }: { model: string; objectId?: string }) {
  const { data } = useList<Comment>("/comments/", { model, object: objectId }, Boolean(objectId));
  const post = useMutate("post", "/comments/", ["/comments/"]);
  const [body, setBody] = useState("");

  function submit(e: FormEvent) {
    e.preventDefault();
    if (!body.trim() && !objectId) return;
    post.mutate({ model, object_id: objectId });
    setBody("");
  }

  return (
    <div>
      <ol className="space-y-3">
        {(data?.results || []).map((c) => (
          <li key={c.id} className="text-sm">
            <p>{c.body}</p>
            <p className="text-xs text-[var(--text-muted)]">{c.author_name} · {dt(c.created_at)}</p>
          </li>
        ))}
      </ol>
      <form onSubmit={submit} className="mt-3 flex gap-2">
        <input className="input" placeholder="Add an internal comment" value={body} onChange={(e) => setBody(e.target.value)} />
        <button className="btn btn-primary" type="button">Send</button>
      </form>
    </div>
  );
}
