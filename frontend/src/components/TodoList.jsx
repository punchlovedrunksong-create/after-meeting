export default function TodoList({ todos }) {
  return (
    <section className="panel" aria-labelledby="todos-title">
      <p className="eyebrow">NEXT STEPS</p>
      <h2 id="todos-title">투두리스트</h2>
      {todos === undefined ? (
        <p className="placeholder">분석 결과의 후속 할 일이 여기에 표시됩니다.</p>
      ) : todos.length === 0 ? (
        <p className="empty-state">요약에서 확인된 후속 할 일이 없습니다.</p>
      ) : (
        <div className="todo-list">
          {todos.map((todo, index) => (
            <article className="todo-item" key={`${todo.task}-${index}`}>
              <h3>{todo.task}</h3>
              <dl>
                {todo.assignee && <><dt>담당자</dt><dd>{todo.assignee}</dd></>}
                {todo.due_date && <><dt>기한</dt><dd>{todo.due_date}</dd></>}
                {todo.priority && <><dt>우선순위</dt><dd>{todo.priority}</dd></>}
              </dl>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
